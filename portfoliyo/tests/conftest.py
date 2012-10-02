"""Test hooks and funcarg resources."""
import django_webtest



def pytest_runtest_setup(item):
    """Clear out Redis prior to each test."""
    from portfoliyo.redis import client
    client.flushdb()



def pytest_funcarg__client(request):
    """Give a test access to a WebTest client for integration-testing views."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    return client.TestClient()



def pytest_funcarg__no_csrf_client(request):
    """Give a test access to a CSRF-exempt WebTest client."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase.csrf_checks = False
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    return client.TestClient()



class FakeSMSMessage(object):
    """A fake SMSMessage object for collecting sent SMSes in tests."""
    def __init__(self, to, from_, body):
        self.to = to
        self.from_ = from_
        self.body = body



def pytest_funcarg__sms(request):
    """Monkeypatch SMS backend to collect messages for test inspection."""
    from portfoliyo.sms import base
    monkeypatch = request.getfuncargvalue('monkeypatch')
    base.backend.outbox = []
    def replacement_send(*a, **kw):
        base.backend.outbox.append(FakeSMSMessage(*a, **kw))
    monkeypatch.setattr(base.backend, 'send', replacement_send)
    return base.backend
