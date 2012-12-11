"""Code to get access to a Pusher API instance."""
from __future__ import absolute_import

from django.conf import settings
import pusher



def get_pusher():
    """Return a real pusher client if configured in settings, or None."""
    app_id = getattr(settings, 'PUSHER_APPID', None)
    key = getattr(settings, 'PUSHER_KEY', None)
    secret = getattr(settings, 'PUSHER_SECRET', None)
    if app_id and key and secret:
       return pusher.Pusher(app_id=app_id, key=key, secret=secret, port=443)
    return None
