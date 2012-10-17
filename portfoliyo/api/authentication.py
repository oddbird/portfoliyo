"""API Authorization."""
from tastypie import authentication



class SessionAuthentication(authentication.SessionAuthentication):
    """
    Session-based auth that doesn't do CSRF checks.

    The django-session-csrf middleware runs on API views as well, so CSRF is
    already covered, we don't need to duplicate it.

    """
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()
