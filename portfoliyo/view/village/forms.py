"""
Student/elder forms.

"""
import floppyforms as forms

from portfoliyo import model, invites, formats
from ..users.forms import EditProfileForm



class StudentCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """A CheckboxSelectMultiple widget with a custom template."""
    template_name = 'village/student_checkbox_select.html'



class ElderCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """A CheckboxSelectMultiple widget with a custom template."""
    template_name = 'village/elder_checkbox_select.html'



class EditElderForm(EditProfileForm):
    def save(self, rel):
        """Save this elder in context of given village relationship."""
        self.profile.name = self.cleaned_data['name']
        old_profile_role = self.profile.role
        old_relationship_role = rel.description_or_role
        new_role = self.cleaned_data['role']
        if old_profile_role == old_relationship_role:
            self.profile.role = new_role
            self.profile.relationships_from.filter(
                description=old_profile_role).update(
                description='')
        else:
            rel.description = new_role
            rel.save()
        self.profile.save()
        return self.profile



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
            active = False
        else:
            dupe_query = {"phone": phone}
            active = True
        try:
            profile = model.Profile.objects.get(**dupe_query)
        except model.Profile.DoesNotExist:
            profile = model.Profile.create_with_user(
                school=rel.student.school,
                email=email,
                phone=phone,
                role=relationship,
                is_active=active,
                )
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

        # create student's rel with invited elder (unless it already exists)
        new_rel, rel_created = model.Relationship.objects.get_or_create(
            from_profile=profile,
            to_profile=rel.student,
            kind=model.Relationship.KIND.elder,
            defaults={'description': relationship},
            )

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



class StudentForm(forms.ModelForm):
    """Form for editing a student."""
    class Meta:
        model = model.Profile
        fields = ['name']


class AddStudentForm(StudentForm):
    """Form for adding a student."""
    def save(self, user):
        """
        Save and return new student.

        Takes the Profile of the current user and creates a relationship
        between them and the new student.

        """
        assert self.is_valid()
        name = self.cleaned_data["name"]

        profile = model.Profile.create_with_user(
            school=user.school, name=name, invited_by=user)

        model.Relationship.objects.create(
            from_profile=user,
            to_profile=profile,
            kind=model.Relationship.KIND.elder,
            )

        return profile



class GroupForm(forms.ModelForm):
    """Form for editing Groups."""
    class Meta:
        model = model.Group
        fields = ['name', 'students', 'elders']
        widgets = {
            'students': StudentCheckboxSelectMultiple,
            'elders': ElderCheckboxSelectMultiple,
            }


    def __init__(self, *args, **kwargs):
        """Store owner, narrow student and elder choices appropriately."""
        instance = kwargs.get('instance', None)
        if instance:
            self.owner = instance.owner
        else:
            self.owner = kwargs.pop('owner')
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['students'].queryset = model.Profile.objects.filter(
            relationships_to__from_profile=self.owner, deleted=False)
        self.fields['elders'].queryset = model.Profile.objects.filter(
            school=self.owner.school, school_staff=True, deleted=False)



class AddGroupForm(GroupForm):
    def save(self):
        """Save group, attaching new group to owner."""
        group = super(AddGroupForm, self).save(commit=False)
        group.owner = self.owner
        group.save()
        self.save_m2m()
        return group
