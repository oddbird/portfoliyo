"""Tests for notification email sending."""
import mock

from portfoliyo.notifications import send
from portfoliyo.tests import factories



class TestSend(object):
    GET_AND_CLEAR_ALL = 'portfoliyo.notifications.store.get_and_clear_all'
    SEND_EMAIL = 'portfoliyo.notifications.send._send_email'


    def test_send_only_if_email(self, db):
        """If user has no email, notifications not queried or sent."""
        p = factories.ProfileFactory.create(user__email=None)
        with mock.patch(self.GET_AND_CLEAR_ALL) as mock_get_and_clear:
            with mock.patch(self.SEND_EMAIL) as mock_send_email:
                assert not send.send(p.id)

        assert not mock_get_and_clear.call_count
        assert not mock_send_email.call_count


    def test_send_only_if_active(self, db):
        """If user is inactive, notifications not queried or sent."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=False)
        with mock.patch(self.GET_AND_CLEAR_ALL) as mock_get_and_clear:
            with mock.patch(self.SEND_EMAIL) as mock_send_email:
                assert not send.send(p.id)

        assert not mock_get_and_clear.call_count
        assert not mock_send_email.call_count


    def test_send_only_if_notifications(self, db):
        """If there are no notifications, don't try to send an email."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=True)
        with mock.patch(self.GET_AND_CLEAR_ALL) as mock_get_and_clear:
            mock_get_and_clear.return_value = []
            with mock.patch(self.SEND_EMAIL) as mock_send_email:
                assert not send.send(p.id)

        assert not mock_send_email.call_count



    def test_send_passes_profile_and_notifications_to_send_email(self, db):
        """If there are notifications, pass profile and notifications on."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=True)
        with mock.patch(self.GET_AND_CLEAR_ALL) as mock_get_and_clear:
            mock_get_and_clear.return_value = [{'name': 'foo'}]
            with mock.patch(self.SEND_EMAIL) as mock_send_email:
                mock_send_email.return_value = True
                assert send.send(p.id)

        mock_send_email.assert_called_with(p, mock_get_and_clear.return_value)
