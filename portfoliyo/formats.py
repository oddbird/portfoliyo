from django.contrib.auth.models import UserManager
from django.core.validators import email_re
from django.utils.encoding import smart_unicode
import phonenumbers



def normalize_phone(value):
    """
    Normalize a phone number to E.164 format.

    Return None if the given value can't be parsed as a phone number.

    """
    if not value:
        return None

    if value[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # Assume US format otherwise
        parse_type = 'US'
    try:
        phone_representation = phonenumbers.parse(value, parse_type)
    except phonenumbers.NumberParseException:
        return None
    else:
        return phonenumbers.format_number(
            phone_representation, phonenumbers.PhoneNumberFormat.E164)


def normalize_email(value):
    """
    Normalize an email address by lowercasing domain part.

    Return None if the given value doesn't appear to be an email address.

    """
    if email_re.search(smart_unicode(value)):
        return UserManager.normalize_email(value)
    return None



def display_phone(value):
    """Convert a phone number to more user-friendly XXX-XXX-XXXX format."""
    p = phonenumbers.parse(value)
    return phonenumbers.format_number(
        p, phonenumbers.PhoneNumberFormat.RFC3966)[7:]
