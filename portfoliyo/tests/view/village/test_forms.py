"""Tests for village forms."""
from django.core import mail
import mock

from portfoliyo.view.village import forms

from portfoliyo.tests import factories, utils


class TestEditElderForm(object):
    def test_edit_custom_relationship_description(self):
        """
        Editing elder changes role in that village, profile only if matched.

        Elder's role in particular village may be different from their profile
        role; the new role should always take effect in the village in which
        they are being edited, and their profile role should only be updated if
        it was the same as their role in that village.

        """
        rel = factories.RelationshipFactory(
            description="gifted and talented teacher",
            from_profile__role="math teacher",
            )
        form = forms.EditElderForm(
            {'name': 'John Doe', 'role': 'science teacher'}, profile=rel.elder)
        assert form.is_valid(), dict(form.errors)
        profile = form.save(rel)

        assert profile.role == 'math teacher'
        assert utils.refresh(rel).description == 'science teacher'


    def test_empty_relationship_description_left_alone(self):
        """Empty relationship description left empty."""
        rel = factories.RelationshipFactory(
            description="",
            from_profile__role="math teacher",
            )
        form = forms.EditElderForm(
            {'name': 'John Doe', 'role': 'science teacher'}, profile=rel.elder)
        assert form.is_valid(), dict(form.errors)
        profile = form.save(rel)

        assert profile.role == 'science teacher'
        assert utils.refresh(rel).description == ''



class TestInviteElderForm(object):
    """Tests for InviteElderForm."""
    def data(self, **kwargs):
        """Utility method to get default form data, with override option."""
        defaults = {
            'contact': 'foo@example.com',
            'relationship': 'mentor',
            'school_staff': False,
            }
        defaults.update(kwargs)
        return defaults


    def test_phone_contact(self, sms):
        """If contact field is phone, it's normalized and saved to profile."""
        form = forms.InviteElderForm(
            self.data(contact='(321)456-7890', relationship='father'))
        assert form.is_valid(), dict(form.errors)
        rel = factories.RelationshipFactory(
            from_profile__name="Teacher John",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        request = mock.Mock()
        request.user = rel.elder.user
        profile = form.save(request, rel)

        assert profile.phone == u'+13214567890'
        assert len(sms.outbox) == 1
        assert sms.outbox[0].to == u'+13214567890'
        assert sms.outbox[0].body == (
            "Hi! Jimmy Doe's Math Teacher (Teacher John) "
            "will text you from this number. "
            "Text 'stop' any time if you don't want this."
            )


    def test_email_contact(self):
        """If contact field is email, invite email is sent."""
        form = forms.InviteElderForm(self.data(contact='bar@EXAMPLE.com'))
        assert form.is_valid(), dict(form.errors)
        rel = factories.RelationshipFactory()
        request = mock.Mock()
        request.get_host.return_value = 'portfoliyo.org'
        request.is_secure.return_value = False
        request.user = rel.elder.user
        profile = form.save(request, rel)

        assert profile.user.email == u'bar@example.com'
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [u'bar@example.com']


    def test_email_user_inactive(self):
        """User invited by email is inactive."""
        form = forms.InviteElderForm(self.data())
        assert form.is_valid(), dict(form.errors)
        rel = factories.RelationshipFactory()
        profile = form.save(mock.Mock(), rel)

        assert not profile.user.is_active


    def test_phone_user_active(self):
        """User invited by phone is immediately active."""
        form = forms.InviteElderForm(self.data(contact='+13216540987'))
        assert form.is_valid(), dict(form.errors)
        rel = factories.RelationshipFactory()
        profile = form.save(mock.Mock(), rel)

        assert profile.user.is_active


    def test_bad_contact(self):
        """If contact field is unparseable, validation error is raised."""
        form = forms.InviteElderForm(self.data(contact='baz'))

        assert not form.is_valid()
        assert form.errors['contact'] == [
            u"Please supply a valid email address or US mobile number."]


    def test_user_with_email_exists(self):
        """If a user with given email already exists, no new user is created."""
        elder = factories.ProfileFactory(user__email='foo@example.com')
        form = forms.InviteElderForm(self.data(contact='foo@example.COM'))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile


    def test_user_with_phone_exists(self):
        """If a user with given phone already exists, no new user is created."""
        elder = factories.ProfileFactory(phone='+13214567890')
        form = forms.InviteElderForm(self.data(contact='321.456.7890'))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile


    def test_update_existing_elder_to_staff(self):
        """If a non-staff is added as staff elder, they gain staff status."""
        elder = factories.ProfileFactory(
            school_staff=False, phone='+13214567890')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, school_staff=True))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert profile.school_staff


    def test_update_existing_elder_role(self):
        """If existing elder has no role, update from new relationship."""
        elder = factories.ProfileFactory(role='', phone='+13214567890')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, relationship='foo'))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert profile.role == u'foo'


    def test_existing_elder_has_role(self):
        """If existing elder has a role, it isn't updated."""
        elder = factories.ProfileFactory(
            school_staff=False, role='something', phone='+13214567890')
        form = forms.InviteElderForm(
            self.data(
                contact=elder.phone, relationship='foo', school_staff=True))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert profile.role == u'something'


    def test_existing_elder_needs_no_update(self):
        """If existing elder has role and is not to be staff, no update done."""
        elder = factories.ProfileFactory(phone='+13214567890', role='foo')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, school_staff=False))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert not profile.school_staff
        assert profile.role == 'foo'


    def test_relationship_exists(self):
        """If existing elder is already elder for student, no error."""
        rel = factories.RelationshipFactory(from_profile__phone='+13214567890')
        form = forms.InviteElderForm(self.data(contact=rel.elder.phone))
        assert form.is_valid(), dict(form.errors)
        profile = form.save(None, rel)

        assert rel.elder == profile
        assert len(profile.students) == 1



class TestStudentForms(object):
    def test_add_student(self):
        """Saves a student, given just name."""
        elder = factories.ProfileFactory.create()
        form = forms.AddStudentForm({'name': "Some Student"}, elder=elder)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()
        rel = profile.elder_relationships[0]

        assert profile.name == u"Some Student"
        assert profile.invited_by == elder
        assert profile.elders == [elder]
        assert rel.elder == elder
        assert rel.student == profile


    def test_add_student_with_group_and_elder(self):
        """Can associate a student with a group or an elder while creating."""
        elder = factories.ProfileFactory.create()
        other_elder = factories.ProfileFactory.create(
            school=elder.school, school_staff=True)
        group = factories.GroupFactory.create(owner=elder)
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'groups': [group.id],
                'elders': [other_elder.id],
                },
            elder=elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {elder, other_elder}
        assert profile.student_in_groups.get() == group


    def test_edit_student_with_group_and_elder(self):
        """Can (de/)associate a student with a group/elder while editing."""
        rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(to_profile=rel.student)
        group = factories.GroupFactory.create(owner=rel.elder)
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [group.id],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {rel.elder}
        assert profile.student_in_groups.get() == group


    def test_edit_form_group_and_elder_initial(self):
        """Group and elder initial values set correctly when editing student."""
        rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student, from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

        assert form.fields['elders'].initial == [other_rel.elder.pk]
        assert form.fields['groups'].initial == [group.pk]


    def test_edit_student_add_elder(self):
        """Can associate a student with an elder while editing."""
        rel = factories.RelationshipFactory.create()
        new_elder = factories.ProfileFactory(
            school=rel.elder.school, school_staff=True)
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [new_elder.pk],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {rel.elder, new_elder}


    def _assert_cannot_add(self, rel, elder=None, group=None):
        form = forms.StudentForm(
            {
                'name': 'New Name',
                'elders': [elder.pk] if elder else [],
                'groups': [group.pk] if group else [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert not form.is_valid()
        if elder is not None:
            assert form.errors['elders'] == [
                u"Select a valid choice. %s is not one of the available choices."
                % elder.pk
                ]
        if group is not None:
            assert form.errors['students'] == [
                u"Select a valid choice. %s is not one of the available choices."
                % group.pk
                ]


    def test_cannot_associate_elder_from_other_school(self):
        """Cannot associate student with an elder from a different school."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(school_staff=True)

        self._assert_cannot_add(rel, elder)


    def test_cannot_associate_non_school_staff_elder(self):
        """Cannot associate student with a non-staff elder."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=False, school=rel.elder.school)

        self._assert_cannot_add(rel, elder)


    def test_cannot_associate_deleted_elder(self):
        """Cannot associate student with a deleted elder."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=True, school=rel.elder.school, deleted=True)

        self._assert_cannot_add(rel, elder)


    def test_cannot_associate_group_from_other_owner(self):
        """Cannot associate student with a group that isn't yours."""
        rel = factories.RelationshipFactory.create()
        group = factories.GroupFactory.create()

        self._assert_cannot_add(rel, group)


    def test_add_two_students_same_name(self):
        """Adding two students with same name causes no username trouble."""
        form = forms.AddStudentForm(
            {'name': "Some Student"}, elder=factories.ProfileFactory.create())
        assert form.is_valid(), dict(form.errors)
        profile1 = form.save()

        form = forms.AddStudentForm(
            {'name': "Some Student"}, elder=factories.ProfileFactory.create())
        assert form.is_valid(), dict(form.errors)
        profile2 = form.save()

        assert profile1 != profile2



class TestGroupForms(object):
    def test_create_group_with_students_and_elders(self):
        """Can add students and elders to a group when creating it."""
        me = factories.ProfileFactory.create(school_staff=True)
        elder = factories.ProfileFactory.create(
            school_staff=True, school=me.school)
        rel = factories.RelationshipFactory.create(from_profile=me)

        form = forms.AddGroupForm(
            {
                'name': 'New Group',
                'elders': [elder.pk],
                'students': [rel.student.pk],
                },
            owner=me,
            )

        assert form.is_valid(), dict(form.errors)
        group = form.save()

        assert set(group.students.all()) == {rel.student}
        assert set(group.elders.all()) == {elder}


    def test_edit_group_with_students_and_elders(self):
        """Can add/remove students and elders from group when editing."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        rel = factories.RelationshipFactory.create(from_profile=group.owner)
        group.students.add(rel.student)

        form = forms.GroupForm(
            {
                'name': 'New Name',
                'elders': [elder.pk],
                'students': [],
                },
            instance=group,
            )

        assert form.is_valid(), dict(form.errors)
        group = form.save()

        assert len(group.students.all()) == 0
        assert set(group.elders.all()) == {elder}


    def _assert_cannot_add(self, group, elder=None, student=None):
        form = forms.GroupForm(
            {
                'name': 'New Name',
                'elders': [elder.pk] if elder else [],
                'students': [student.pk] if student else [],
                },
            instance=group,
            )

        assert not form.is_valid()
        if elder is not None:
            assert form.errors['elders'] == [
                u"Select a valid choice. %s is not one of the available choices."
                % elder.pk
                ]
        if student is not None:
            assert form.errors['students'] == [
                u"Select a valid choice. %s is not one of the available choices."
                % student.pk
                ]


    def test_cannot_add_elder_from_other_school(self):
        """Cannot add an elder from a different school to a group."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(school_staff=True)

        self._assert_cannot_add(group, elder=elder)


    def test_cannot_add_non_staff_elder(self):
        """Cannot add an elder who is not school staff."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=False, school=group.owner.school)

        self._assert_cannot_add(group, elder=elder)


    def test_cannot_add_unrelated_student(self):
        """Cannot add a student you aren't related to to a group."""
        group = factories.GroupFactory.create()
        student = factories.ProfileFactory.create()

        self._assert_cannot_add(group, student=student)


    def test_cannot_add_deleted_elder(self):
        """Cannot add a deleted elder."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school, deleted=True)

        self._assert_cannot_add(group, elder=elder)


    def test_cannot_add_deleted_student(self):
        """Cannot add a deleted student."""
        group = factories.GroupFactory.create()
        rel = factories.RelationshipFactory.create(
            from_profile=group.owner, to_profile__deleted=True)

        self._assert_cannot_add(group, student=rel.student)
