"""Unread-counts data-model layer implementation."""
from portfoliyo.redis import client



def mark_unread(post, profile):
    """Mark given post unread by given profile."""
    client.sadd(make_key(post.student, profile), post.id)



def is_read(post, profile):
    """Given post is read by given profile (returns boolean)."""
    return not client.sismember(make_key(post.student, profile), post.id)



def unread_count(student, profile):
    """Return count of profile's unread posts in given student's village."""
    return client.scard(make_key(student, profile))



def mark_village_read(student, profile):
    """Mark all posts in given student's village as read by profile."""
    client.delete(make_key(student, profile))



def make_key(student, profile):
    """Construct Redis key for given profile and student."""
    return 'unread:%s:%s' % (profile.id, student.id)
