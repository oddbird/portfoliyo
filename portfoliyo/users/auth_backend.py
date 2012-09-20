"""
Backwards-compatibility import location for EmailBackend.

Django stores auth backend dotted paths in the session, so we need to keep this
around until all existing sessions have expired / been renewed.

Here is the code to run on the live database to determine when it is safe to
remove this fallback:

from django.contrib.sessions.models import Session
import base64, pickle
set([pickle.loads(base64.decodestring(s.session_data)[41:]).get('_auth_user_backend', '') for s in Session.objects.all()])

If the resulting set does not contain
'portfoliyo.users.auth_backend.EmailBackend', this module can safely be
removed.

"""
from portfoliyo.model.users.auth_backend import EmailBackend
