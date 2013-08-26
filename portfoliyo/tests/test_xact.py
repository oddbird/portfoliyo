"""Tests for transaction wrapper."""
from django.db import transaction, IntegrityError
import mock
import pytest

from portfoliyo import model, xact

from portfoliyo.tests import factories


def test_can_use_twice():
    """Can use same xact object as context manager twice."""
    cm = xact.xact()

    assert not transaction.is_managed()

    for i in range(2):
        with cm:
            assert transaction.is_managed()
        assert not transaction.is_managed()


@pytest.fixture
def mock_transaction_methods(request):
    """Mock transaction methods for easier testing of xact edge-case logic."""
    module = 'portfoliyo.xact.transaction'
    to_mock = [
        'commit',
        'rollback',
        'savepoint',
        'savepoint_commit',
        'savepoint_rollback',
        ]
    patchers = {attr: mock.patch('%s.%s' % (module, attr)) for attr in to_mock}

    def _stop():
        for patcher in patchers.values():
            patcher.stop()
    request.addfinalizer(_stop)

    mocks = {attr: patcher.start() for attr, patcher in patchers.items()}
    return mocks


def test_error_in_commit(mock_transaction_methods):
    """Error in commit causes rollback and re-raises error."""
    mock_transaction_methods['commit'].side_effect = IntegrityError()
    with pytest.raises(IntegrityError):
        with xact.xact():
            pass

    assert mock_transaction_methods['rollback'].call_count == 1



def test_nested_xact_uses_savepoints(mock_transaction_methods):
    mock_sp_commit = mock_transaction_methods['savepoint_commit']
    mock_sp = mock_transaction_methods['savepoint']
    mock_sp.return_value = 3

    with xact.xact():
        with xact.xact():
            pass

    assert mock_sp.call_count == 1
    assert mock_sp_commit.call_count == 1
    mock_sp_commit.assert_called_with(3, 'default')



def test_error_in_savepoint_commit_causes_rollback(mock_transaction_methods):
    mock_sp_commit = mock_transaction_methods['savepoint_commit']
    mock_sp_rollback = mock_transaction_methods['savepoint_rollback']
    mock_sp = mock_transaction_methods['savepoint']
    mock_sp.return_value = 4
    mock_sp_commit.side_effect = IntegrityError()

    with pytest.raises(IntegrityError):
        with xact.xact():
            with xact.xact():
                pass

    assert mock_sp_commit.call_count == 1
    assert mock_sp_rollback.call_count == 1
    mock_sp_rollback.assert_called_with(4, 'default')


def test_savepoint_rollback(mock_transaction_methods):
    with pytest.raises(IntegrityError):
        with xact.xact():
            with xact.xact():
                raise IntegrityError()

    assert mock_transaction_methods['savepoint_rollback'].call_count == 1
    assert mock_transaction_methods['savepoint_commit'].call_count == 0


def test_post_commit_listener_uses_db(transactional_db):
    """Test that a post_commit listener can safely query the database."""
    called = []
    def _my_listener(**kwargs):
        assert model.Profile.objects.count() == 1
        called.append(True)
    xact.post_commit.connect(_my_listener)

    with xact.xact():
        factories.ProfileFactory.create()

    assert called == [True]
