"""Tests for notification email sending."""
from django.core import mail
import mock
import pytest

from portfoliyo.notifications import send, record, types
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



@pytest.fixture
def recip(request, db):
    """A user who can receive notifications."""
    # Turn all notification triggers off; we want to trigger sending manually
    return factories.ProfileFactory.create(
        user__email='foo@example.com',
        user__is_active=True,
        notify_new_parent=False,
        notify_parent_text=False,
        notify_added_to_village=False,
        notify_joined_my_village=False,
        notify_teacher_post=False,
        )



class TestSendEmail(object):
    def test_generic_subject_single_student(self, recip):
        """Generic subject if multiple notification types, single student."""
        rel = factories.RelationshipFactory.create(
            from_profile=recip, to_profile__name='A Student')
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student)

        record.added_to_village(recip, other_rel.elder, rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert send.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in A Student's village."


    def test_generic_subject_multiple_students(self, recip):
        """Generic subject if multiple notification types, multiple students."""
        rel = factories.RelationshipFactory.create(from_profile=recip)
        other_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            from_profile=recip, to_profile=other_rel.student)

        record.added_to_village(recip, other_rel.elder, other_rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert send.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in 2 of your villages."


    @pytest.mark.parametrize('village_count', [1, 2])
    def test_only_added_to_village_subject(self, village_count, recip):
        """Specific subject if all notifications are added-to-village."""
        for i in range(village_count):
            rel = factories.RelationshipFactory.create(
                from_profile=recip, to_profile__name='S%s' % i)
            other_rel = factories.RelationshipFactory.create(
                from_profile__name='E%s' % i, to_profile=rel.student)
            record.added_to_village(recip, other_rel.elder, rel.student)

        if village_count == 1:
            exp = "E0 added you to S0's village."
        else:
            exp = "You have been added to 2 villages."

        assert send.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == exp


    def test_invalid_notification_type(self, recip):
        """An invalid notification type is logged and ignored."""
        with mock.patch('portfoliyo.notifications.send.logger') as mock_logger:
            assert not send._send_email(recip, [{'name': 'foo'}])

        mock_logger.warning.assert_called_with(
            "Unknown notification type '%s'", 'foo')


    def test_invalid_data(self, recip):
        """No email sent if no notifications have valid data."""
        assert not send._send_email(recip, [{'name': types.ADDED_TO_VILLAGE}])
        assert not len(mail.outbox)



class TestNotificationAggregator(object):
    def test_get_context(self):
        """Default get_context returns empty dict."""
        na = send.NotificationAggregator()
        assert na.get_context() == {}



class TestAddedToVillageNotifications(object):
    def test_add_invalid(self, db):
        """Adding invalid data returns False and leaves list empty."""
        atvn = send.AddedToVillageNotifications()

        # invalid data could be because its missing from the DB...
        assert not atvn.add({'added-by-id': 1, 'student-id': 2})
        # ...or because the required key(s) aren't provided at all.
        assert not atvn.add({})

        # aggregator is still empty
        assert not atvn
