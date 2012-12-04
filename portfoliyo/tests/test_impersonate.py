"""Tests for impersonation middleware."""
import mock

from portfoliyo import impersonate
from portfoliyo.tests import factories


def _call(request):
    """Shortcut to pass request through middleware and get return value."""
    return impersonate.ImpersonationMiddleware().process_request(request)


def test_start_impersonating(db):
    """Can start impersonating a user with ?impersonate=email@example.com."""
    real_user = factories.UserFactory.create(is_superuser=True)
    user = factories.UserFactory.create(email="email@example.com")
    req = mock.Mock()
    req.user = real_user
    req.session = {}
    req.GET = {'impersonate': "email@example.com"}

    assert _call(req) is None
    assert req.session[impersonate.SESSION_KEY] == user.id
    assert req.user == user
    assert req.real_user == real_user


def test_cannot_start_if_not_superuser(db):
    """Cannot start impersonating a user unless you're a superuser."""
    real_user = factories.UserFactory.create(is_superuser=False)
    factories.UserFactory.create(email="email@example.com")
    req = mock.Mock()
    req.user = real_user
    req.session = {}
    req.GET = {'impersonate': "email@example.com"}

    assert _call(req) is None
    assert impersonate.SESSION_KEY not in req.session
    assert req.user == real_user


def test_continue_impersonating(db):
    """Can continue impersonating in same session."""
    real_user = factories.UserFactory.create(is_superuser=True)
    user = factories.UserFactory.create(email="email@example.com")
    req = mock.Mock()
    req.user = real_user
    req.session = {impersonate.SESSION_KEY: user.id}
    req.GET = {}

    assert _call(req) is None
    assert req.session[impersonate.SESSION_KEY] == user.id
    assert req.user == user
    assert req.real_user == real_user


def test_cannot_continue_impersonating_if_not_superuser(db):
    """Cannot impersonate using previous session if not superuser."""
    real_user = factories.UserFactory.create(is_superuser=False)
    user = factories.UserFactory.create(email="email@example.com")
    req = mock.Mock()
    req.user = real_user
    req.session = {impersonate.SESSION_KEY: user.id}
    req.GET = {}

    assert _call(req) is None
    assert req.session[impersonate.SESSION_KEY] == user.id
    assert req.user == real_user


def test_stop_impersonating(db):
    """Can stop impersonating with ?impersonate=stop."""
    real_user = factories.UserFactory.create(is_superuser=True)
    user = factories.UserFactory.create(email="email@example.com")
    req = mock.Mock()
    req.user = real_user
    req.session = {impersonate.SESSION_KEY: user.id}
    req.GET = {'impersonate': "stop"}

    assert _call(req) is None
    assert impersonate.SESSION_KEY not in req.session
    assert req.user == real_user


def test_stop_impersonating_again(db):
    """Trying to stop impersonating when you're not doesn't cause an error."""
    real_user = factories.UserFactory.create(is_superuser=True)
    req = mock.Mock()
    req.user = real_user
    req.session = {}
    req.GET = {'impersonate': "stop"}

    assert _call(req) is None
    assert impersonate.SESSION_KEY not in req.session
    assert req.user == real_user


def test_bad_email(db):
    """Returns simple error response if bad email is given."""
    real_user = factories.UserFactory.create(is_superuser=True)
    req = mock.Mock()
    req.user = real_user
    req.session = {}
    req.GET = {'impersonate': "email@example.com"}

    resp = _call(req)

    assert resp.content == (
        "Cannot impersonate email@example.com; user not found.")
    assert resp.status_code == 400


def test_no_error_if_not_superuser(db):
    """No error response if not a superuser."""
    real_user = factories.UserFactory.create(is_superuser=False)
    req = mock.Mock()
    req.user = real_user
    req.session = {}
    req.GET = {'impersonate': "email@example.com"}

    assert _call(req) is None
