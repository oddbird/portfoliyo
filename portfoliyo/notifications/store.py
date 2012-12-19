"""Notification storage and retrieval."""
import time

from portfoliyo.redis import client as redis

# notifications last 48 hours
EXPIRY_SECONDS = 48 * 60 * 60

PENDING_PROFILES_KEY = 'notify:pending:profile-ids'
NEXT_NOTIFICATION_ID_KEY_PATTERN = 'notify:profiles:%s:next-notification-id'
PENDING_NOTIFICATIONS_KEY_PATTERN = 'notify:profiles:%s:pending'
NOTIFICATION_KEY_PATTERN = 'notify:profiles:%s:notifications:%s'



def pending_profile_ids():
    """Get list of profile IDs with pending triggering notifications."""
    return redis.smembers(PENDING_PROFILES_KEY)



def store(profile_id, name, triggering=False, data=None):
    """
    Store a notification for given profile ID.

    ``name`` is the notification type name.

    If ``triggering`` is True, this notification will trigger a notification
    email for this user the next time they are sent out.

    ``data`` is a dictionary of arbitrary additional data about the
    notification; all values should be strings.

    """
    data = data or {}
    data['triggering'] = '1' if triggering else '0'
    data['name'] = name

    pending_key = make_pending_notifications_key(profile_id)
    notification_id = get_next_notification_id(profile_id)
    key = make_notification_key(profile_id, notification_id)

    expiry_timestamp = time.time() + EXPIRY_SECONDS

    p = redis.pipeline()
    # add the notification ID to the list of pending notifications for this user
    p.zadd(pending_key, expiry_timestamp, notification_id)
    # Store data hash for the notification. Allow the data to exist for an
    # extra minute so we don't ever try to query expired data
    p.hmset(key, data).expireat(key, int(expiry_timestamp) + 60)
    if triggering:
        # Add user to the set of users with pending triggering notifications
        p.sadd(PENDING_PROFILES_KEY, profile_id)
    p.execute()



def get_and_clear_all(profile_id):
    """
    Get and clear all pending notifications for given profile ID.

    Does not return expired notifications (those older than EXPIRY_SECONDS).

    """
    pending_key = make_pending_notifications_key(profile_id)
    now_ts = int(time.time())

    p = redis.pipeline()
    # get non-expired pending notifications for this user
    p.zrangebyscore(pending_key, now_ts, '+inf')
    # clear the pending notifications list
    p.delete(pending_key)
    # remove this user from the set of users w/ pending triggering notifications
    p.srem(PENDING_PROFILES_KEY, profile_id)
    # we don't clear out individual notification data; redis expiration will
    ids = p.execute()[0]

    for notification_id in ids:
        yield get(profile_id, notification_id)



def get(profile_id, notification_id):
    """Get a notification's data by id."""
    key = make_notification_key(profile_id, notification_id)
    return redis.hgetall(key)



def get_next_notification_id(profile_id):
    """Get the next notification ID for the given profile ID."""
    return redis.incr(NEXT_NOTIFICATION_ID_KEY_PATTERN % profile_id)



def make_notification_key(profile_id, notification_id):
    """Make Redis key for a notification's data."""
    return NOTIFICATION_KEY_PATTERN % (profile_id, notification_id)



def make_pending_notifications_key(profile_id):
    """Make Redis key for set of pending notifications."""
    return PENDING_NOTIFICATIONS_KEY_PATTERN % profile_id
