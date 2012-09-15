from __future__ import absolute_import

from django.conf import settings
import pusher



def context_processor(request):
    return {'PUSHER_KEY': getattr(settings, 'PUSHER_KEY', '')}


def get_pusher():
    """Return a real pusher client if configured in settings, or None."""
    app_id = getattr(settings, 'PUSHER_APPID', None)
    key = getattr(settings, 'PUSHER_KEY', None)
    secret = getattr(settings, 'PUSHER_SECRET', None)
    if app_id and key and secret:
       return pusher.Pusher(app_id=app_id, key=key, secret=secret)
    return None
