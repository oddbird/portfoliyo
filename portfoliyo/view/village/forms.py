"""
Student/elder forms.

"""
from django.forms import formsets

import floppyforms as forms

from portfoliyo import model, invites, formats
from ..users.forms import EditProfileForm



class EditElderForm(EditProfileForm):
    """At this point, editing an elder is same as editing a profile."""
    pass



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


    def save(self, request, rel):
        """
        Save/return new elder profile and send invites, or return existing.

        Takes request and relationship between inviting elder and student.

        """
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
            profile = model.Profile.objects.get(**dupe_query)
        except model.Profile.DoesNotExist:
            profile = model.Profile.create_with_user(
                email=email, phone=phone, role=relationship)
            created = True
        else:
            created = False
            # update school_staff and role fields as needed
            if ((staff and not profile.school_staff) or
                    (relationship and not profile.role)):
                profile.school_staff = True
                if not profile.role:
                    profile.role = relationship
                profile.save()

        # create student's rel with inviting elder (unless it already exists)
        new_rel, rel_created = model.Relationship.objects.get_or_create(
            from_profile=profile,
            to_profile=rel.student,
            kind=model.Relationship.KIND.elder,
            defaults={'description': relationship},
            )

        # get the relations

        # send invite notifications
        if created:
            if email:
                invites.send_invite_email(
                    profile.user,
                    email_template_name='registration/invite_elder_email.txt',
                    subject_template_name='registration/invite_elder_subject.txt',
                    use_https=request.is_secure(),
                    extra_context={
                        'inviter': rel.elder,
                        'student': rel.student,
                        'inviter_rel': rel,
                        'invitee_rel': new_rel,
                        'domain': request.get_host(),
                        },
                    )
            else:
                invites.send_invite_sms(
                    profile.user,
                    template_name='registration/invite_elder_sms.txt',
                    extra_context={
                        'inviter': rel.elder,
                        'student': rel.student,
                        'inviter_rel': rel,
                        'invitee_rel': new_rel,
                        },
                    )

        return profile


class InviteEldersBaseFormSet(formsets.BaseFormSet):
    """Base formset class for inviting elders."""
    def save(self, request, rel):
        """Save all elder forms and return list of elders."""
        elders = []
        for form in self:
            if form.has_changed():
                elders.append(form.save(request, rel))

        return elders



InviteEldersFormSet = formsets.formset_factory(
    form=InviteElderForm,
    formset=InviteEldersBaseFormSet,
    extra=1,
    )



class StudentForm(forms.Form):
    """Common student-form fields."""
    name = forms.CharField(max_length=200)



class EditStudentForm(StudentForm):
    """Form for editing a student."""
    def save(self, student):
        """Saves the edits to the given student."""
        student.name = self.cleaned_data['name']
        student.save()
        return student



class AddStudentForm(StudentForm):
    """A form for adding a new student."""
    def save(self, added_by):
        """
        Save new student and return (student-profile, rel-with-creating-elder).

        Takes the Profile of the current user and creates a relationship between
        them and the student.

        """
        assert self.is_valid()
        name = self.cleaned_data["name"]

        profile = model.Profile.create_with_user(name=name)

        rel = model.Relationship.objects.create(
            from_profile=added_by,
            to_profile=profile,
            kind=model.Relationship.KIND.elder,
            )

        return (profile, rel)



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
        student, rel = super(AddStudentAndInviteEldersForm, self).save(*a, **kw)
        elders = self.elders_formset.save(request, rel)

        return (student, elders)
