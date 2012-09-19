"""
Backwards-compatibility import location for EmailBackend.

Django stores auth backend dotted paths in the session, so we need to keep this
around until all existing sessions have expired / been renewed.

"""
from portfoliyo.model.users.auth_backend import EmailBackend
