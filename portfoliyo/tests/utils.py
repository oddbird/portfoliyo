"""Test utilities."""
from contextlib import contextmanager

from django.db import connection
from django.test.testcases import _AssertNumQueriesContext
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



def refresh(obj):
    """Refresh a model instance from the database."""
    return obj.__class__._base_manager.get(pk=obj.pk)



def deleted(obj):
    """Return True if given obj has been deleted."""
    return not obj.__class__._base_manager.filter(pk=obj.pk).exists()



class FakeTestCase(object):
    """
    Fake TestCase class with an assertEqual implementation.

    Necessary because _AssertNumQueriesContext requires such an object passed
    in as an instantiation argument.

    """
    def assertEqual(self, one, two, message):
        """Assert that ``one`` and ``two`` are equal, else print ``message``"""
        assert one == two, message



def assert_num_queries(num):
    """Context manager: assert ``num`` queries occur within block."""
    return _AssertNumQueriesContext(FakeTestCase(), num, connection)


@contextmanager
def assert_num_calls(redis, num):
    """Context manager: assert ``num`` redis queries occur within block."""
    start_calls = redis.num_calls
    yield
    total_calls = redis.num_calls - start_calls
    assert total_calls == num, 'Expected %s redis quer%s, saw %s' % (
        num, 'y' if num == 1 else 'ies', total_calls)
