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
        assert form.is_valid()
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
        assert form.is_valid()
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
        assert form.is_valid()
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
        assert form.is_valid()
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
        assert form.is_valid()
        rel = factories.RelationshipFactory()
        profile = form.save(mock.Mock(), rel)

        assert not profile.user.is_active


    def test_phone_user_active(self):
        """User invited by phone is immediately active."""
        form = forms.InviteElderForm(self.data(contact='+13216540987'))
        assert form.is_valid()
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
        assert form.is_valid()
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile


    def test_user_with_phone_exists(self):
        """If a user with given phone already exists, no new user is created."""
        elder = factories.ProfileFactory(phone='+13214567890')
        form = forms.InviteElderForm(self.data(contact='321.456.7890'))
        assert form.is_valid()
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile


    def test_update_existing_elder_to_staff(self):
        """If a non-staff is added as staff elder, they gain staff status."""
        elder = factories.ProfileFactory(
            school_staff=False, phone='+13214567890')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, school_staff=True))
        assert form.is_valid()
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert profile.school_staff


    def test_update_existing_elder_role(self):
        """If existing elder has no role, update from new relationship."""
        elder = factories.ProfileFactory(role='', phone='+13214567890')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, relationship='foo'))
        assert form.is_valid()
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
        assert form.is_valid()
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert profile.role == u'something'


    def test_existing_elder_needs_no_update(self):
        """If existing elder has role and is not to be staff, no update done."""
        elder = factories.ProfileFactory(phone='+13214567890', role='foo')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, school_staff=False))
        assert form.is_valid()
        profile = form.save(None, factories.RelationshipFactory())

        assert elder == profile
        assert not profile.school_staff
        assert profile.role == 'foo'


    def test_relationship_exists(self):
        """If existing elder is already elder for student, no error."""
        rel = factories.RelationshipFactory(from_profile__phone='+13214567890')
        form = forms.InviteElderForm(self.data(contact=rel.elder.phone))
        assert form.is_valid()
        profile = form.save(None, rel)

        assert rel.elder == profile
        assert len(profile.students) == 1



class TestAddStudentForm(object):
    """Tests for AddStudentForm."""
    def test_add_student(self):
        """Saves a student, given just name."""
        elder = factories.ProfileFactory()
        form = forms.AddStudentForm({'name': "Some Student"})
        assert form.is_valid()
        profile, rel = form.save(elder)

        assert profile.name == u"Some Student"
        assert profile.invited_by == elder
        assert profile.elders == [elder]
        assert rel.elder == elder
        assert rel.student == profile


    def test_add_two_students_same_name(self):
        """Adding two students with same name causes no username trouble."""
        form = forms.AddStudentForm({'name': "Some Student"})
        assert form.is_valid()
        profile1, rel1 = form.save(factories.ProfileFactory())

        form = forms.AddStudentForm({'name': "Some Student"})
        assert form.is_valid()
        profile2, rel2 = form.save(factories.ProfileFactory())

        assert profile1 != profile2
