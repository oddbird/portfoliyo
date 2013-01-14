"""Tests for mixpanel-tracking."""
import base64
import json
import urlparse

import mock

from portfoliyo import mixpanel


def test_track():
    """Track sends correct request to Mixpanel."""
    with mock.patch('portfoliyo.mixpanel.urllib2.urlopen') as mock_urlopen:
        mock_urlopen.return_value.getcode.return_value = 200
        mock_urlopen.return_value.read.return_value = '1'
        with mock.patch('portfoliyo.mixpanel.settings') as mock_settings:
            mock_settings.MIXPANEL_ID = 'mixpanel-token'
            mixpanel.track('some-event', {'property': 'value'})


    expected_data = {
        'event': 'some-event',
        'properties': {'token': 'mixpanel-token', 'property': 'value'},
        }

    assert mock_urlopen.call_count == 1
    url = mock_urlopen.call_args[0][0]
    found_data = json.loads(
        base64.b64decode(urlparse.parse_qs(
                urlparse.urlparse(url).query)['data'][0])
        )
    assert found_data == expected_data



def test_track_not_configured():
    """If mixpanel is not configured, no request is sent."""
    with mock.patch('portfoliyo.mixpanel.urllib2.urlopen') as mock_urlopen:
        with mock.patch('portfoliyo.mixpanel.settings', spec=[]):
            mixpanel.track('some-event', {'property': 'value'})

    assert not mock_urlopen.call_count



def test_bad_status_code():
    """Logs warning if status code is not 200."""
    with mock.patch('portfoliyo.mixpanel.urllib2.urlopen') as mock_urlopen:
        mock_urlopen.return_value.getcode.return_value = 400
        mock_urlopen.return_value.read.return_value = '0'
        with mock.patch('portfoliyo.mixpanel.settings') as mock_settings:
            mock_settings.MIXPANEL_ID = 'mptok'
            with mock.patch('portfoliyo.mixpanel.logger') as mock_logger:
                mixpanel.track('some-event')


    mock_logger.warning.assert_called_with(
        "Mixpanel returned bad status code %s",
        400,
        extra={
            'stack': True,
            'body': '0',
            'params': {'event': 'some-event', 'properties': {'token': 'mptok'}},
            },
        )



def test_bad_response():
    """Logs warning if response body is not '1'."""
    with mock.patch('portfoliyo.mixpanel.urllib2.urlopen') as mock_urlopen:
        mock_urlopen.return_value.getcode.return_value = 200
        mock_urlopen.return_value.read.return_value = '0'
        with mock.patch('portfoliyo.mixpanel.settings') as mock_settings:
            mock_settings.MIXPANEL_ID = 'mptok'
            with mock.patch('portfoliyo.mixpanel.logger') as mock_logger:
                mixpanel.track('some-event')


    mock_logger.warning.assert_called_with(
        "Mixpanel returned bad response %s",
        '0',
        extra={
            'stack': True,
            'params': {'event': 'some-event', 'properties': {'token': 'mptok'}},
            },
        )
