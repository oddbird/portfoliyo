"""Twilio SMS backend."""
from __future__ import absolute_import

from django.conf import settings
from twilio import rest

from . import base


class TwilioSMSBackend(base.SMSBackend):
    def __init__(self):
        """Instantiate a TwilioRestClient based on settings."""
        self.client = rest.TwilioRestClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            )


    def send(self, to, from_, body):
        """Send an SMS."""
        return self.client.sms.messages.create(to=to, from_=from_, body=body)
