"""Tests for Pusher support code."""
from django.test.utils import override_settings

import mock

from portfoliyo import pusher


def test_context_processor():
    with override_settings(PUSHER_KEY="foo"):
        expected = {"PUSHER_KEY": "foo"}
        assert pusher.context_processor(None) == expected


@mock.patch('pusher.Pusher')
def test_get_pusher(mock_Pusher):
    """If settings are configured, returns a Pusher instance."""
    with override_settings(PUSHER_APPID='a', PUSHER_KEY='k', PUSHER_SECRET='s'):
        p = pusher.get_pusher()

    assert p is mock_Pusher.return_value
    mock_Pusher.assert_called_with(app_id='a', key='k', secret='s')


def test_get_pusher_none():
    """If settings are not configured, return None."""
    assert pusher.get_pusher() is None
