"""
Student/elder forms.

"""
from base64 import b64encode
from hashlib import sha1
import time

from django.contrib.auth import models as auth_models
from django.forms import formsets

import floppyforms as forms

from ..users import formats, models as user_models



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


    def save(self, student):
        """Given student profile, save the new elder, return their profile."""
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
            user = auth_models.User.objects.create_user(
                username=username, email=email)
            profile = user_models.Profile.objects.create(
                user=user, phone=phone, role=relationship)
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
    def _construct_form(self, i, **kwargs):
        """Set all fields optional for all forms."""
        form = super(InviteEldersBaseFormSet, self)._construct_form(
            i, **kwargs)
        for field in form.fields.values():
            field.required = False
            field.widget.is_required = False
        return form


    def _get_empty_form(self, **kwargs):
        """Set all fields optional for the empty form."""
        form = super(InviteEldersBaseFormSet, self)._get_empty_form(**kwargs)
        for field in form.fields.values():
            field.required = False
            field.widget.is_required = False
        return form
    empty_form = property(_get_empty_form)



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
        username = b64encode(sha1("%s%s" % (name, time.time())).digest())
        user = auth_models.User.objects.create_user(username=username)
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


    def save(self, *a, **kw):
        """
        Save the student and any associated elders.

        Returns a tuple of (student-profile, list-of-elder-profiles).

        """
        profile = super(AddStudentAndInviteEldersForm, self).save(*a, **kw)

        elders = []
        for form in self.elders_formset:
            if form.has_changed():
                elders.append(form.save(profile))

        return (profile, elders)
