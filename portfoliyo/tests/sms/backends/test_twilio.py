"""Tests for Twilio SMS backend class."""
from django.test.utils import override_settings

import mock

from portfoliyo.sms.backends import twilio


@override_settings(TWILIO_ACCOUNT_SID='account_sid', TWILIO_AUTH_TOKEN='token')
@mock.patch("twilio.rest.TwilioRestClient")
def test_send(twilio_client_class):
    """send() method passes on its args to client send."""
    sms = twilio.TwilioSMSBackend()
    twilio_client_class.assert_called_with('account_sid', 'token')

    sms.send('1', '2', 'body')
    sms.client.sms.messages.create.assert_called_with(
        to='1', from_='2', body='body')
