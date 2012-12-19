"""Tests for notification storage/retrieval."""
from portfoliyo.notifications import store



def test_pending_profile_ids():
    """Includes profile IDs with triggering notifications."""
    store.store(1, 'some', triggering=True)
    store.store(1, 'other', triggering=False)
    store.store(2, 'thing', triggering=False)
    store.store(3, 'thing', triggering=True)

    assert store.pending_profile_ids() == {1, 3}



def test_get_and_clear_all():
    """Gets all data from all pending notifications."""
    store.store(1, 'some', foo='bar')
    store.store(1, 'other', triggering=True)
    store.store(2, 'irrelevant')

    res = list(store.get_and_clear_all(1))

    assert res == [
        {'name': 'some', 'triggering': '0', 'foo': 'bar'},
        {'name': 'other', 'triggering': '1'},
        ]
