"""
Portfoliyo network models.

"""
from django.contrib.auth import models as auth_models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor

from model_utils import Choices


# monkeypatch Django's User.email to be sufficiently long and unique/nullable
email_field = auth_models.User._meta.get_field("email")
email_field._unique = True
email_field.null = True
email_field.max_length = 255
# ensure empty strings never make it to the database.
email_field.get_prep_value = lambda value: value or None

# monkeypatch User's __unicode__ method to be friendlier for no-username
auth_models.User.__unicode__ = lambda self: self.email or self.profile.name


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


class Profile(models.Model):
    """A Portfoliyo user profile."""
    user = AutoOneToOneField(auth_models.User)
    # fields from User we use: username, password, email
    name = models.CharField(max_length=200)
    phone = PhoneNumberField(blank=True, null=True, unique=True)
    # e.g. "Math Teacher", "Father", "Principal", etc
    # serves as default fall-back for the relationship-description field
    role = models.CharField(max_length=200)
    school_staff = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name


    @property
    def elder_relationships(self):
        return self.relationships_to.filter(
            kind=Relationship.KIND.elder).select_related("from_profile")


    @property
    def elders(self):
        return [rel.from_profile for rel in self.elder_relationships]


    @property
    def student_relationships(self):
        return self.relationships_from.filter(
            kind=Relationship.KIND.elder).select_related("to_profile")


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
        """If the description is empty, fall back to profile role."""
        return self.description or self.from_profile.role


    # Add a couple clearer aliases for working with elder relationships
    @property
    def elder(self):
        return self.from_profile


    @property
    def student(self):
        return self.to_profile
