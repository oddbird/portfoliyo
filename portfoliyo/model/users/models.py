"""
Portfoliyo network models.

"""
import base64
import time
from hashlib import sha1
from django.contrib.auth import models as auth_models
from django.db import models, transaction, IntegrityError
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.utils import timezone

from model_utils import Choices


# monkeypatch Django's User.email to be sufficiently long and unique/nullable
email_field = auth_models.User._meta.get_field("email")
email_field._unique = True
email_field.null = True
email_field.max_length = 255

# monkeypatch User's __unicode__ method to be friendlier for no-username
auth_models.User.__unicode__ = lambda self: (
    self.email or self.profile.name or self.profile.phone or u'<unknown>')


class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        value = None
        try:
            value = super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            pass
        if value is None:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            setattr(instance, self.cache_name, obj)
            value = obj
        return value


class AutoOneToOneField(models.OneToOneField):
    """OneToOneField that creates related obj on first access if needed."""
    def contribute_to_related_class(self, cls, related):
        setattr(
            cls,
            related.get_accessor_name(),
            AutoSingleRelatedObjectDescriptor(related),
            )


from south.modelsinspector import add_introspection_rules
add_introspection_rules(
    [], ["^portfoliyo\.model\.users\.models\.AutoOneToOneField"])


class Profile(models.Model):
    """A Portfoliyo user profile."""
    user = AutoOneToOneField(auth_models.User)
    # fields from User we use: username, password, email
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    # e.g. "Math Teacher", "Father", "Principal", etc
    # serves as default fall-back for the relationship-description field
    role = models.CharField(max_length=200)
    school_staff = models.BooleanField(default=False)
    # code for parent-initiated signups
    code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    # signup status (for text-based multi-step signup); what are we awaiting?
    STATE = Choices('kidname', 'relationship', 'done')
    state = models.CharField(max_length=20, choices=STATE, default=STATE.done)
    # who invited this user to the site?
    invited_by = models.ForeignKey('self', blank=True, null=True)
    deleted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name or self.phone or self.user.email or u'<unknown>'


    def save(self, *a, **kw):
        """Make site staff always school staff, too."""
        if self.user.is_staff:
            self.school_staff = True
        return super(Profile, self).save(*a, **kw)


    @classmethod
    def create_with_user(cls, name='', email=None, phone=None, password=None,
                         role='', school_staff=False, is_active=False,
                         state=None, invited_by=None):
        """
        Create a Profile and associated User and return the new Profile.

        Generates a unique username to satisfy the User model by hashing as
        much user data as we're given, plus a timestamp.

        """
        to_hash = u"-".join(
            [email or u'', phone or u'', name, u'%f' % time.time()])
        username = base64.b64encode(sha1(to_hash.encode('utf-8')).digest())
        now = timezone.now()
        user = auth_models.User(
            username=username,
            email=email,
            is_staff=False,
            is_active=is_active,
            is_superuser=False,
            date_joined=now,
            )
        user.set_password(password)
        user.save()
        code = generate_code(username, 6) if school_staff else None
        profile = cls(
            name=name,
            phone=phone,
            user=user,
            role=role,
            school_staff=school_staff,
            state=state or cls.STATE.done,
            invited_by=invited_by,
            code=code,
            )

        # try a few times to generate a unique code, if we keep failing (quite
        # unlikely until we have many many users) give up and set code to None
        for i in range(5):
            try:
                sid = transaction.savepoint()
                profile.save()
                break
            except IntegrityError:
                if code is not None:
                    transaction.savepoint_rollback(sid)
                    profile.code = generate_code(u'%s%s' % (username, i), 6)
                else:
                    raise
        else:
            profile.code = None
            profile.save()

        return profile


    @property
    def elder_relationships(self):
        return self.relationships_to.filter(
            kind=Relationship.KIND.elder, from_profile__deleted=False).order_by(
            'description').select_related("from_profile")


    @property
    def elders(self):
        return [rel.from_profile for rel in self.elder_relationships]


    @property
    def student_relationships(self):
        return self.relationships_from.filter(
            kind=Relationship.KIND.elder, to_profile__deleted=False).order_by(
            'to_profile__name').select_related("to_profile")


    @property
    def students(self):
        return [rel.to_profile for rel in self.student_relationships]



class Relationship(models.Model):
    """A relationship between two Portfoliyo users."""
    KIND = Choices("elder")

    from_profile = models.ForeignKey(
        Profile, related_name="relationships_from")
    to_profile = models.ForeignKey(
        Profile, related_name="relationships_to")
    kind = models.CharField(max_length=20, choices=KIND, default=KIND.elder)
    description = models.CharField(max_length=200, blank=True)


    def __unicode__(self):
        return u"%s is %s%s to %s" % (
            self.from_profile,
            self.kind,
            ((u" (%s)" % self.description_or_role)
             if self.description_or_role else u""),
            self.to_profile,
            )


    class Meta:
        unique_together = [("from_profile", "to_profile", "kind")]


    @property
    def description_or_role(self):
        """If the description is empty, fall back to from_profile role."""
        return self.description or self.from_profile.role


    # Add a couple clearer aliases for working with elder relationships
    @property
    def elder(self):
        return self.from_profile


    @property
    def student(self):
        return self.to_profile



class Group(models.Model):
    """A group of students, set up by a particular teacher."""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(Profile, related_name='owned_groups')
    students = models.ManyToManyField(
        Profile, related_name='student_in_groups', blank=True)
    elders = models.ManyToManyField(
        Profile, related_name='elder_in_groups', blank=True)


    def __unicode__(self):
        return self.name


    class Meta:
        unique_together = [('name', 'owner')]



# 1 and 0 already eliminated by base32 encoding
AMBIGUOUS = ['L', 'I', 'O', 'S', '5']


def generate_code(seed, length):
    """Generate a probably-unique length-letter code given a unique seed."""
    full = base64.b32encode(sha1(seed).digest())
    for char in AMBIGUOUS:
        full = full.replace(char, '')
    return full[:length]
