"""Tests for custom auth backend."""
from portfoliyo.users import auth_backend

from tests.users import factories
from tests import utils


def test_authenticate_failure():
    """authenticate method returns None if no matching user."""
    backend = auth_backend.EmailBackend()
    user = backend.authenticate(username='foo', password='bar')

    assert user is None


def test_authenticate_select_related():
    """authenticate method returns user with profile pre-selected."""
    factories.UserFactory.create(email='test@example.com', password='testpw')
    backend = auth_backend.EmailBackend()
    user = backend.authenticate(username='test@example.com', password='testpw')

    with utils.assert_num_queries(0):
        user.profile


def test_get_user_select_related():
    """get_user method returns user with profile pre-selected."""
    user = factories.UserFactory.create()
    backend = auth_backend.EmailBackend()
    user = backend.get_user(user.id)

    with utils.assert_num_queries(0):
        user.profile


def test_get_user_nonexistent():
    """get_user method returns None if no matching user."""
    backend = auth_backend.EmailBackend()
    user = backend.get_user(999)

    assert user is None
