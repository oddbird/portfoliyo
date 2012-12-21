"""Rendering and sending of notifications."""
from . import store


def send(profile_id):
    """Send activity notification(s) to user with given profile ID."""
    from portfoliyo import model
    profile = model.Profile.objects.select_related('user').get(pk=profile_id)
    notifications = store.get_and_clear_all(profile_id)

    return _send_email(profile, notifications)



def _send_email(profile, notifications):
    """Actually construct and send activity notification email."""
    # @@@ temporary development/debugging stub
    import pprint
    print pprint.pprint(list(notifications))
    # log warning on unknown notification names
