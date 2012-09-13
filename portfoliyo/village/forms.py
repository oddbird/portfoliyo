"""
Student/elder forms.

"""
from base64 import b64encode
from hashlib import sha1
import time

from django.contrib.auth import models as auth_models
from django.forms import formsets
from django.utils import timezone

import floppyforms as forms

from ..users import formats, emails, models as user_models



class InviteElderForm(forms.Form):
    """A form for inviting an elder to a student village."""
    contact = forms.CharField(max_length=255)
    relationship = forms.CharField(max_length=200)
    school_staff = forms.BooleanField(required=False)


    def clean_contact(self):
        contact = self.cleaned_data["contact"]
        as_phone = formats.normalize_phone(contact)
        as_email = formats.normalize_email(contact)
        if as_phone:
            self.cleaned_data["phone"] = as_phone
            self.cleaned_data["email"] = None
        elif as_email:
            self.cleaned_data["email"] = as_email
            self.cleaned_data["phone"] = None
        else:
            raise forms.ValidationError(
                "Please supply a valid email address or US mobile number.")


    def save(self, request, student):
        """Given request and student profile, save/return elder profile."""
        email = self.cleaned_data.get("email")
        phone = self.cleaned_data.get("phone")
        relationship = self.cleaned_data.get("relationship", u"")
        staff = self.cleaned_data.get("school_staff", False)

        # first check for an existing user match
        if email:
            dupe_query = {"user__email": email}
        else:
            dupe_query = {"phone": phone}
        try:
            profile = user_models.Profile.objects.get(**dupe_query)
        except user_models.Profile.DoesNotExist:
            username = b64encode(sha1(email or phone).digest())
            now = timezone.now()
            user = auth_models.User(
                username=username,
                email=email,
                is_staff=False,
                is_active=False,
                is_superuser=False,
                date_joined=now,
                )
            user.set_unusable_password()
            user.save()
            profile = user_models.Profile.objects.create(
                user=user, phone=phone, role=relationship)
            if email:
                emails.send_invite_email(
                    user,
                    email_template_name='registration/invite_elder_email.txt',
                    subject_template_name='registration/invite_elder_subject.txt',
                    use_https=request.is_secure(),
                    extra_context={
                        'inviter': request.user.profile,
                        'student': student,
                        'domain': request.get_host(),
                        },
                    )
        else:
            # update school_staff and role fields as needed
            if ((staff and not profile.school_staff) or
                    (relationship and not profile.role)):
                profile.school_staff = True
                if not profile.role:
                    profile.role = relationship
                profile.save()

        # create the student-elder relationship (unless it already exists)
        user_models.Relationship.objects.get_or_create(
            from_profile=profile,
            to_profile=student,
            kind=user_models.Relationship.KIND.elder,
            defaults={'description': relationship},
            )

        return profile


class InviteEldersBaseFormSet(formsets.BaseFormSet):
    """Base formset class for inviting elders."""
    def save(self, request, student):
        """Save all elder forms and return list of elders."""
        elders = []
        for form in self:
            if form.has_changed():
                elders.append(form.save(request, student))

        return elders



InviteEldersFormSet = formsets.formset_factory(
    form=InviteElderForm,
    formset=InviteEldersBaseFormSet,
    extra=1,
    )



class AddStudentForm(forms.Form):
    """A form for adding a new student."""
    name = forms.CharField(max_length=200)


    def save(self, added_by=None):
        """
        Save new student and return their Profile.

        Optionally accept the Profile of the current user and create a
        relationship between them and the student.

        """
        assert self.is_valid()
        name = self.cleaned_data["name"]

        # name may not be unique, and it's all the info we have on a student,
        # so append the time to seed a hash to generate a unique username
        username = b64encode(sha1("%s%f" % (name, time.time())).digest())
        now = timezone.now()
        user = auth_models.User(
            username=username,
            is_staff=False,
            is_active=False,
            is_superuser=False,
            date_joined=now,
            )
        user.set_unusable_password()
        user.save()
        profile = user_models.Profile.objects.create(name=name, user=user)

        if added_by:
            user_models.Relationship.objects.create(
                from_profile=added_by,
                to_profile=profile,
                kind=user_models.Relationship.KIND.elder,
                )

        return profile



class AddStudentAndInviteEldersForm(AddStudentForm):
    """Form to add a student and invite any number of elders for them."""
    def __init__(self, *args, **kwargs):
        """Initialize AddStudentForm, including InviteEldersFormSet."""
        super(AddStudentAndInviteEldersForm, self).__init__(*args, **kwargs)

        self.elders_formset = InviteEldersFormSet(
            data=self.data or None, prefix='elders')


    def is_valid(self):
        """The student form and the elders formset must both be valid."""
        return self.elders_formset.is_valid() and super(
            AddStudentAndInviteEldersForm, self).is_valid()


    def save(self, request, *a, **kw):
        """
        Save the student and any associated elders.

        Returns a tuple of (student-profile, list-of-elder-profiles).

        """
        student = super(AddStudentAndInviteEldersForm, self).save(*a, **kw)
        elders = self.elders_formset.save(request, student)

        return (student, elders)
