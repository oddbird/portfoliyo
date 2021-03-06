"""Tests for village forms."""
from django.core import mail
from django.core.urlresolvers import reverse
import mock

from portfoliyo import model
from portfoliyo.view.village import forms

from portfoliyo.tests import factories, utils


class TestEditFamilyForm(object):
    def test_edit_family_member(self, db):
        """Can edit a family member's name."""
        phone = '+13216540987'
        parent = factories.ProfileFactory.create(
            phone=phone, name='Old Name', role='dad')

        form = forms.EditFamilyForm(
            {'name': 'New Name', 'role': 'dad', 'phone': phone},
            instance=parent,
            )
        assert form.is_valid(), dict(form.errors)
        assert parent == form.save(editor=factories.ProfileFactory.create())
        parent = utils.refresh(parent)
        assert parent.name == 'New Name'


    def test_edit_custom_relationship_description(self, db):
        """
        Editing elder changes role in that village, profile only if matched.

        Elder's role in particular village may be different from their profile
        role; the new role should always take effect in the village in which
        they are being edited, and their profile role should only be updated if
        it was the same as their role in that village.

        """
        phone = '+13216540987'
        rel = factories.RelationshipFactory.create(
            description="mother",
            from_profile__role="mom",
            from_profile__phone=phone,
            )
        form = forms.EditFamilyForm(
            {
                'name': "Jane Doe",
                'role': "aunt",
                'phone': phone,
                },
            instance=rel.elder,
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save(editor=factories.ProfileFactory.create())

        assert profile.role == "mom"
        assert utils.refresh(rel).description == "aunt"


    def test_edit_relationship_description(self, db):
        """Editing elder sets role to empty if it matches village role. """
        phone = '+13216540987'
        rel = factories.RelationshipFactory.create(
            description="mom",
            from_profile__role="mom",
            from_profile__phone=phone,
            )
        form = forms.EditFamilyForm(
            {
                'name': "Jane Doe",
                'role': "aunt",
                'phone': phone,
                },
            instance=rel.elder,
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save(editor=factories.ProfileFactory.create())

        assert profile.role == "aunt"
        assert utils.refresh(rel).description == ""


    def test_empty_relationship_description_left_alone(self, db):
        """Empty relationship description left empty."""
        phone = '+13216540987'
        rel = factories.RelationshipFactory.create(
            description="",
            from_profile__role="mom",
            from_profile__phone=phone,
            )
        form = forms.EditFamilyForm(
            {
                'name': "Jane Doe",
                'role': "aunt",
                'phone': phone,
                },
            instance=rel.elder,
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save(editor=factories.ProfileFactory.create())

        assert profile.role == "aunt"
        assert utils.refresh(rel).description == ""


    def test_update_phone_sends_invite_sms(self, sms, db):
        """Changing elder's phone number sends invite SMS to that number."""
        teacher_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            from_profile__name="Teacher John",
            from_profile__role="Various",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        parent_rel = factories.RelationshipFactory.create(
            from_profile__phone="+13216549876",
            to_profile=teacher_rel.student,
            )

        form = forms.EditFamilyForm(
            {
                'name': 'John Doe',
                'role': 'dad',
                'phone': '+17894561234',
                },
            instance=parent_rel.elder,
            rel=parent_rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save(editor=model.elder_in_context(teacher_rel))

        assert profile.phone == '+17894561234'
        assert len(sms.outbox) == 1
        assert sms.outbox[0].to == '+17894561234'
        assert sms.outbox[0].body == (
            "Hi! Jimmy Doe's Math Teacher, Teacher John, "
            "will text you from this number. "
            "Text 'stop' any time if you don't want this."
            )


    def test_bad_phone(self, db):
        """Bad phone number results in validation error."""
        elder = factories.ProfileFactory.create()

        form = forms.EditFamilyForm(
            {
                'name': 'John Doe',
                'role': 'dad',
                'phone': 'foo',
                },
            instance=elder,
            )
        assert not form.is_valid()
        assert form.errors['phone'] == [
            u"Please supply a valid US or Canada mobile number."]


    def test_dupe_phone(self, db):
        """Dupe phone number results in validation error."""
        factories.ProfileFactory.create(phone='+13216540987')
        elder = factories.ProfileFactory.create()

        form = forms.EditFamilyForm(
            {
                'name': 'John Doe',
                'role': 'dad',
                'phone': '321-654-0987',
                },
            instance=elder,
            )
        assert not form.is_valid()
        assert form.errors['phone'] == [
            u"A user with this phone number already exists."]


    def test_dupe_phone_in_village(self, db):
        """Dupe phone number in village links to invite."""
        factories.ProfileFactory.create(phone='+13216540987')
        rel = factories.RelationshipFactory.create()

        form = forms.EditFamilyForm(
            {
                'name': 'John Doe',
                'role': 'dad',
                'phone': '(321) 654-0987',
                },
            instance=rel.elder,
            rel=rel,
            )
        assert not form.is_valid()
        invite_url = reverse(
            'invite_family',
            kwargs={'student_id': rel.to_profile_id},
            ) + '?phone=%28321%29%20654-0987'
        assert form.errors['phone'] == [
            u"A user with this phone number already exists. "
            u'You can <a href="%s">invite them</a> to this village instead.'
            % invite_url
            ]


    def test_initial_role_is_contextual(self, db):
        """role_in_context is used to populate role field."""
        rel = factories.RelationshipFactory.create(
            from_profile__role="Various",
            description="Math Teacher",
            )

        form = forms.EditFamilyForm(instance=model.elder_in_context(rel))

        assert form.initial['role'] == "Math Teacher"



class TestInviteTeacherForm(object):
    """Tests for InviteTeacherForm."""
    def data(self, **kwargs):
        """Utility method to get default form data, with override option."""
        defaults = {
            'email': 'foo@example.com',
            'role': 'math teacher',
            }
        defaults.update(kwargs)
        return defaults


    def test_invite_new_creates_profile(self, db):
        rel = factories.RelationshipFactory.create()
        form = forms.InviteTeacherForm(
            self.data(email='bar@EXAMPLE.com'), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert profile.user.email == u'bar@example.com'
        assert profile.school_staff


    def test_invite_new_sends_invite_email(self, db):
        rel = factories.RelationshipFactory.create()
        form = forms.InviteTeacherForm(
            self.data(email='bar@EXAMPLE.com'), rel=rel)
        assert form.is_valid(), dict(form.errors)
        form.save()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [u'bar@example.com']


    def test_invite_teacher_with_students_and_groups(self, db):
        """Can associate newly-invited teacher with students and groups."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel.elder)
        group = factories.GroupFactory.create(owner=rel.elder)
        form = forms.InviteTeacherForm(
            self.data(
                groups=[group.pk], students=[rel.student.pk, rel2.student.pk]),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elder_in_groups.all()) == {group}
        assert set(profile.students) == {rel.student, rel2.student}


    def test_invite_teacher_transforms_group_relationship_to_direct(self, db):
        """Can transform a group student relationship to a direct one."""
        rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            school=rel.elder.school,
            from_profile__school_staff=True,
            from_profile__user__email='foo@example.com',
            )
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)
        group.elders.add(other_rel.elder)
        group_rel = group.relationships.get()

        form = forms.InviteTeacherForm(
            self.data(
                contact='foo@example.com',
                groups=[],
                students=[rel.student.pk],
                ),
            rel=rel,
            )

        assert form.is_valid(), dict(form.errors)
        form.save()

        group_rel = utils.refresh(group_rel)
        assert group_rel.direct
        # group membership is not removed, though
        assert set(group_rel.groups.all()) == {group}


    def test_invite_teacher_never_removes_student_relationships(self, db):
        """Inviting existing teacher never removes student relationships."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            from_profile__user__email='foo@example.com')

        form = forms.InviteTeacherForm(
            self.data(
                contact='foo@example.com',
                students=[rel.student.pk],
                ),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.students) == {rel.student, rel2.student}


    def test_invite_teacher_never_removes_from_another_teachers_group(self, db):
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(user__email='foo@example.com')
        group = factories.GroupFactory.create()
        group.elders.add(elder)

        form = forms.InviteTeacherForm(
            self.data(contact='foo@example.com', groups=[]), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elder_in_groups.all()) == {group}


    def test_invite_teacher_never_removes_from_my_group(self, db):
        """Inviting a teacher should never remove them from groups."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(user__email='foo@example.com')
        group = factories.GroupFactory.create(owner=rel.elder)
        group.elders.add(elder)

        form = forms.InviteTeacherForm(
            self.data(contact='foo@example.com', groups=[]), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elder_in_groups.all()) == {group}


    def test_context_student_pre_checked(self, db):
        """Student from whose village teacher is invited initially checked."""
        rel = factories.RelationshipFactory.create()

        form = forms.InviteTeacherForm(rel=rel)

        assert form.fields['students'].initial == [rel.student.pk]


    def test_context_group_pre_checked(self, db):
        """Group teacher is invited to is initially checked."""
        group = factories.GroupFactory.create()

        form = forms.InviteTeacherForm(group=group)

        assert form.fields['groups'].initial == [group.pk]


    def test_sets_invited_by(self, db):
        """Invited_by field is set to inviting elder."""
        rel = factories.RelationshipFactory.create()
        form = forms.InviteTeacherForm(self.data(), rel=rel)
        assert form.is_valid()
        profile = form.save()

        assert profile.invited_by == rel.elder


    def test_sets_country_code(self, db):
        """Country_code field is set to same country as inviting teacher."""
        rel = factories.RelationshipFactory.create(
            from_profile__country_code='ca')
        form = forms.InviteTeacherForm(self.data(), rel=rel)
        assert form.is_valid()
        profile = form.save()

        assert profile.country_code == 'ca'


    def test_new_user_inactive(self, db):
        """New user invited by email is inactive."""
        rel = factories.RelationshipFactory.create()
        form = forms.InviteTeacherForm(self.data(), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert not profile.user.is_active


    def test_user_with_email_exists(self, db):
        """If a user with given email already exists, no new user is created."""
        elder = factories.ProfileFactory.create(user__email='foo@example.com')
        form = forms.InviteTeacherForm(
            self.data(contact='foo@example.COM'),
            rel=factories.RelationshipFactory(),
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert elder == profile


    def test_existing_teacher_new_role(self, db):
        """Inviting an existing teacher with new role doesn't change profile."""
        factories.ProfileFactory.create(
            user__email='foo@example.com', role="math teacher")
        rel = factories.RelationshipFactory()
        form = forms.InviteTeacherForm(
            self.data(
                contact='foo@example.com',
                role="science teacher",
                students=[rel.student.pk],
                ),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        p = form.save()

        assert p.role == u"math teacher"
        assert p.student_relationships[0].description == u"science teacher"


    def test_existing_teacher_has_role(self, db):
        """If existing teacher has a role, it isn't updated."""
        teacher = factories.ProfileFactory.create(
            school_staff=True, role='something', user__email='foo@example.com')
        form = forms.InviteTeacherForm(
            self.data(
                email=teacher.user.email, role='foo'),
            rel=factories.RelationshipFactory(),
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert teacher == profile
        assert profile.role == u'something'


    def test_existing_user_notified(self, db):
        """If a user with given email already exists, they are notified."""
        invitee = factories.ProfileFactory.create(user__email='foo@example.com')
        rel = factories.RelationshipFactory()
        form = forms.InviteTeacherForm(
            self.data(contact='foo@example.COM', students=[rel.student.pk]),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        mock_record_notification.assert_called_once_with(
            'village_additions', rel.elder, [invitee], {rel.student})


    def test_no_notification_if_relationship_exists(self, db):
        """If existing teacher is already teacher for student, no error."""
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='foo@example.com')
        form = forms.InviteTeacherForm(
            self.data(contact=rel.elder.user.email, students=[rel.student.pk]),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            profile = form.save()

        assert rel.elder == profile
        assert len(profile.students) == 1

        # no students notified
        mock_record_notification.assert_called_once_with(
            'village_additions', rel.elder, [rel.elder], set())


    def test_existing_user_notified_of_group(self, db):
        """Existing teacher's notified of group addition (new students only)."""
        inviter = factories.ProfileFactory.create()
        invitee = factories.ProfileFactory.create(user__email='foo@example.com')
        rel1 = factories.RelationshipFactory.create(from_profile=inviter)
        rel2 = factories.RelationshipFactory.create(from_profile=inviter)
        factories.RelationshipFactory.create(
            from_profile=invitee, to_profile=rel2.student)
        group = factories.GroupFactory.create(owner=inviter)
        group.students.add(rel1.student, rel2.student)
        form = forms.InviteTeacherForm(
            self.data(
                contact='foo@example.COM',
                groups=[group.pk],
                students=[],
                ),
            group=group,
            )
        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        # no notification for rel2.student b/c already had relationship
        mock_record_notification.assert_called_once_with(
            'village_additions', inviter, [invitee], {rel1.student})



class TestInviteFamilyForm(object):
    """Tests for InviteFamilyForm."""
    def data(self, **kwargs):
        """Utility method to get default form data, with override option."""
        defaults = {
            'phone': '321-456-1234',
            'role': 'mom',
            }
        defaults.update(kwargs)
        return defaults


    def test_invite_family_by_role(self, sms, db):
        """Can invite a family member by role and phone."""
        rel = factories.RelationshipFactory.create(
            from_profile__name="Teacher John",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        form = forms.InviteFamilyForm(
            self.data(phone='(321)456-7890', role='father'),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert profile.phone == u'+13214567890'
        assert not profile.school_staff
        assert len(sms.outbox) == 1
        assert sms.outbox[0].to == u'+13214567890'
        assert sms.outbox[0].body == (
            "Hi! Jimmy Doe's Math Teacher, Teacher John, "
            "will text you from this number. "
            "Text 'stop' any time if you don't want this."
            )


    def test_invite_family_by_name(self, db):
        """Can invite a family member by name and phone."""
        rel = factories.RelationshipFactory.create(
            from_profile__name="Teacher John",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        form = forms.InviteFamilyForm(
            self.data(phone='(321)456-7890', role='', name="Jane Doe"),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert profile.phone == u'+13214567890'
        assert profile.name == "Jane Doe"
        assert not profile.school_staff


    def test_either_name_or_role_required(self, db):
        """Either name or role field must be filled out."""
        rel = factories.RelationshipFactory.create(
            from_profile__name="Teacher John",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        form = forms.InviteFamilyForm(
            self.data(phone='(321)456-7890', role="", name=""),
            rel=rel,
            )
        assert not form.is_valid()
        assert form.errors['__all__'] == [
            u"Either name or relationship is required."]


    def test_bad_phone(self, db):
        """Bad phone number results in validation error."""
        form = forms.InviteFamilyForm(
            self.data(phone='foo'), rel=factories.RelationshipFactory.create())

        assert not form.is_valid()
        assert form.errors['phone'] == [
            u"Please supply a valid US or Canada mobile number."]


    def test_sets_invited_by(self, db):
        """Invited_by field is set to inviting elder."""
        rel = factories.RelationshipFactory.create()
        form = forms.InviteFamilyForm(self.data(), rel=rel)
        assert form.is_valid()
        profile = form.save()

        assert profile.invited_by == rel.elder


    def test_sets_country_code(self, db):
        """Country_code field is set to same country as inviting teacher."""
        rel = factories.RelationshipFactory.create(
            from_profile__country_code='ca')
        form = forms.InviteFamilyForm(self.data(), rel=rel)
        assert form.is_valid()
        profile = form.save()

        assert profile.country_code == 'ca'


    def test_phone_user_active(self, db):
        """User invited by phone is immediately active."""
        rel = factories.RelationshipFactory.create()
        form = forms.InviteFamilyForm(
            self.data(contact='+13216540987'), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert profile.user.is_active


    def test_user_with_phone_exists(self, sms, db):
        """If a user with given phone already exists, no new user is created."""
        elder = factories.ProfileFactory(phone='+13216541234')
        rel = factories.RelationshipFactory.create(
            from_profile__name="Teacher John",
            to_profile__name="Jimmy Doe",
            description="Math Teacher",
            )
        form = forms.InviteFamilyForm(
            self.data(phone=elder.phone),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert elder == profile
        assert len(sms.outbox) == 1
        assert sms.outbox[0].to == u'+13216541234'
        assert sms.outbox[0].body == (
            "Hi! Jimmy Doe's Math Teacher, Teacher John, "
            "will text you from this number. "
            "Text 'stop' any time if you don't want this."
            )


    def test_existing_user_new_role(self, db):
        """Inviting an existing elder with a new role doesn't change profile."""
        factories.ProfileFactory.create(
            phone='+13216541234', role="math teacher")
        rel = factories.RelationshipFactory()
        form = forms.InviteFamilyForm(
            self.data(
                phone='3216541234',
                role="science teacher",
                ),
            rel=rel,
            )
        assert form.is_valid(), dict(form.errors)
        p = form.save()

        assert p.role == u"math teacher"
        assert p.student_relationships[0].description == u"science teacher"


    def test_cannot_invite_to_second_student(self, sms, db):
        """For now, it's an error to add a family member to a 2nd village."""
        parent_rel = factories.RelationshipFactory(
            from_profile__phone='+13216541234')
        factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=parent_rel.student)
        teacher_rel = factories.RelationshipFactory.create()
        form = forms.InviteFamilyForm(
            self.data(phone=parent_rel.elder.phone),
            rel=teacher_rel,
            )
        assert not form.is_valid()

        assert form.errors['phone'] == [
            u"This person is already connected to a different student. "
            u"Portfoliyo doesn't support family members in multiple villages "
            u"yet, but we're working on it!"
            ]


    def test_can_invite_to_second_student_if_first_orphaned(self, sms, db):
        """A student w/ no teachers doesn't prevent invite to a new student."""
        parent_rel = factories.RelationshipFactory(
            from_profile__phone='+13216541234')
        teacher_rel = factories.RelationshipFactory.create()
        form = forms.InviteFamilyForm(
            self.data(phone=parent_rel.elder.phone),
            rel=teacher_rel,
            )
        assert form.is_valid()
        parent = form.save()

        # parent is removed from orphaned village and added to new one
        assert utils.deleted(parent_rel)
        assert parent in teacher_rel.student.elders


    def test_relationship_exists(self, db):
        """If existing family is already family for student, no error."""
        rel = factories.RelationshipFactory.create(
            from_profile__phone='+13214567890')
        form = forms.InviteFamilyForm(self.data(phone=rel.elder.phone), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert rel.elder == profile
        assert len(profile.students) == 1


    def test_group_relationship_exists(self, db):
        """If existing family is already elder via group, upgrades to direct."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(phone='+13214567890')
        group = factories.GroupFactory.create(owner=rel.elder)
        group.elders.add(elder)
        group.students.add(rel.student)
        form = forms.InviteFamilyForm(self.data(phone=elder.phone), rel=rel)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert elder == profile
        assert profile.student_relationships.get().direct



class TestStudentForms(object):
    def test_add_student(self, db):
        """Saves a student, given just name."""
        elder = factories.ProfileFactory.create()
        form = forms.AddStudentForm({'name': "Some Student"}, elder=elder)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()
        rel = profile.elder_relationships.get()

        assert profile.name == u"Some Student"
        assert profile.invited_by == elder
        assert list(profile.elders) == [elder]
        assert rel.elder == elder
        assert rel.student == profile
        assert rel.level == 'owner'


    def test_add_student_with_family(self, db):
        """Saves a student and adds a family member."""
        teacher = factories.ProfileFactory.create()
        phone = "+13216540987"
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'family-phone': phone,
                'family-role': "mother",
                },
            elder=teacher,
            )
        assert form.is_valid(), (
            dict(form.errors), dict(form.family_form.errors))
        profile = form.save()
        family = profile.elder_relationships.exclude(
            from_profile=teacher).get().elder

        assert set(profile.elders) == {teacher, family}
        assert family.phone == phone
        assert family.role == "mother"


    def test_add_student_with_family_that_already_has_student(self, db):
        """Can't add student with family that already has one (with teacher)."""
        teacher = factories.ProfileFactory.create()
        phone = "+13216540987"
        parent_rel = factories.RelationshipFactory.create(
            from_profile__phone=phone)
        # the student only prevents adding a new one if they have a teacher
        factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=parent_rel.student)
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'family-phone': phone,
                'family-role': "mother",
                },
            elder=teacher,
            )
        assert not form.is_valid()
        assert form.family_form.errors['phone'] == [
            u"This person is already connected to a different student. "
            u"Portfoliyo doesn't support family members in multiple "
            u"villages yet, but we're working on it!"
            ]


    def test_add_student_with_family_phone_required(self, db):
        """Phone field is required if either name or relationship is given."""
        teacher = factories.ProfileFactory.create()
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'family-name': "Some Parent",
                },
            elder=teacher,
            )
        assert not form.is_valid()
        assert form.family_form.errors['phone'] == [
            u"This field is required."]


    def test_add_student_strips_whitespace(self, db):
        """Leading and trailing whitespace are stripped from student name."""
        elder = factories.ProfileFactory.create()
        form = forms.AddStudentForm({'name': "  Some Student\t"}, elder=elder)
        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert profile.name == u"Some Student"


    def test_add_student_sends_pusher_event(self, db):
        """Adding a student sends a Pusher event."""
        elder = factories.ProfileFactory.create()
        form = forms.AddStudentForm({'name': "Some Student"}, elder=elder)
        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.student_added'
        with mock.patch(target) as mock_student_added:
            profile = form.save()

        mock_student_added.assert_called_with(profile.id, [elder.id])


    def test_add_student_in_group_context(self, db):
        """If group is passed in, prepopulate its checkbox."""
        rel = factories.RelationshipFactory.create()
        group = factories.GroupFactory.create(owner=rel.elder)

        form = forms.AddStudentForm(elder=rel.elder, group=group)

        assert form.fields['groups'].initial == [group.pk]


    def test_group_ids(self, db):
        """group_ids attr of each choice is list of group memberships."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        other_elder = factories.ProfileFactory.create(
            school=rel.elder.school, school_staff=True)
        factories.ProfileFactory.create(
            school=rel.elder.school, school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.elders.add(other_elder)

        form = forms.StudentForm(instance=other_elder, elder=rel.elder)

        # verifies that groups are prefetched, not checked per-elder
        with utils.assert_num_queries(2):
            elder_from_choice = [
                c[1] for c in form['elders'].field.choices
                if c[0] == other_elder.pk
                ][0]

        assert elder_from_choice.group_ids == [group.pk]


    def test_self_not_in_elder_choices(self, db):
        """The user viewing the form is not in the elder choices."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

        assert rel.elder not in form.fields['elders'].queryset


    def test_add_student_with_group_and_elder(self, db):
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


    def test_add_student_with_teacher_sends_notification(self, db):
        """Teacher added to new student is notified."""
        elder = factories.ProfileFactory.create()
        other_elder = factories.ProfileFactory.create(
            school=elder.school, school_staff=True)
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'elders': [other_elder.id],
                },
            elder=elder,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            profile = form.save()

        mock_record_notification.assert_called_once_with(
            'village_additions', elder, {other_elder}, [profile])


    def test_add_student_with_group_sends_notifications(self, db):
        """Teacher added via group to new student is notified."""
        group = factories.GroupFactory.create()
        other_elder = factories.ProfileFactory.create(
            school=group.owner.school, school_staff=True)
        group.elders.add(other_elder)
        form = forms.AddStudentForm(
            {
                'name': "Some Student",
                'groups': [group.id],
                },
            elder=group.owner,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            profile = form.save()

        assert mock_record_notification.call_count == 2
        mock_record_notification.assert_any_call(
            'village_additions', group.owner, set(), [profile])
        mock_record_notification.assert_any_call(
            'village_additions', group.owner, {other_elder}, [profile])


    def test_edit_student_with_other_school_elder(self, db):
        """Can preserve cross-school elder relationship."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        other_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            from_profile__school=factories.SchoolFactory.create(),
            to_profile=rel.student,
            )
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [other_rel.elder.pk],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {rel.elder, other_rel.elder}


    def test_no_dupes_in_elders_list(self, db):
        """List of elders to select does not contain dupes."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        rel2 = factories.RelationshipFactory.create(
            from_profile__name='A',
            from_profile__school_staff=True,
            from_profile__school=rel1.elder.school,
            to_profile=rel1.student,
            )
        rel3 = factories.RelationshipFactory.create(
            from_profile__name='B',
            from_profile__school_staff=True,
            school=rel1.elder.school,
            )
        factories.RelationshipFactory.create(
            from_profile=rel1.elder,
            to_profile=rel3.student)
        factories.RelationshipFactory.create(
            from_profile=rel2.elder,
            to_profile=rel3.student)

        form = forms.StudentForm(instance=rel1.student, elder=rel1.elder)

        assert list(form.fields['elders'].queryset) == [rel2.elder, rel3.elder]


    def test_family_not_listed(self, db):
        """Only school staff listed in elders list."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        parent_rel = factories.RelationshipFactory.create(
            to_profile=rel.student, from_profile__school_staff=False)

        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

        assert parent_rel.elder not in set(form.fields['elders'].queryset)


    def test_edit_student_does_not_remove_parent(self, db):
        """Editing student doesn't remove parent relationships."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        parent_rel = factories.RelationshipFactory.create(
            to_profile=rel.student, from_profile__school_staff=False)
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {rel.elder, parent_rel.elder}


    def test_edit_student_cannot_remove_owner(self, db):
        """Editing student cannot remove owners."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        owner_rel = factories.RelationshipFactory.create(
            to_profile=rel.student,
            from_profile__school_staff=True,
            level='owner',
            )
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.elders) == {rel.elder, owner_rel.elder}


    def test_edit_student_with_group_and_elder(self, db):
        """Can (de/)associate a student with a group/elder while editing."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=rel.student)
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


    def test_remove_elder_sends_pusher_event(self, db):
        """Removing an elder from a student sends a pusher event."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        other_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=rel.student)
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.student_removed'
        with mock.patch(target) as mock_student_removed:
            profile = form.save()

        mock_student_removed.assert_called_with(profile.id, [other_rel.elder.id])


    def test_edit_student_sends_pusher_event(self, db):
        """Editing a student sends a pusher event to all their elders."""
        rel = factories.RelationshipFactory.create()
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.student_edited'
        with mock.patch(target) as mock_student_edited:
            profile = form.save()

        mock_student_edited.assert_called_with(profile.id)


    def test_edit_student_only_sends_event_if_name_changed(self, db):
        """Sends pusher event only  if name changed."""
        rel = factories.RelationshipFactory.create(
            to_profile__name="Some Student")
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.student_edited'
        with mock.patch(target) as mock_student_edited:
            form.save()

        assert not mock_student_edited.call_count


    def test_edit_student_never_removes_from_others_groups(self, db):
        """Editing a student never removes them from others' groups."""
        rel = factories.RelationshipFactory.create()
        group1 = factories.GroupFactory.create(owner=rel.elder)
        group2 = factories.GroupFactory.create()
        rel.student.student_in_groups.add(group1, group2)

        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        profile = form.save()

        assert set(profile.student_in_groups.all()) == {group2}


    def test_edit_student_transforms_group_rel_to_direct(self, db):
        """Can add a direct relationship where there was a group one."""
        rel = factories.RelationshipFactory.create()
        other_elder = factories.ProfileFactory.create(
            school=rel.elder.school, school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)
        group.elders.add(other_elder)

        form = forms.StudentForm(
            {
                'name': "Some Student",
                'elders': [other_elder.pk],
                'groups': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        form.save()

        rel = other_elder.student_relationships[0]
        assert rel.direct
        assert not rel.groups.exists()


    def test_edit_student_transforms_direct_rel_to_group(self, db):
        """
        Can add a group relationship where there was a direct one.

        (Without deleting and recreating a new relationship, which would cause
        clients to get student_removed then student_added events in quick
        succession.)

        """
        rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            to_profile=rel.student,
            )
        group = factories.GroupFactory.create(owner=rel.elder)
        group.elders.add(other_rel.elder)

        form = forms.StudentForm(
            {
                'name': "Some Student",
                'elders': [],
                'groups': [group.pk],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        form.save()

        # If we deleted and created a new relationship, this would fail
        other_rel = utils.refresh(other_rel)
        assert not other_rel.direct
        assert set(other_rel.groups.all()) == {group}


    def test_edit_form_group_and_elder_initial(self, db):
        """Group and elder initial values set correctly when editing student."""
        rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student, from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

        assert form.fields['elders'].initial == [other_rel.elder.pk]
        assert form.fields['groups'].initial == [group.pk]


    def test_edit_student_add_elder(self, db):
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


    def test_edit_student_add_elder_sends_notification(self, db):
        """Associating a student with a new teacher sends notification."""
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
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        mock_record_notification.assert_called_once_with(
            'village_additions', rel.elder, {new_elder}, [rel.student])


    def test_edit_student_add_group_sends_notification(self, db):
        """Associating a student with new elder via group sends notification."""
        rel = factories.RelationshipFactory.create()
        new_elder = factories.ProfileFactory(
            school=rel.elder.school, school_staff=True)
        other_new_rel = factories.RelationshipFactory(
            to_profile=rel.student, from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.elders.add(new_elder, other_new_rel.elder)
        form = forms.StudentForm(
            {
                'name': "Some Student",
                'groups': [group.pk],
                'elders': [],
                },
            instance=rel.student,
            elder=rel.elder,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        assert mock_record_notification.call_count == 2
        mock_record_notification.assert_any_call(
            'village_additions', rel.elder, set(), [rel.student])
        mock_record_notification.assert_any_call(
            'village_additions', rel.elder, {new_elder}, [rel.student])


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


    def test_cannot_associate_elder_from_other_school(self, db):
        """Cannot associate student with an elder from a different school."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(school_staff=True)

        self._assert_cannot_add(rel, elder)


    def test_cannot_associate_non_school_staff_elder(self, db):
        """Cannot associate student with a non-staff elder."""
        rel = factories.RelationshipFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=False, school=rel.elder.school)

        self._assert_cannot_add(rel, elder)


    def test_cannot_associate_group_from_other_owner(self, db):
        """Cannot associate student with a group that isn't yours."""
        rel = factories.RelationshipFactory.create()
        group = factories.GroupFactory.create()

        self._assert_cannot_add(rel, group)


    def test_add_two_students_same_name(self, db):
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
    def test_create_group_with_students_and_elders(self, db):
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


    def test_create_group_sends_notifications(self, db):
        """Sends added-to-village notification for every student/elder combo."""
        me = factories.ProfileFactory.create(school_staff=True)
        elder = factories.ProfileFactory.create(
            school_staff=True, school=me.school)
        rel = factories.RelationshipFactory.create(from_profile=me)
        other_elder_rel = factories.RelationshipFactory.create(
            to_profile=rel.student, from_profile__school_staff=True)

        form = forms.AddGroupForm(
            {
                'name': 'New Group',
                'elders': [elder.pk, other_elder_rel.elder.pk],
                'students': [rel.student.pk],
                },
            owner=me,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        # no notification for other_elder_rel.elder, because they already had a
        # relationship with student
        mock_record_notification.assert_called_once_with(
            'village_additions', me, {elder}, [rel.student])


    def test_edit_group_with_students_and_elders(self, db):
        """Can add/remove students and elders from group when editing."""
        group = factories.GroupFactory.create()
        prev_elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        rel = factories.RelationshipFactory.create(from_profile=group.owner)
        group.students.add(rel.student)
        group.elders.add(prev_elder)

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


    def test_edit_group_sends_notifications(self, db):
        """Sends notifications to new student/elder combos."""
        group = factories.GroupFactory.create()
        prev_elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        rel = factories.RelationshipFactory.create(from_profile=group.owner)
        group.students.add(rel.student)
        group.elders.add(prev_elder)

        form = forms.GroupForm(
            {
                'name': 'New Name',
                'elders': [elder.pk],
                'students': [rel.student.pk],
                },
            instance=group,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.tasks.record_notification.delay'
        with mock.patch(target) as mock_record_notification:
            form.save()

        mock_record_notification.assert_called_once_with(
            'village_additions', group.owner, {elder}, [rel.student])


    def test_edit_group_with_cross_school_elder(self, db):
        """Can preserve cross-school elder group membership."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=True, school=factories.SchoolFactory.create())
        group.elders.add(elder)

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

        assert set(group.elders.all()) == {elder}


    def test_can_preserve_parent_membership(self, db):
        """Can preserve non-school-staff elder group membership."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=False, school=group.owner.school)
        group.elders.add(elder)

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

        assert set(group.elders.all()) == {elder}


    def test_no_dupes_in_elders_list(self, db):
        """List of elders to select does not contain dupes."""
        me = factories.ProfileFactory.create(school_staff=True)
        g1 = factories.GroupFactory.create(owner=me)
        g2 = factories.GroupFactory.create(owner=me)
        elder = factories.ProfileFactory.create(
            school_staff=True, school=me.school)
        elder.elder_in_groups.add(g1, g2)

        form = forms.GroupForm(instance=g1)

        assert list(form.fields['elders'].queryset) == [elder]


    def test_edit_group_does_not_delete_and_recreate_relationships(self, db):
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)
        rel = factories.RelationshipFactory.create(from_profile=group.owner)
        group.elders.add(elder.pk)
        group.students.add(rel.student)
        group_rel = group.relationships.get()

        form = forms.GroupForm(
            {
                'name': 'New Name',
                'elders': [elder.pk],
                'students': [rel.student.pk],
                },
            instance=group,
            )

        assert form.is_valid(), dict(form.errors)
        group = form.save()

        # this will fail if the group relationship was deleted/recreated
        utils.refresh(group_rel)


    def test_edit_group_fires_event(self, db):
        """Editing a group's name fires a Pusher event."""
        group = factories.GroupFactory.create(name='Old name')

        form = forms.GroupForm(
            {
                'name': 'New Name',
                'elders': [],
                'students': [],
                },
            instance=group,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.group_edited'
        with mock.patch(target) as mock_group_edited:
            group = form.save()

        mock_group_edited.assert_called_with(group.id, group.owner.id)


    def test_edit_group_fires_event_only_if_name_changed(self, db):
        """Editing a group without changing name does not fire event."""
        group = factories.GroupFactory.create(name='A name')

        form = forms.GroupForm(
            {
                'name': group.name,
                'elders': [],
                'students': [],
                },
            instance=group,
            )

        assert form.is_valid(), dict(form.errors)
        target = 'portfoliyo.pusher.events.group_edited'
        with mock.patch(target) as mock_group_edited:
            group = form.save()

        assert not mock_group_edited.call_count


    def test_self_not_in_elder_choices(self, db):
        """The user viewing the form is not in the elder choices."""
        group = factories.GroupFactory.create(owner__school_staff=True)

        form = forms.GroupForm(instance=group)

        assert group.owner not in form.fields['elders'].queryset


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


    def test_cannot_add_elder_from_other_school(self, db):
        """Cannot add an elder from a different school to a group."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(school_staff=True)

        self._assert_cannot_add(group, elder=elder)


    def test_cannot_add_non_staff_elder(self, db):
        """Cannot add an elder who is not school staff."""
        group = factories.GroupFactory.create()
        elder = factories.ProfileFactory.create(
            school_staff=False, school=group.owner.school)

        self._assert_cannot_add(group, elder=elder)


    def test_cannot_add_unrelated_student(self, db):
        """Cannot add a student you aren't related to to a group."""
        group = factories.GroupFactory.create()
        student = factories.ProfileFactory.create()

        self._assert_cannot_add(group, student=student)
