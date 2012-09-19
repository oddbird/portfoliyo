"""Tests for invite-sending functions."""
import mock

from portfoliyo import invites


def test_send_invite_sms_too_long(sms):
    """If the SMS invite text is too long, break it up at newlines."""
    user = mock.Mock()
    user.profile.phone = '+32165440987'

    with mock.patch('portfoliyo.invites.loader') as mock_loader:
        mock_loader.render_to_string.return_value = (
            "%s\n%s" % ('a' * 100, 'b' * 100))

        invites.send_invite_sms(user, 'foo', {})

    assert len(sms.outbox) == 2
    assert sms.outbox[0].body == 'a' * 100
    assert sms.outbox[1].body == 'b' * 100
