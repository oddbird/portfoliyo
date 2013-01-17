"""Tests for notification storage/retrieval."""
import mock

from portfoliyo.notifications import store



def test_pending_profile_ids(redis):
    """Includes profile IDs with triggering notifications."""
    store.store(1, 'some', triggering=True)
    store.store(1, 'other', triggering=False)
    store.store(2, 'thing', triggering=False)
    store.store(3, 'thing', triggering=True)

    assert store.pending_profile_ids() == {'1', '3'}



def test_get_all(redis):
    """Gets all data from all pending notifications."""
    store.store(1, 'some', data={'foo': 'bar'})
    store.store(1, 'other', triggering=True)
    store.store(2, 'irrelevant')

    res = list(store.get_all(1))

    assert res == [
        {'name': 'some', 'triggering': '0', 'foo': 'bar'},
        {'name': 'other', 'triggering': '1'},
        ]

    # does not clear by default
    assert list(store.get_all(1)) == res
    assert store.pending_profile_ids() == set(['1'])



def test_get_all_clear(redis):
    """Can also clear all pending notifications."""
    store.store(1, 'some', data={'foo': 'bar'})
    store.store(1, 'other', triggering=True)
    store.store(2, 'irrelevant')

    res = list(store.get_all(1, clear=True))

    assert res == [
        {'name': 'some', 'triggering': '0', 'foo': 'bar'},
        {'name': 'other', 'triggering': '1'},
        ]

    # clears
    assert list(store.get_all(1)) == []
    assert store.pending_profile_ids() == set()



def test_get_all_excludes_expired(redis):
    """Does not return expired notifications."""
    initial_time = 123456.789
    expired_time = initial_time + store.EXPIRY_SECONDS + 120

    with mock.patch('portfoliyo.notifications.store.time.time') as mock_time:
        mock_time.return_value = initial_time
        store.store(1, 'some')
        mock_time.return_value = expired_time

        assert list(store.get_all(1)) == []
