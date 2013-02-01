"""Tests for Celery tasks."""
import mock

from portfoliyo import tasks



def test_check_for_pending_notifications():
    """Triggers send_notification_email task for all pending profile IDs."""
    target1 = 'portfoliyo.tasks.send_notification_email'
    target2 = 'portfoliyo.notifications.store.pending_profile_ids'
    with mock.patch(target1) as mock_send_notification:
        with mock.patch(target2) as mock_pending_profile_ids:
            mock_pending_profile_ids.return_value = [5]
            tasks.check_for_pending_notifications.delay()

    mock_send_notification.delay.assert_called_once_with(5)
