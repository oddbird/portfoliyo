"""Rendering and sending of notifications."""
from portfoliyo import model

from . import store


def send(profile_id):
    """
    Send activity notification(s) to user with given profile ID.

    Return ``True`` if email was sent, ``False`` otherwise.

    """
    profile = model.Profile.objects.select_related('user').get(pk=profile_id)
    user = profile.user
    if user.email and user.is_active:
        notifications = store.get_and_clear_all(profile_id)

        if notifications:
            return _send_email(profile, notifications)

    return False



def _send_email(profile, notifications):
    """Construct and send activity notification email."""
    # @@@ temporary development/debugging stub
    import pprint
    print pprint.pprint(list(notifications))
    # log warning on unknown notification names
