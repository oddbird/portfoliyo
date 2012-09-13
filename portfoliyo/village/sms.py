"""Village SMS-handling."""
from ..users import models


def receive_sms(source, body):
    """Hook for when an SMS is received."""
    try:
        profile = models.Profile.objects.select_related(
            'user').get(phone=source)
    except models.Profile.DoesNotExist:
        # @@@ log this?
        return

    profile.user.is_active = True
    profile.user.save()

    # @@@ post message
