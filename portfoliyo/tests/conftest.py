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
