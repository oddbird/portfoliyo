"""Load SMS backend based on settings."""
from django.conf import settings


def get_backend(path):
    bits = path.split('.')
    module_name = '.'.join(bits[:-1])
    module = __import__(module_name, {}, {}, bits[-1])
    return getattr(module, bits[-1])


sms = get_backend(settings.PORTFOLIYO_SMS_BACKEND)()
