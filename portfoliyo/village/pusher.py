from django.conf import settings
import pusher



def context_processor(request):
    return {'PUSHER_KEY': getattr(settings, 'PUSHER_KEY', '')}


def get_pusher():
    """Return a real pusher client if configured in settings, or None."""
    app_id = getattr(settings, 'PUSHER_APP_ID')
    key = getattr(settings, 'PUSHER_KEY')
    secret = getattr(settings, 'PUSHER_SECRET')
    if app_id and key and secret:
       return pusher.Pusher(app_id=app_id, key=key, secret=secret)
    return None
