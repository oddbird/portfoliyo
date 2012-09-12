"""Test hooks and funcarg resources."""
import django_webtest



def pytest_funcarg__client(request):
    """Give a test access to a WebTest client for integration-testing views."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from tests import client
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    return client.TestClient()
