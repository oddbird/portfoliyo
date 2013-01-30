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

    # any test using the web client automatically gets db, redis, cache
    request.getfuncargvalue('redis')
    request.getfuncargvalue('db')
    request.getfuncargvalue('cache')

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

    # any test using the web client automatically gets db, redis, cache
    request.getfuncargvalue('redis')
    request.getfuncargvalue('db')
    request.getfuncargvalue('cache')

    return client.TestClient()



class FakeSMSMessage(object):
    """A fake SMSMessage object for collecting sent SMSes in tests."""
    def __init__(self, to, from_, body):
        self.to = to
        self.from_ = from_
        self.body = body



@pytest.fixture
def sms(request, monkeypatch):
    """Monkeypatch SMS backend to collect messages for test inspection."""
    from portfoliyo.sms import base
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
    client.num_calls = 0
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

    # patch a real redis client to track number of calls
    if not isinstance(redis.client, redis.InMemoryRedis):
        def _tracked_send_packed_command(self, command):
            self.num_calls += 1
            return self._orig_send_packed(command)
        redis.client._orig_send_packed = client.send_packed_command
        redis.client.send_packed_command = _tracked_send_packed_command

    redis._orig_client = redis.client
    redis._disabled_client = DisabledRedis()
    redis.client = redis._disabled_client

    def _restore_redis():
        redis.client = redis._orig_client
        if hasattr(client, '_orig_send_packed'):
            redis.client.send_packed_command = redis.client._orig_send_packed
            del redis.client._orig_send_packed
        del redis._orig_client

    request.addfinalizer(_restore_redis)



@pytest.fixture
def cache(request):
    """Clear cache and give test access to it."""
    from django.core import cache
    from django.core.cache.backends.locmem import LocMemCache
    c = cache._orig_cache
    cache.cache = cache._orig_cache
    def _disable_cache():
        cache.cache = cache._disabled_cache
    request.addfinalizer(_disable_cache)
    if isinstance(c, LocMemCache):
        c.clear()
    else:
        raise ValueError(
            "Tests can only be run with the locmem cache backend."
            )

    return c



class DisabledCache(object):
    def _error(self):
        raise ValueError(
            "Tests cannot access cache unless the 'cache' fixture is used.")

    def __getattr__(self, attr):
        self._error()

    def __getitem__(self, key):
        self._error()



@pytest.fixture(scope='session', autouse=True)
def _disable_cache(request):
    """Disable cache by default (use cache fixture to enable for a test)."""
    from django.core import cache
    cache._orig_cache = cache.cache
    cache._disabled_cache = DisabledCache()
    cache.cache = cache._disabled_cache
    def _restore_cache():
        cache.cache = cache._orig_cache
        del cache._orig_cache
    request.addfinalizer(_restore_cache)



@pytest.fixture(autouse=True)
def _celery_transaction_task_helper(request):
    """
    If running tests in a DB transaction, tell Celery to pretend there's none.

    Our Celery tasks are delayed until the end of a DB transaction, and
    discarded if the transaction is rolled back. But many of our tests are run
    using the `db` fixture, which runs every test within a transaction and
    always rolls the transaction back at the end of the test (so the database
    is clear for the next test). The effect of this is that tasks are never run
    in many tests.

    So if a test is using the `db` fixture, we temporarily monkeypatch Celery
    to tell it to pretend there is no transaction in progress, so it will apply
    the task immediately.

    This still allows us to have some tests use the `transactional_db` fixture
    instead (where tests are not run in a transaction, and the database is
    wiped manually instead of via rollback) and fully test the
    transactional/delayed behavior of our Celery tasks.

    """
    if 'db' in request.funcargnames:
        from portfoliyo import celery
        celery._original_in_transaction = celery._in_transaction
        celery._in_transaction = lambda: False
        def _restore():
            celery._in_transaction = celery._original_in_transaction
        request.addfinalizer(_restore)
