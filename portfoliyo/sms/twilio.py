"""
Temporary back-compat location for TwilioSMSBackend.

Avoids downtime on next Heroku deploy; can be removed after that.

"""
from .backends.twilio import TwilioSMSBackend
