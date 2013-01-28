"""Tests for invite-sending functions."""
import mock

from portfoliyo import invites


def test_send_invite_sms_too_long():
    """If the SMS invite text is too long, break it up at newlines."""
    profile = mock.Mock()
    profile.phone = '+32165440987'
    profile.source_phone = '+13336660000'

    with mock.patch('portfoliyo.invites.loader') as mock_loader:
        mock_loader.render_to_string.return_value = (
            "%s\n%s" % ('a' * 100, 'b' * 100))

        invites.send_invite_sms(profile, 'foo', {})

    assert profile.send_sms.call_count == 2
    assert profile.send_sms.call_args_list[0][0][0] == 'a' * 100
    assert profile.send_sms.call_args_list[1][0][0] == 'b' * 100
