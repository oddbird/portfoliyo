"""
Tests for custom django-registration backend.

"""
from django.core import mail
import mock

from portfoliyo.tests import factories
from portfoliyo.view.users import forms, register



def test_get_form_class():
    """get_form_class method returns our RegistrationForm class."""
    backend = register.RegistrationBackend()
    assert backend.get_form_class(None) is forms.RegistrationForm



def _register(**kwargs):
    """
    Utility function to call RegistrationBackend().register(...).

    Fills in required keyword arguments with defaults if not given.

    """
    backend = register.RegistrationBackend()
    request = mock.Mock()
    request.get_host.return_value = 'example.com'
    if 'school' not in kwargs:
        kwargs['school'] = factories.SchoolFactory.create()
    kwargs.setdefault('name', 'Some Name')
    kwargs.setdefault('email', 'some@example.com')
    kwargs.setdefault('password', 'sekrit')
    kwargs.setdefault('role', 'Role')
    return backend.register(request, **kwargs)



def test_register_creates_inactive_user():
    """register method creates inactive user."""
    user = _register()

    assert not user.is_active


def test_register_sets_password():
    """register method sets password on user correctly."""
    user = _register(password='foo')

    assert user.check_password('foo')


def test_register_sets_email():
    """register method sets email on user."""
    user = _register(email='foo@example.com')

    assert user.email == u'foo@example.com'


def test_register_creates_profile():
    """register method creates a profile."""
    user = _register(name='Foo', role='Bar')

    assert user.profile.name == u'Foo'
    assert user.profile.role == u'Bar'


def test_register_creates_school_staff():
    """A newly-registered user is marked as school staff."""
    user = _register()

    assert user.profile.school_staff


def test_register_creates_code():
    """A newly-registered user has a unique code."""
    user = _register()

    assert user.profile.code


def test_register_creates_registration_profile():
    """register method creates RegistrationProfile."""
    user = _register()

    assert user.registrationprofile_set.count() == 1


def test_register_sends_email():
    """register method sends email to new user."""
    _register(email='foo@example.com')

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [u'foo@example.com']


def test_register_saves_school():
    """register method saves unsaved school."""
    s = factories.SchoolFactory.build(name='Foo')
    _register(school=s)

    assert s.__class__.objects.filter(name='Foo').count() == 1
