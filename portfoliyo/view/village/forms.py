"""
Student/elder forms.

"""
import floppyforms as forms

from portfoliyo import model, invites, formats
from portfoliyo.model import events
from .. import forms as pyoforms
from ..users.forms import EditProfileForm



class StudentCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/student_checkbox_select.html'



class ElderCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/elder_checkbox_select.html'



class GroupCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/group_checkbox_select.html'



class GroupIdsMultipleChoiceField(pyoforms.ModelMultipleChoiceField):
    # subclasses should override
    groups_attr = None


    def _set_queryset(self, queryset):
        """Prefetch the related groups."""
        self._queryset = queryset.prefetch_related(self.groups_attr)
        self.widget.choices = self.choices


    queryset = property(
        pyoforms.ModelMultipleChoiceField._get_queryset, _set_queryset)


    def label_from_instance(self, obj):
        """Annotate each object with list of group IDs."""
        obj.group_ids = [g.id for g in getattr(obj, self.groups_attr).all()]
        return obj



class StudentGroupIdsMultipleChoiceField(GroupIdsMultipleChoiceField):
    """Annotates each student with a list of group IDs."""
    groups_attr = 'student_in_groups'



class ElderGroupIdsMultipleChoiceField(GroupIdsMultipleChoiceField):
    """Annotates each student with a list of group IDs."""
    groups_attr = 'elder_in_groups'



class ElderFormBase(forms.Form):
    """Common elements of EditElderForm and InviteElderForm."""
    groups = pyoforms.ModelMultipleChoiceField(
        queryset=model.Group.objects.none(),
        widget=GroupCheckboxSelectMultiple,
        required=False,
        )
    students = StudentGroupIdsMultipleChoiceField(
        queryset=model.Profile.objects.none(),
        widget=StudentCheckboxSelectMultiple,
        required=False,
        )


    def __init__(self, *args, **kwargs):
        super(ElderFormBase, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = model.Group.objects.filter(
            owner=self.editor)
        self.fields['students'].queryset = model.Profile.objects.filter(
            relationships_to__from_profile=self.editor)
        self.fields['students'].groups_attr = 'student_in_groups'


    def update_elder_groups(self, elder, groups):
        """
        Update elder to be in only given groups of self.editor.

        Don't touch any memberships they may have in anyone else's groups.

        """
        current = set(elder.elder_in_groups.filter(owner=self.editor))
        target = set(groups)
        remove = current.difference(target)
        add = target.difference(current)

        if remove:
            elder.elder_in_groups.remove(*remove)
        if add:
            elder.elder_in_groups.add(*add)



class EditElderForm(ElderFormBase, EditProfileForm):
    def __init__(self, *args, **kwargs):
        self.editor = kwargs.pop('editor')
        super(EditElderForm, self).__init__(*args, **kwargs)
        self.fields['groups'].initial = [
            g.pk for g in self.instance.elder_in_groups.all()]
        self.fields['students'].initial = [
            s.pk for s in self.direct_students(self.instance)]


    def save(self, rel=None):
        """Save elder (optionally in context of given village relationship)."""
        self.instance.name = self.cleaned_data['name']
        old_profile_role = self.instance.role
        old_relationship_role = (
            rel.description_or_role if rel else self.instance.role)
        new_role = self.cleaned_data['role']
        if old_profile_role == old_relationship_role:
            self.instance.role = new_role
            self.instance.relationships_from.filter(
                description=old_profile_role).update(
                description='')
        else:
            rel.description = new_role
            rel.save()
        self.instance.save()

        check_for_orphans = self.update_elder_students(
            self.instance, self.cleaned_data['students'])
        self.update_elder_groups(self.instance, self.cleaned_data['groups'])
        if check_for_orphans:
            model.Relationship.objects.delete_orphans()

        return self.instance


    def update_elder_students(self, elder, students):
        """
        Update elder to have exactly given direct (non-group) students.

        Return boolean indicating whether it's necessary to check for orphan
        relationships.

        """
        current = set(self.direct_students(elder))
        target = set(students)
        remove = current.difference(target)
        add = target.difference(current)

        check_for_orphans = False

        if remove:
            model.Relationship.objects.filter(
                from_profile=elder,
                to_profile__in=remove,
                ).update(direct=False)
            check_for_orphans = True

        for student in add:
            rel, created = model.Relationship.objects.get_or_create(
                to_profile=student,
                from_profile=elder,
                )
            if not created and not rel.direct:
                rel.direct = True
                rel.save()

        return check_for_orphans


    def direct_students(self, elder):
        """
        Get all direct students of an elder.

        Memoized by elder id.

        """
        if not hasattr(self, '_direct_students'):
            self._direct_students = {}
        if self._direct_students.get(elder.pk) is None:
            self._direct_students[elder.pk] = [
                r.student for r in
                model.Relationship.objects.filter(
                    from_profile=elder,
                    direct=True,
                    ).select_related('to_profile')
                ]
        return self._direct_students[elder.pk]



class InviteElderForm(ElderFormBase):
    """A form for inviting an elder to a student village."""
    contact = forms.CharField(max_length=255)
    relationship = forms.CharField(max_length=200)


    def __init__(self, *args, **kwargs):
        """
        Accepts ``rel`` or ``group``.

        ``rel`` is relationship between inviting elder and student, if elder is
        being invited in student context.

        ``group`` is a group owned by inviting elder, if elder is being invited
        in group context.

        """
        self.rel = kwargs.pop('rel', None)
        self.group = kwargs.pop('group', None)
        self.editor = self.rel.elder if self.rel else self.group.owner
        super(InviteElderForm, self).__init__(*args, **kwargs)
        if self.rel:
            self.fields['students'].initial = [self.rel.to_profile_id]
        if self.group:
            self.fields['groups'].initial = [self.group.id]


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


    def save(self):
        """Save/return new elder profile & send invites, or return existing."""
        email = self.cleaned_data.get("email")
        phone = self.cleaned_data.get("phone")
        relationship = self.cleaned_data.get("relationship", u"")
        staff = (email is not None)

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
                school=self.editor.school,
                email=email,
                phone=phone,
                role=relationship,
                is_active=active,
                school_staff=staff,
                invited_by=self.editor,
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

        # send invite notifications
        if created:
            if email:
                invites.send_invite_email(
                    profile.user,
                    email_template_name='registration/invite_elder_email.txt',
                    subject_template_name='registration/invite_elder_subject.txt',
                    extra_context={
                        'inviter': self.editor,
                        'student': self.rel.student if self.rel else None,
                        'inviter_rel': self.rel,
                        },
                    )
            else:
                invites.send_invite_sms(
                    profile.user,
                    template_name='registration/invite_elder_sms.txt',
                    extra_context={
                        'inviter': self.editor,
                        'student': self.rel.student if self.rel else None,
                        'inviter_rel': self.rel,
                        },
                    )

        for student in self.cleaned_data['students']:
            rel, created = model.Relationship.objects.get_or_create(
                from_profile=profile,
                to_profile=student,
                defaults={
                    'description': relationship,
                    }
                )
            if not created and not rel.direct:
                rel.direct = True
                rel.save()
        self.update_elder_groups(profile, self.cleaned_data['groups'])

        return profile



class StudentForm(forms.ModelForm):
    """Form for editing a student."""
    groups = pyoforms.ModelMultipleChoiceField(
        queryset=model.Group.objects.none(),
        widget=GroupCheckboxSelectMultiple,
        required=False,
        )
    elders = ElderGroupIdsMultipleChoiceField(
        queryset=model.Profile.objects.none(),
        widget=ElderCheckboxSelectMultiple,
        required=False,
        )


    class Meta:
        model = model.Profile
        fields = ['name', 'groups', 'elders']
        widgets = {'name': forms.TextInput}


    def __init__(self, *args, **kwargs):
        """Store elder, set up group/elder choices and initial values."""
        self.elder = kwargs.pop('elder')
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = model.Group.objects.filter(
            owner=self.elder)
        self.fields['elders'].queryset = model.Profile.objects.filter(
            school=self.elder.school, school_staff=True).exclude(
            pk=self.elder.pk)
        self.fields['elders'].groups_attr = 'elder_in_groups'
        if self.instance.pk:
            self.fields['groups'].initial = [
                g.pk for g in self.instance.student_in_groups.all()]
            self.fields['elders'].initial = [
                e.pk for e in self.direct_other_teachers(self.instance)]


    def save(self):
        """Save and return student."""
        student = super(StudentForm, self).save()

        check_for_orphans = self.update_student_elders(
            student, self.cleaned_data['elders'])
        self.update_student_groups(student, self.cleaned_data['groups'])
        if check_for_orphans:
            model.Relationship.objects.delete_orphans()

        events.student_edited(student, *student.elders)

        return student


    def direct_other_teachers(self, student):
        """
        Get all direct (non-group) other-than-me teachers of a student.

        Memoized by student id.

        """
        if not hasattr(self, '_direct_other_teachers'):
            self._direct_other_teachers = {}
        if self._direct_other_teachers.get(student.pk) is None:
            self._direct_other_teachers[student.pk] = [
                r.elder for r in
                model.Relationship.objects.filter(
                    to_profile=self.instance,
                    direct=True,
                    from_profile__school_staff=True,
                    ).exclude(
                    from_profile=self.elder).select_related('from_profile')
                ]
        return self._direct_other_teachers[student.pk]


    def update_student_elders(self, student, elders):
        """
        Update student to have exactly given direct other-than-me elders.

        Exclude elder relationships due to group membership, and exclude the
        elder editing the student.

        Return boolean indicating whether we need to check for orphan
        relationships after updating group relationships.

        """
        current = set(self.direct_other_teachers(student))
        target = set(elders)
        remove = current.difference(target)
        add = target.difference(current)

        check_for_orphans = False

        if remove:
            model.Relationship.objects.filter(
                to_profile=student,
                from_profile__in=remove,
                ).update(direct=False)
            check_for_orphans = True

        for elder in add:
            rel, created = model.Relationship.objects.get_or_create(
                to_profile=student,
                from_profile=elder,
                )
            if not created and not rel.direct:
                rel.direct = True
                rel.save()

        return check_for_orphans


    def update_student_groups(self, student, groups):
        """
        Update student to be in only given groups of self.elder.

        Don't touch any memberships they may have in anyone else's groups.

        """
        current = set(student.student_in_groups.filter(owner=self.elder))
        target = set(groups)
        remove = current.difference(target)
        add = target.difference(current)

        if remove:
            student.student_in_groups.remove(*remove)
        if add:
            student.student_in_groups.add(*add)



class AddStudentForm(StudentForm):
    """Form for adding a student."""
    def __init__(self, *args, **kwargs):
        """Pre-check group, if in group context."""
        self.group = kwargs.pop('group', None)
        super(AddStudentForm, self).__init__(*args, **kwargs)
        if self.group is not None:
            self.fields['groups'].initial = [self.group.pk]


    def save(self):
        """
        Save and return new student.

        Creates a relationship between the elder adding the student and the new
        student.

        """
        name = self.cleaned_data["name"]

        student = model.Profile.create_with_user(
            school=self.elder.school, name=name, invited_by=self.elder)

        self.update_student_elders(
            student, list(self.cleaned_data['elders']) + [self.elder])
        self.update_student_groups(student, self.cleaned_data['groups'])

        return student



class GroupForm(forms.ModelForm):
    """Form for editing Groups."""
    students = pyoforms.ModelMultipleChoiceField(
        queryset=model.Profile.objects.none(),
        widget=StudentCheckboxSelectMultiple,
        required=False,
        )
    elders = pyoforms.ModelMultipleChoiceField(
        queryset=model.Profile.objects.none(),
        widget=ElderCheckboxSelectMultiple,
        required=False,
        )


    class Meta:
        model = model.Group
        fields = ['name', 'students', 'elders']
        widgets = {'name': forms.TextInput}


    def __init__(self, *args, **kwargs):
        """Store owner, narrow student and elder choices appropriately."""
        instance = kwargs.get('instance', None)
        if instance:
            self.owner = instance.owner
        else:
            self.owner = kwargs.pop('owner')
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['students'].queryset = model.Profile.objects.filter(
            relationships_to__from_profile=self.owner)
        self.fields['elders'].queryset = model.Profile.objects.filter(
            school=self.owner.school, school_staff=True).exclude(
            pk=self.owner.pk)
        self._old_name = self.instance.name


    def save(self, commit=True):
        """
        Implement saving ourselves to avoid inefficient M2M handling.

        """
        self.instance.name = self.cleaned_data['name']
        if commit:
            self.instance.save()
            self.save_m2m()
            if self._old_name != self.instance.name:
                events.group_edited(self.instance)
        return self.instance


    def save_m2m(self):
        """
        Save students and elders efficiently.

        By default ModelForm just assigns a list to an m2m attribute, which the
        ORM implements by first clearing the M2M and then adding all the
        submitted items back to it. We want a smarter diffing approach to avoid
        spurious delete/create signals.

        """
        # handle students
        selected = set(self.cleaned_data['students'])
        current = set(self.instance.students.all())

        remove = current.difference(selected)
        add = selected.difference(current)

        if remove:
            self.instance.students.remove(*remove)
        if add:
            self.instance.students.add(*add)

        # handle elders
        selected = set(self.cleaned_data['elders'])
        current = set(self.instance.elders.all())

        remove = current.difference(selected)
        add = selected.difference(current)

        if remove:
            self.instance.elders.remove(*remove)
        if add:
            self.instance.elders.add(*add)



class AddGroupForm(GroupForm):
    def save(self):
        """Save group, attaching new group to owner."""
        group = super(AddGroupForm, self).save(commit=False)
        group.owner = self.owner
        group.save()
        self.save_m2m()
        return group
