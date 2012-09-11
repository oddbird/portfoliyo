import re

from django.contrib.auth.models import UserManager
from django.contrib.localflavor.us.forms import phone_digits_re
from django.core.validators import email_re
from django.utils.encoding import smart_unicode



def normalize_phone(value):
    """
    Normalize a US phone number to XXX-XXX-XXXX format.

    Return None if the given value can't be parsed as a US phone number.

    """
    value = re.sub('(\(|\)|\s+)', '', smart_unicode(value))
    m = phone_digits_re.search(value)
    if m:
        return u'%s-%s-%s' % (m.group(1), m.group(2), m.group(3))
    return None


def normalize_email(value):
    """
    Normalize an email address by lowercasing domain part.

    Return None if the given value doesn't appear to be an email address.

    """
    if email_re.search(smart_unicode(value)):
        return UserManager.normalize_email(value)
    return None
