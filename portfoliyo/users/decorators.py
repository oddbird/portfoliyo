"""
Auth/account-related view decorators.

"""
from functools import wraps

from django.conf import settings
from django.contrib.auth import decorators as auth_decorators
from django.contrib import messages


def insufficient_permissions(func):
    """View decorator to add explanatory no-perms message."""
    @wraps(func)
    def _wrapped(request, *a, **kw):
        response = func(request, *a, **kw)
        if (response.status_code == 302 and
                response['Location'].startswith(settings.LOGIN_URL)):
            messages.warning(
                request,
                u"Sorry, your account doesn't have access to this page. "
                u"Please log in with a different account "
                u"or visit a different page.")
        return response
    return _wrapped


def school_staff_required(func):
    """View decorator to require ``school_staff`` attribute."""
    actual_decorator = auth_decorators.user_passes_test(
        lambda u: u.profile.school_staff,
    )
    return insufficient_permissions(actual_decorator(func))
