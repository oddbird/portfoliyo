"""Mirror the Mixpanel JS people API (as closely as possible)."""
from . import base



def set(profile, data):
    """Set given mixpanel ``data`` (dict) for given profile."""
    base._send(
        'engage/', {'$set': data, '$distinct_id': profile.user.id, '$ip': 0})



def increment(profile, data):
    """Increment given mixpanel ``data`` (dict) for given profile."""
    base._send(
        'engage/', {'$add': data, '$distinct_id': profile.user.id, '$ip': 0})
