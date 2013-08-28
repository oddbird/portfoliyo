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
        'terms_confirm': '1',
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


    def test_must_accept_terms(self, db):
        """Registration requires accepting terms of service."""
        data = self.base_data.copy()
        del data['terms_confirm']
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert form.errors == {'terms_confirm': [u"This field is required."]}


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


    def test_add_school(self, db):
        """If addschool is True, create a new school and use it."""
        data = self.base_data.copy()
        data['addschool'] = '1'
        data['addschool-name'] = "New School"
        data['addschool-postcode'] = "12345"
        form = forms.RegistrationForm(data)

        assert form.is_valid()
        profile = form.save()
        school = profile.school
        assert school.name == u"New School"
        assert school.postcode == u"12345"


    def test_add_school_takes_user_country(self, db):
        """New school takes country of new user."""
        data = self.base_data.copy()
        data['country_code'] = 'ca'
        data['addschool'] = '1'
        data['addschool-name'] = "New School"
        data['addschool-postcode'] = "12345"
        form = forms.RegistrationForm(data)

        assert form.is_valid()
        profile = form.save()
        school = profile.school
        assert school.country_code == 'ca'


    def test_add_school_validation_error(self, db):
        """If addschool is True but fields not complete, validation error."""
        data = self.base_data.copy()
        data['addschool'] = 'True'
        data['addschool-name'] = "New School"
        data['addschool-postcode'] = ""
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert form.errors['__all__'] == [u"Could not add a school."]
        assert form.addschool_form.errors['postcode'] == [
            u"This field is required."]


    def test_no_addschool_validation_error_if_addschool_false(self, db):
        """If addschool is False, addschool form not bound."""
        data = self.base_data.copy()
        data['addschool'] = 'False'
        data['email'] = 'not a valid email'
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert not form.addschool_form.is_bound


    def test_no_school(self, db):
        """If no school selected, create one."""
        form = forms.RegistrationForm(self.base_data.copy())

        assert form.is_valid()
        profile = form.save()
        school = profile.school
        assert school.auto
        assert not school.postcode


    def test_add_dupe_school(self, db):
        """No integrity error on school-creation race condition."""
        data = self.base_data.copy()
        data['addschool'] = '1'
        data['addschool-name'] = "My School"
        data['addschool-postcode'] = "12345"
        form = forms.RegistrationForm(data)

        assert form.is_valid()

        school = factories.SchoolFactory.create(
            name="My School",
            postcode="12345",
            )

        profile = form.save()
        assert profile.school == school



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
