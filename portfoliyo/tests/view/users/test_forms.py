"""Tests for user-related forms."""
from portfoliyo.view.users import forms

from portfoliyo.tests import factories, utils


class TestRegistrationForm(object):
    """Tests for RegistrationForm."""
    base_data = {
        'name': 'Some Body',
        'email': 'some@example.com',
        'password': 'sekrit',
        'password_confirm': 'sekrit',
        'role': 'Some Role',
        }


    def test_unmatched_passwords(self):
        """Registration form not valid if passwords don't match."""
        data = self.base_data.copy()
        data['password'] = 'other-sekrit'
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert form.errors['__all__'] == [u"The passwords didn't match."]


    def test_dupe_email(self):
        """Registration form not valid if email already in use."""
        factories.UserFactory.create(email='some@example.com')
        form = forms.RegistrationForm(self.base_data.copy())

        assert not form.is_valid()
        assert form.errors['email'] == [
            u"This email address is already in use. "
            u"Please supply a different email address."
            ]


    def test_add_school(self):
        """If addschool is True, create a new school and use it."""
        data = self.base_data.copy()
        data['addschool'] = '1'
        data['addschool-name'] = "New School"
        data['addschool-postcode'] = "12345"
        form = forms.RegistrationForm(data)

        assert form.is_valid()
        school = form.cleaned_data['school']
        assert school.name == u"New School"
        assert school.postcode == u"12345"
        # don't save the school to DB on form validation, reg backend will
        assert school.id is None


    def test_add_school_validation_error(self):
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


    def test_no_addschool_validation_error_if_addschool_false(self):
        """If addschool is False, addschool form not bound."""
        data = self.base_data.copy()
        data['addschool'] = 'False'
        data['email'] = 'not a valid email'
        form = forms.RegistrationForm(data)

        assert not form.is_valid()
        assert not form.addschool_form.is_bound


    def test_no_school(self):
        """If no school selected, create one."""
        form = forms.RegistrationForm(self.base_data.copy())

        assert form.is_valid()
        school = form.cleaned_data['school']
        assert school.auto
        assert not school.postcode
        # don't save the school to DB on form validation, reg backend will
        assert school.id is None



class TestEditProfileForm(object):
    def test_update_relationships(self):
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
