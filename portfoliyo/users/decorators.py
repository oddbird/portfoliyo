"""
Auth/account-related view decorators.

"""
from django.contrib.auth import decorators as auth_decorators


def school_staff_required(func):
    """View decorator to require ``school_staff`` attribute."""
    actual_decorator = auth_decorators.user_passes_test(
        lambda u: u.profile.school_staff,
    )
    return actual_decorator(func)
