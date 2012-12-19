"""Test hooks and fixture resources."""
import pytest



@pytest.fixture
def client(request):
    """Give a test access to a WebTest client for integration-testing views."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    import django_webtest
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    # any test using the web client automatically gets db and redis
    request.getfuncargvalue('redis')
    request.getfuncargvalue('db')

    return client.TestClient()



@pytest.fixture
def no_csrf_client(request):
    """Give a test access to a CSRF-exempt WebTest client."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    import django_webtest
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase.csrf_checks = False
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    # any test using the web client automatically gets db and redis
    request.getfuncargvalue('redis')
    request.getfuncargvalue('db')

    return client.TestClient()



class FakeSMSMessage(object):
    """A fake SMSMessage object for collecting sent SMSes in tests."""
    def __init__(self, to, from_, body):
        self.to = to
        self.from_ = from_
        self.body = body



@pytest.fixture
def sms(request):
    """Monkeypatch SMS backend to collect messages for test inspection."""
    from portfoliyo.sms import base
    monkeypatch = request.getfuncargvalue('monkeypatch')
    base.backend.outbox = []
    def replacement_send(*a, **kw):
        base.backend.outbox.append(FakeSMSMessage(*a, **kw))
    monkeypatch.setattr(base.backend, 'send', replacement_send)
    return base.backend


@pytest.fixture
def redis(request):
    """Clear Redis and give test access to redis client."""
    from django.conf import settings
    from portfoliyo import redis
    client = redis._orig_client
    redis.client = client
    def _disable_redis():
        redis.client = redis._disabled_client
    request.addfinalizer(_disable_redis)
    if isinstance(client, redis.InMemoryRedis):
        client.data = {}
        client.expiry = {}
    else:
        if getattr(settings, 'TEST_DESTROY_REDIS_DATA', False):
            client.flushdb()
        else:
            raise ValueError(
                "To run tests with a real Redis, you must set the "
                "TEST_DESTROY_REDIS_DATA setting to True. "
                "All data in the db at REDIS_URL will be destroyed."
                )

    return client



class DisabledRedis(object):
    def __getattr__(self, attr):
        raise ValueError(
            "Tests cannot access redis unless the 'redis' fixture is used.")



@pytest.fixture(scope='session', autouse=True)
def _disable_redis(request):
    """Disable redis by default (use redis fixture to enable for a test)."""
    from portfoliyo import redis
    redis._orig_client = redis.client
    redis._disabled_client = DisabledRedis()
    redis.client = redis._disabled_client
    def _restore_redis():
        redis.client = redis._orig_client
        del redis._orig_client
    request.addfinalizer(_restore_redis)
