"""
Student/elder forms.

"""
import urllib

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
import floppyforms as forms

from portfoliyo import model, invites, formats, tasks
from .. import forms as pyoforms



class StudentCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/checkbox_select/_student.html'



class ElderCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/checkbox_select/_elder.html'



class GroupCheckboxSelectMultiple(pyoforms.CheckboxSelectMultiple):
    template_name = 'village/checkbox_select/_group.html'



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



class FamilyForm(forms.Form):
    """Common elements for editing/inviting family."""
    name = pyoforms.StripCharField(max_length=200, required=False)
    role = pyoforms.StripCharField(max_length=200, required=False)
    phone = pyoforms.StripCharField(max_length=20)


    def clean(self):
        """Either name or relationship must be provided."""
        if self.fields['phone'].required and not (
                self.cleaned_data.get('name') or
                self.cleaned_data.get('role')):
            raise forms.ValidationError(
                u"Either name or relationship is required.")
        return self.cleaned_data


    def clean_phone(self):
        """Ensure phone number is valid."""
        phone = self.cleaned_data.get('phone', "")
        if not phone and not self.fields['phone'].required:
            return phone
        phone = formats.normalize_phone(phone)
        if phone is None:
            raise forms.ValidationError(
                "Please supply a valid US or Canada mobile number.")
        return phone



class EditFamilyForm(FamilyForm):
    def __init__(self, *a, **kw):
        """
        Pull instance/rel kwargs out, set initial data.

        Optional 'rel' kwarg is the relationship between the edited elder and a
        student, if the elder is being edited in a student village context.

        """
        self.instance = kw.pop('instance')
        self.rel = kw.pop('rel', None)
        initial = kw.setdefault('initial', {})
        initial['name'] = self.instance.name
        initial['role'] = self.instance.role_in_context
        initial['phone'] = (
            formats.display_phone(self.instance.phone)
            if self.instance.phone else ''
            )
        super(EditFamilyForm, self).__init__(*a, **kw)


    def clean_phone(self):
        """Ensure phone number is valid and not a duplicate."""
        phone = super(EditFamilyForm, self).clean_phone()
        if model.Profile.objects.filter(
                phone=phone).exclude(pk=self.instance.pk).exists():
            msg = "A user with this phone number already exists."
            if self.rel:
                invite_url = reverse(
                    'invite_family',
                    kwargs={'student_id': self.rel.to_profile_id},
                    )
                msg = mark_safe(
                    '%s You can <a href="%s?phone=%s">invite them</a> '
                    'to this village instead.' %
                    (msg, invite_url, urllib.quote(self.cleaned_data['phone']))
                    )
            raise forms.ValidationError(msg)
        return phone


    def save(self, editor):
        """Save elder (optionally in context of given village relationship)."""
        self.instance.name = self.cleaned_data['name']

        old_phone = self.instance.phone
        new_phone = self.cleaned_data['phone'] or None
        self.instance.phone = new_phone

        old_profile_role = self.instance.role
        old_relationship_role = (
            self.rel.description_or_role if self.rel else self.instance.role)
        new_role = self.cleaned_data['role']
        if old_profile_role == old_relationship_role:
            self.instance.role = new_role
            self.instance.relationships_from.filter(
                description=old_profile_role).update(
                description='')
        else:
            self.rel.description = new_role
            self.rel.save()
        self.instance.save()

        if new_phone and new_phone != old_phone:
            invites.send_invite_sms(
                self.instance,
                template_name='sms/invite_elder.txt',
                extra_context={
                    'inviter': editor,
                    'student': self.rel.student if self.rel else None,
                    },
                )

        return self.instance



class InviteFamilyForm(FamilyForm):
    """A form for inviting a family member to a student village."""
    def __init__(self, *args, **kwargs):
        """
        Optionally takes ``rel`` between inviting elder and student.

        """
        self.rel = kwargs.pop('rel', None)
        super(InviteFamilyForm, self).__init__(*args, **kwargs)


    def clean_phone(self):
        """Ensure phone number is valid and that person can be invited."""
        phone = super(InviteFamilyForm, self).clean_phone()
        try:
            self.instance = model.Profile.objects.get(phone=phone)
        except model.Profile.DoesNotExist:
            self.instance = None
        else:
            students = set(self.instance.students)
            if self.rel is not None:
                students.discard(self.rel.student)
            if students:
                raise forms.ValidationError(
                    u"This person is already connected to a different student. "
                    u"Portfoliyo doesn't support family members in multiple "
                    u"villages yet, but we're working on it!"
                    )
        return phone


    def save(self, rel=None):
        """
        Save/return new elder profile & send invite, or return existing.

        Optionally takes ``rel`` between inviting elder and student. If given
        will override rel given at initialization time. A rel must be given
        either at initialization or save time.

        """
        if rel is not None:
            self.rel = rel

        inviter = self.rel.elder

        name = self.cleaned_data.get('name')
        phone = self.cleaned_data.get('phone')
        relationship = self.cleaned_data.get('role', u"")

        if self.instance is None:
            self.instance = model.Profile.create_with_user(
                school=inviter.school,
                name=name,
                phone=phone,
                role=relationship,
                is_active=True,
                school_staff=False,
                invited_by=inviter,
                )

        # send invite notifications
        invites.send_invite_sms(
            self.instance,
            template_name='sms/invite_elder.txt',
            extra_context={
                'inviter': model.elder_in_context(self.rel),
                'student': self.rel.student,
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
    role = pyoforms.StripCharField(max_length=200)
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
        role = self.cleaned_data.get("role", u"")

        # first check for an existing user match
        try:
            profile = model.Profile.objects.get(user__email=email)
        except model.Profile.DoesNotExist:
            profile = model.Profile.create_with_user(
                school=self.inviter.school,
                email=email,
                role=role,
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
                profile,
                template_name='emails/invite_elder',
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
                    'description': role,
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
    name = pyoforms.StripCharField()
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
            tasks.push_event.delay('student_edited', student.id)

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
    """Form for adding a student (and optionally a family member)."""
    def __init__(self, *args, **kwargs):
        """Pre-check group, if in group context."""
        self.group = kwargs.pop('group', None)
        super(AddStudentForm, self).__init__(*args, **kwargs)
        if self.group is not None:
            self.fields['groups'].initial = [self.group.pk]
        kwargs.pop('elder', None)
        kwargs['prefix'] = 'family'
        self.family_form = InviteFamilyForm(*args, **kwargs)
        # if any data was entered in the family form, then all fields are
        # required; but the entire form is optional.
        if not self.family_form.has_changed():
            for field in self.family_form.fields.values():
                field.required = False
                field.widget.is_required = False


    def is_valid(self):
        """Inline invite-family form must also be valid."""
        return (
            self.family_form.is_valid() and
            super(AddStudentForm, self).is_valid()
            )


    def save(self):
        """
        Save and return new student.

        Creates a relationship between the elder adding the student and the new
        student.

        """
        name = self.cleaned_data["name"]

        student = model.Profile.create_with_user(
            school=self.elder.school, name=name, invited_by=self.elder)

        rel = model.Relationship.objects.create(
                to_profile=student,
                from_profile=self.elder,
                level=model.Relationship.LEVEL.owner,
                )
        self.update_student_elders(student, self.cleaned_data['elders'])
        self.update_student_groups(student, self.cleaned_data['groups'])

        if self.family_form.has_changed():
            self.family_form.save(rel)

        return student



class GroupForm(forms.ModelForm):
    """Form for editing Groups."""
    name = pyoforms.StripCharField()
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
                tasks.push_event.delay(
                    'group_edited', self.instance.id, self.instance.owner_id)
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
