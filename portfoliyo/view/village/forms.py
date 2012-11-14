"""
Student/elder forms.

"""
from django.db.models import Q
import floppyforms as forms

from portfoliyo import model, invites, formats
from portfoliyo.model import events
from .. import forms as pyoforms



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



class EditElderForm(forms.Form):
    name = forms.CharField(max_length=200)
    role = forms.CharField(max_length=200)


    def __init__(self, *a, **kw):
        """Pull instance kwarg out."""
        self.instance = kw.pop('instance')
        initial = kw.setdefault('initial', {})
        initial['name'] = self.instance.name
        initial['role'] = self.instance.role
        super(EditElderForm, self).__init__(*a, **kw)


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

        return self.instance



class InviteFamilyForm(forms.Form):
    """A form for inviting a family member to a student village."""
    phone = forms.CharField(max_length=255)
    relationship = forms.CharField(max_length=200)


    def __init__(self, *args, **kwargs):
        """
        Requires ``rel``: relationship between inviting elder and student.

        """
        self.rel = kwargs.pop('rel')
        self.inviter = self.rel.elder
        super(InviteFamilyForm, self).__init__(*args, **kwargs)


    def clean_phone(self):
        phone = formats.normalize_phone(self.cleaned_data["phone"])
        if phone is None:
            raise forms.ValidationError(
                "Please supply a valid US/Canada mobile number.")
        return phone


    def save(self):
        """Save/return new elder profile & send invite, or return existing."""
        phone = self.cleaned_data.get('phone')
        relationship = self.cleaned_data.get('relationship', u"")

        # first check for an existing user match
        try:
            self.instance = model.Profile.objects.get(phone=phone)
        except model.Profile.DoesNotExist:
            self.instance = model.Profile.create_with_user(
                school=self.inviter.school,
                phone=phone,
                role=relationship,
                is_active=True,
                school_staff=False,
                invited_by=self.inviter,
                )
            created = True
        else:
            created = False

        # send invite notifications
        if created:
            invites.send_invite_sms(
                self.instance.user,
                template_name='registration/invite_elder_sms.txt',
                extra_context={
                    'inviter': self.inviter,
                    'student': self.rel.student if self.rel else None,
                    'inviter_rel': self.rel,
                    },
                )

        rel, created = model.Relationship.objects.get_or_create(
            from_profile=self.instance,
            to_profile=self.rel.student,
            defaults={
                'description': relationship,
                }
            )

        if not created and not rel.direct:
            rel.direct = True
            rel.save()

        return self.instance



class InviteTeacherForm(forms.Form):
    """A form for inviting a teacher to a student village."""
    email = forms.EmailField(max_length=255)
    relationship = forms.CharField(max_length=200)
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
        """
        Accepts ``rel`` or ``group``.

        ``rel`` is relationship between inviting elder and student, if teacher
        is being invited in student context.

        ``group`` is a group owned by inviting elder, if teacher is being
        invited in group context.

        """
        self.rel = kwargs.pop('rel', None)
        self.group = kwargs.pop('group', None)
        self.inviter = self.rel.elder if self.rel else self.group.owner
        super(InviteTeacherForm, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = model.Group.objects.filter(
            owner=self.inviter)
        self.fields['students'].queryset = model.Profile.objects.filter(
            relationships_to__from_profile=self.inviter)
        self.fields['students'].groups_attr = 'student_in_groups'
        if self.rel:
            self.fields['students'].initial = [self.rel.to_profile_id]
        if self.group:
            self.fields['groups'].initial = [self.group.id]


    def clean_email(self):
        return formats.normalize_email(self.cleaned_data["email"])


    def save(self):
        """Save/return new elder profile & send invites, or return existing."""
        email = self.cleaned_data.get("email")
        relationship = self.cleaned_data.get("relationship", u"")

        # first check for an existing user match
        try:
            profile = model.Profile.objects.get(user__email=email)
        except model.Profile.DoesNotExist:
            profile = model.Profile.create_with_user(
                school=self.inviter.school,
                email=email,
                role=relationship,
                is_active=False,
                school_staff=True,
                invited_by=self.inviter,
                )
            created = True
        else:
            created = False

        # send invite notifications
        if created:
            invites.send_invite_email(
                profile.user,
                email_template_name='registration/invite_elder_email.txt',
                subject_template_name='registration/invite_elder_subject.txt',
                extra_context={
                    'inviter': self.inviter,
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

        # inviting an elder never removes from groups, only adds
        profile.elder_in_groups.add(*self.cleaned_data['groups'])

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
        elder_conditions = Q(school=self.elder.school)
        # explicitly allow already-related elders when editing
        if self.instance.pk:
            elder_conditions = elder_conditions | Q(
                relationships_from__to_profile=self.instance)
        self.fields['elders'].queryset = model.Profile.objects.filter(
            elder_conditions).exclude(
            pk=self.elder.pk).exclude(school_staff=False).distinct().order_by(
                'name')
        self.fields['elders'].groups_attr = 'elder_in_groups'
        self.owners = set()
        if self.instance.pk:
            self.fields['groups'].initial = [
                g.pk for g in self.instance.student_in_groups.all()]
            initial_elders = self.direct_other_teachers(self.instance)
            self.owners = set([e for e in initial_elders if e.owner])
            self.fields['elders'].initial = [e.pk for e in initial_elders]
            self.fields['elders'].widget.context_data['owners'] = set(
                [str(e.pk) for e in self.owners])
        self._old_name = self.instance.name


    def save(self):
        """Save and return student."""
        student = super(StudentForm, self).save()

        check_for_orphans = self.update_student_elders(
            student, self.cleaned_data['elders'])
        self.update_student_groups(student, self.cleaned_data['groups'])
        if check_for_orphans:
            model.Relationship.objects.delete_orphans()

        # if the name is unchanged, only send the event to the editing elder
        # (in case they are logged in in two places - changes to groups may be
        # relevant to them). If name is changed, send to all elders so nav can
        # be updated.
        if self._old_name != self.instance.name:
            events.student_edited(student, *student.elders)

        return student


    def direct_other_teachers(self, student):
        """
        Get all direct (non-group) other-than-me teachers of a student.

        Each teacher has an additional 'owner' boolean attribute; True if that
        teacher has an owner-level relationship with that student.

        Memoized by student id.

        """
        if not hasattr(self, '_direct_other_teachers'):
            self._direct_other_teachers = {}
        if self._direct_other_teachers.get(student.pk) is None:
            qs = model.Relationship.objects.filter(
                to_profile=self.instance,
                direct=True,
                from_profile__school_staff=True,
                ).exclude(
                from_profile=self.elder).select_related('from_profile')
            self._direct_other_teachers[student.pk] = []
            for rel in qs:
                rel.elder.owner = (rel.level == model.Relationship.LEVEL.owner)
                self._direct_other_teachers[student.pk].append(rel.elder)
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
        remove = current.difference(target).difference(self.owners)
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

        model.Relationship.objects.create(
                to_profile=student,
                from_profile=self.elder,
                level=model.Relationship.LEVEL.owner,
                )
        self.update_student_elders(student, self.cleaned_data['elders'])
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
            relationships_to__from_profile=self.owner).order_by('name')
        elder_conditions = Q(school=self.owner.school, school_staff=True)
        if self.instance.pk:
            elder_conditions = elder_conditions | Q(
                elder_in_groups=self.instance)
        self.fields['elders'].queryset = model.Profile.objects.filter(
            elder_conditions).exclude(pk=self.owner.pk).distinct().order_by(
            'name')
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
