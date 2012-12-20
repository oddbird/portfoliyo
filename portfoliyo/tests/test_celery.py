"""Tests for our transactional Celery behavior."""
from portfoliyo import tasks, xact


def test_tasks_run_after_transaction(sms):
    """Task is not applied until after transaction-in-progress commits."""
    # If we actually touched the database in this test, we would need the
    # `transactional_db` fixture; but we don't, so we avoid the slowdown.
    with xact.xact():
        tasks.send_sms.delay('+15555555555', 'something')
        assert len(sms.outbox) == 0

    assert len(sms.outbox) == 1


def test_tasks_discarded_if_transaction_rolled_back(sms):
    class TestException(Exception):
        pass
    try:
        with xact.xact():
            tasks.send_sms.delay('+15555555555', 'something')
            # exception causes transaction to be rolled back
            raise TestException()
    except TestException:
        pass

    # task was discarded because transaction was rolled back
    assert len(sms.outbox) == 0
