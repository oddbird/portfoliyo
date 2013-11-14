import csv
import urllib

from django.conf import settings

from portfoliyo.model import Profile


def import_from_csv(teacher, fn, source_phone=None):
    """
    Import users from a CSV file and associate with given teacher.

    The first three columns of the CSV file must be name, phone, and
    groups. All other columns are ignored. The groups column may contain
    multiple group names separated by "::".

    If a user with a matching name already exists within this teacher's
    account, that user will not be modified.

    Optionally sets source-phone for all created users to given number.

    Return a tuple of two lists, (created_profiles, found_profiles).

    """
    pass
