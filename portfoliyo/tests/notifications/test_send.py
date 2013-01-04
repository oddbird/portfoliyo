"""Tests for notification email sending."""
import mock

from portfoliyo.notifications import send
from portfoliyo.tests import factories



def test_send_only_if_email(db):
    """If user has no email, notifications not queried or sent."""
    p = factories.ProfileFactory.create(user__email=None)
    with mock.patch('portfoliyo.notifications.store.get_and_clear_all') as mg:
        with mock.patch('portfoliyo.notifications.send._send_email') as mse:
            assert not send.send(p.id)

    assert not mg.call_count
    assert not mse.call_count



def test_send_only_if_active(db):
    """If user is inactive, notifications not queried or sent."""
    p = factories.ProfileFactory.create(
        user__email='foo@example.com', user__is_active=False)
    with mock.patch('portfoliyo.notifications.store.get_and_clear_all') as mg:
        with mock.patch('portfoliyo.notifications.send._send_email') as mse:
            assert not send.send(p.id)

    assert not mg.call_count
    assert not mse.call_count



def test_send_only_if_notifications(db):
    """If there are no notifications, don't try to send an email."""
    p = factories.ProfileFactory.create(
        user__email='foo@example.com', user__is_active=True)
    with mock.patch('portfoliyo.notifications.store.get_and_clear_all') as mg:
        mg.return_value = []
        with mock.patch('portfoliyo.notifications.send._send_email') as mse:
            assert not send.send(p.id)

    assert not mse.call_count



def test_send_passes_profile_and_notifications_to_send_email(db):
    """If there are notifications, pass profile and notifications on."""
    p = factories.ProfileFactory.create(
        user__email='foo@example.com', user__is_active=True)
    with mock.patch('portfoliyo.notifications.store.get_and_clear_all') as mg:
        mg.return_value = [{'name': 'foo'}]
        with mock.patch('portfoliyo.notifications.send._send_email') as mse:
            mse.return_value = True
            assert send.send(p.id)

    mse.assert_called_with(p, mg.return_value)
