"""Tests for admin."""
import mock

from portfoliyo.model.users import admin



def pytest_funcarg__pa(request):
    return admin.ProfileAdmin(admin.models.Profile, mock.Mock())



class TestProfileAdmin(object):
    def test_email(self, pa):
        email = 'foo@example.com'
        profile = mock.Mock()
        profile.user.email = email

        assert pa.email(profile) == email


    def test_save_model(self, pa):
        """Empty string in phone is converted to None."""
        profile = mock.Mock()
        profile.phone = ''
        pa.save_model(mock.Mock(), profile, mock.Mock(), mock.Mock())

        assert profile.phone is None



class TestUserChangeForm(object):
    def test_no_empty_string_email(self, db):
        form = admin.UserChangeForm(
            {
                'email': '',
                'username': 'foo',
                'last_login': '2012-11-12',
                'date_joined': '2012-11-10',
                },
            initial={'password': 'foo'},
            )

        assert form.is_valid(), dict(form.errors)
        assert form.cleaned_data['email'] is None



def pytest_funcarg__ua(request):
    return admin.UserAdmin(admin.auth_models.User, mock.Mock())



class TestUserAdmin(object):
    def test_name(self, ua):
        user = mock.Mock()
        user.profile.name = 'Foo'

        assert ua.name(user) == 'Foo'


    def test_name_no_profile(self, ua):
        class MockUser(object):
            @property
            def profile(self):
                raise admin.models.Profile.DoesNotExist

        assert ua.name(MockUser()) == '<no profile>'
