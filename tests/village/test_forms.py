"""Tests for village forms."""
from portfoliyo.village import forms

from tests.users import factories



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


    def test_phone_contact(self):
        """If contact field is phone, it's normalized and saved to profile."""
        form = forms.InviteElderForm(self.data(contact='(123)456-7890'))
        assert form.is_valid()
        profile = form.save(factories.ProfileFactory())

        assert profile.phone == u'123-456-7890'


    def test_email_contact(self):
        """If contact field is email, it's normalized and saved to profile."""
        form = forms.InviteElderForm(self.data(contact='bar@EXAMPLE.com'))
        assert form.is_valid()
        profile = form.save(factories.ProfileFactory())

        assert profile.user.email == u'bar@example.com'


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
        profile = form.save(factories.ProfileFactory())

        assert elder == profile


    def test_user_with_phone_exists(self):
        """If a user with given phone already exists, no new user is created."""
        elder = factories.ProfileFactory(phone='123-456-7890')
        form = forms.InviteElderForm(self.data(contact='123.456.7890'))
        assert form.is_valid()
        profile = form.save(factories.ProfileFactory())

        assert elder == profile


    def test_update_existing_elder_to_staff(self):
        """If a non-staff is added as staff elder, they gain staff status."""
        elder = factories.ProfileFactory(school_staff=False)
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, school_staff=True))
        assert form.is_valid()
        profile = form.save(factories.ProfileFactory())

        assert elder == profile
        assert profile.school_staff


    def test_update_existing_elder_role(self):
        """If existing elder has no role, update from new relationship."""
        elder = factories.ProfileFactory(role='')
        form = forms.InviteElderForm(
            self.data(contact=elder.phone, relationship='foo'))
        assert form.is_valid()
        profile = form.save(factories.ProfileFactory())

        assert elder == profile
        assert profile.role == u'foo'


    def test_relationship_exists(self):
        """If existing elder is already elder for student, no error."""
        rel = factories.RelationshipFactory()
        form = forms.InviteElderForm(self.data(contact=rel.elder.phone))
        assert form.is_valid()
        profile = form.save(rel.student)

        assert rel.elder == profile
        assert len(profile.students) == 1
