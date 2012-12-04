"""Tests for custom auth backend."""
from portfoliyo.model.users import auth_backend

from portfoliyo.tests import factories, utils


def test_authenticate_failure(db):
    """authenticate method returns None if no matching user."""
    backend = auth_backend.EmailBackend()
    user = backend.authenticate(username='foo', password='bar')

    assert user is None


def test_authenticate_select_related(db):
    """authenticate method returns user with profile pre-selected."""
    factories.ProfileFactory.create(
        user__email='test@example.com', user__password='testpw')
    backend = auth_backend.EmailBackend()
    user = backend.authenticate(username='test@example.com', password='testpw')

    with utils.assert_num_queries(0):
        user.profile


def test_get_user_select_related(db):
    """get_user method returns user with profile pre-selected."""
    profile = factories.ProfileFactory.create()
    backend = auth_backend.EmailBackend()
    user = backend.get_user(profile.user.id)

    with utils.assert_num_queries(0):
        user.profile


def test_get_user_nonexistent(db):
    """get_user method returns None if no matching user."""
    backend = auth_backend.EmailBackend()
    user = backend.get_user(999)

    assert user is None


def test_legacy_import():
    """Can still import from legacy location."""
    from portfoliyo.users.auth_backend import EmailBackend
