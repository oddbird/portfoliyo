import contextlib

import mock

from portfoliyo.notifications import types
from portfoliyo.notifications.render import collect


@contextlib.contextmanager
def mock_store(notification_data):
    get_all = 'portfoliyo.notifications.store.get_and_clear_all'
    with mock.patch(get_all) as mock_get_all:
        mock_get_all.return_value = notification_data
        yield



class TestNotificationCollection(object):
    def test_invalid_notification_type(self):
        """An invalid notification type is logged and ignored."""
        logger = 'portfoliyo.notifications.render.collect.logger'
        profile = mock.Mock(id=1)
        collection = collect.NotificationCollection(profile)
        with mock.patch(logger) as mock_logger:
            with mock_store([{'name': 'foo'}]):
                assert not collection

        mock_logger.warning.assert_called_with(
            "Unknown notification type '%s'", 'foo')


    def test_invalid_data(self):
        """Evaluates to false if no notifications have valid data."""
        profile = mock.Mock(id=1)
        collection = collect.NotificationCollection(profile)
        with mock_store([{'name': types.ADDED_TO_VILLAGE}]):
            assert not collection
