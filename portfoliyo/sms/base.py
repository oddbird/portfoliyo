"""Core SMS functionality."""
from django.conf import settings


def get_backend(path):
    """Load SMS backend based on settings."""
    bits = path.split('.')
    module_name = '.'.join(bits[:-1])
    module = __import__(module_name, {}, {}, bits[-1])
    return getattr(module, bits[-1])


backend = get_backend(settings.PORTFOLIYO_SMS_BACKEND)()


def send(phone, body):
    """Sends sms to ``phone`` with text ``body``."""
    backend.send(phone, settings.PORTFOLIYO_SMS_DEFAULT_FROM, body)
