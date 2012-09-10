"""Test utilities."""
from contextlib import contextmanager
from mock import patch


@contextmanager
def patch_session(session_data):
    """Context manager to patch session vars."""
    with patch(
            "django.contrib.sessions.backends.cached_db."
            "SessionStore._session_cache",
            session_data,
            create=True):
        yield


def location(url_path):
    """Qualify a URL path with 'http://testserver' prefix."""
    return 'http://testserver' + url_path
