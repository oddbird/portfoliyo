"""Tests for user-related forms."""
from django.test.utils import override_settings

from portfoliyo.tests import factories, utils
from portfoliyo.view.users import forms


class TestRegistrationForm(object):
    """Tests for RegistrationForm."""
    base_data = {
        'name': 'Some Body',
        'email': 'some@example.com',
        'password': 'sekrit',
        'password_confirm': 'sekrit',
        'role': 'Some Role',
        'country_code': 'us',
        }


    def test_register(self, db):
        """Registration creates active school_staff w/ unconfirmed email."""
        form = forms.RegistrationForm(self.base_data.copy())

        assert form.is_valid()
        profile = form.save()
        assert not profile.email_confirmed
        assert profile.school_staff
        assert profile.user.is_active
        assert profile.country_code == 'us'


    def test_source_phone(self, db):
        """Source phone is set according to country code."""
        data = self.base_data.copy()
        data['country_code'] = 'ca'
        ca_phone = '+13216543987'
        with override_settings(PORTFOLIYO_NUMBERS={'ca': ca_phone}):
            form = forms.RegistrationForm(data)
            assert form.is_valid()
            profile = form.save()

        assert profile.country_code == 'ca'
        assert profile.source_phone == ca_phone


    def test_unmatched_passwords(self, db):
        """Registration form not valid if passwords don't match."""
        data = self.base_data.copy()
        data['password'] = 'other-sekrit'
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert form.errors['__all__'] == [u"The passwords didn't match."]


    def test_dupe_email(self, db):
        """Registration form not valid if email already in use."""
        factories.UserFactory.create(email='some@example.com')
        form = forms.RegistrationForm(self.base_data.copy())

        assert not form.is_valid()
        assert form.errors['email'] == [
            u"This email address is already in use. "
            u"Please supply a different email address."
            ]


    def test_no_school(self, db):
        """If no school selected, create one (with user's country)."""
        data = self.base_data.copy()
        data['country_code'] = 'ca'
        form = forms.RegistrationForm(data)

        assert form.is_valid()
        profile = form.save()
        school = profile.school
        assert school.auto
        assert not school.postcode
        assert school.country_code == 'ca'



class TestEditProfileForm(object):
    def test_update_relationships(self, db):
        """
        Updating role updates matching relationship descriptions to empty.

        If I have my role set in my profile as 'foo' and I change it to 'bar',
        any relationships where I am the elder and the relationship description
        is 'foo' will be updated to '' (which falls back to profile role).

        """
        rel1 = factories.RelationshipFactory.create(
            description='foo', from_profile__role='foo')
        rel2 = factories.RelationshipFactory.create(
            description='bar', from_profile=rel1.elder)

        form = forms.EditProfileForm(
            {'name': 'New', 'role': 'new'}, instance=rel1.elder)
        assert form.is_valid()
        form.save()

        rel1 = utils.refresh(rel1)
        rel2 = utils.refresh(rel2)

        assert rel1.description == ''
        assert rel2.description == 'bar'
