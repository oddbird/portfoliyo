"""Allow superusers to impersonate other users as a debugging aid."""
from django import http

from portfoliyo import model


SESSION_KEY = '_impersonate_user_id'


class ImpersonationMiddleware(object):
    """
    Allow superusers to impersonate other users as a debug aid.

    Append ?impersonate=email@example.com to begin impersonating a user. The
    impersonation will persist in your session until you append
    ?impersonate=stop to a URL.

    """
    def process_request(self, request):
        request.impersonating = False
        if not request.user.is_superuser:
            return None

        if 'impersonate' in request.GET:
            email = request.GET['impersonate']
            if email == 'stop':
                if SESSION_KEY in request.session:
                    del request.session[SESSION_KEY]
                return None
            try:
                impersonate = model.User.objects.get(email=email)
            except model.User.DoesNotExist:
                return http.HttpResponseBadRequest(
                    "Cannot impersonate %s; user not found." % email)
            request.session[SESSION_KEY] = impersonate.pk
        elif SESSION_KEY in request.session:
            try:
                impersonate = model.User.objects.get(
                    pk=request.session[SESSION_KEY])
            except model.User.DoesNotExist:
                del request.session[SESSION_KEY]
                return None
        else:
            return None

        request.real_user = request.user
        request.impersonating = True
        request.user = impersonate
