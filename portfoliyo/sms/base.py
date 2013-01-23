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
    for chunk in split_sms(body):
        backend.send(phone, settings.DEFAULT_NUMBER, chunk)


def split_sms(text, joiner='...'):
    """
    Return iterable of chunks of ``text`` <=160 chars each.

    Joined components will end/begin with ``joiner``.

    """
    joiner_len = len(joiner)
    while True:
        if len(text) <= 160:
            yield text
            break
        breakpoint = 160-joiner_len
        yield text[:breakpoint] + joiner
        text = joiner + text[breakpoint:]
