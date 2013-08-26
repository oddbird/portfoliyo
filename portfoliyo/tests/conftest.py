"""Test hooks and fixture resources."""
import pytest



@pytest.fixture
def client(request, db, redis, cache):
    """Give a test access to a WebTest client for integration-testing views."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    import django_webtest
    webtestcase = django_webtest.WebTest("__init__")
    webtestcase._patch_settings()
    request.addfinalizer(webtestcase._unpatch_settings)

    return client.TestClient()



@pytest.fixture
def no_csrf_client(request, db, redis, cache):
    """Give a test access to a CSRF-exempt WebTest client."""
    # We don't use TestCase classes, but we instantiate the django_webtest
    # TestCase subclass to use its methods for patching/unpatching settings.
    from portfoliyo.tests import client
    import django_webtest
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



@pytest.fixture
def sms(request, monkeypatch):
    """Monkeypatch SMS backend to collect messages for test inspection."""
    from portfoliyo.sms import base
    base.backend.outbox = []
    def replacement_send(*a, **kw):
        base.backend.outbox.append(FakeSMSMessage(*a, **kw))
    monkeypatch.setattr(base.backend, 'send', replacement_send)
    return base.backend


def pytest_addoption(parser):
    parser.addoption(
        '--clobber-redis',
        action='store_true',
        help=(
            "Run tests against real Redis (clobbering data). "
            "Requires REDIS_URL setting."
            ),
        )


def pytest_generate_tests(metafunc):
    """
    Execute all Redis-using tests with both in-memory and real Redis.

    If real Redis is not available, execute them only using the in-memory fake
    Redis.

    """
    if 'redis' in metafunc.fixturenames:
        from django.conf import settings
        redis_types = ['fake']
        if metafunc.config.getoption('--clobber-redis'):
            if settings.REDIS_URL:
                redis_types.append('real')
            else:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured(
                    "--clobber-redis requires the REDIS_URL setting.")
        metafunc.parametrize('redis', redis_types, indirect=True)


@pytest.fixture
def redis(request):
    """
    Clear Redis and give test access to redis client.

    Uses the param passed in by ``pytest_generate_tests`` to decide whether to
    instantiate a real or fake Redis.

    """
    from portfoliyo import redis

    _disabled_client = redis.client
    redis_type = getattr(request, 'param', 'fake')
    if redis_type == 'real':
        # if we're using real Redis, _orig_client will be a real Redis client.
        # It's faster not to instantiate a new redis client for each test.
        client = redis._orig_client
        client.flushdb()
    else:
        client = redis.InMemoryRedis()

    redis.client = client
    client.num_calls = 0

    def _disable_redis():
        redis.client = _disabled_client
    request.addfinalizer(_disable_redis)

    return client


@pytest.fixture(scope='session', autouse=True)
def _redis_call_counts(request):
    """
    Patch the Redis client to track the number of server queries.

    In the case of pipelines, this makes the assumption that a given pipeline
    will only be executed once (and thus send a single query to the
    server). This is at least a correct assumption for our usage.

    """
    from redis import StrictRedis
    sr = StrictRedis
    def _tracked_execute_command(self, *args, **kw):
        self.num_calls += 1
        return self._orig_exec(*args, **kw)
    sr._orig_exec = sr.execute_command
    sr.execute_command = _tracked_execute_command
    # we assume a pipeline is only executed once; generally true
    def _tracked_pipeline(self, *args, **kw):
        self.num_calls += 1
        return self._orig_pipeline(*args, **kw)
    sr._orig_pipeline = sr.pipeline
    sr.pipeline = _tracked_pipeline
    sr.num_calls = 0

    def _unpatch():
        sr.execute_command = sr._orig_exec
        del sr._orig_exec
        sr.pipeline = sr._orig_pipeline
        del sr._orig_pipeline
        del sr.num_calls

    request.addfinalizer(_unpatch)



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



@pytest.fixture
def cache(request):
    """Enable the cache, clear it, and give test access to it."""
    from django.core.cache import cache
    _disabled_class = cache.__class__
    cache.__class__ = cache._orig_class
    cache.clear()
    def _disable_cache():
        cache.__class__ = _disabled_class
    request.addfinalizer(_disable_cache)

    return cache



@pytest.fixture(scope='session', autouse=True)
def _disable_cache(request):
    """
    Disable the given cache backend.

    We disable by monkeypatching rather than replacing wholesale, because the
    common "from django.core.cache import cache" idiom makes replacement
    unreliable; some module may have imported the cache before we can replace
    it.

    """
    from django.core.cache import cache
    from django.core.cache.backends.locmem import LocMemCache

    if not isinstance(cache, LocMemCache):
        raise ValueError("Tests can only be run with the LocMem cache backend.")

    class _DisabledCache(cache.__class__):
        def _error(self):
            raise ValueError(
                "Tests cannot access cache unless the 'cache' fixture is used.")

        def __getattr__(self, attr):
            self._error()

        def __getitem__(self, key):
            self._error()

    cache._orig_class = cache.__class__
    cache.__class__ = _DisabledCache

    def _restore_cache():
        cache.__class__ = cache._orig_class

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
