"""Test hooks and funcarg resources."""
import django_webtest

from tests import client
from tests.users import factories



def pytest_funcarg__client(request):
    """Give a test access to a WebTest client for integration-testing views."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    return client.TestClient()



def pytest_funcarg__admin(request):
    """Give a test an admin-enabled superuser."""
    return factories.UserFactory.create(is_staff=True, is_superuser=True)
