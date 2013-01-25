"""Unread-counts data-model layer implementation."""
from portfoliyo.redis import client



def mark_unread(post, profile):
    """Mark given post unread by given profile."""
    client.sadd(make_key(post.student, profile), post.id)


def mark_read(post, profile):
    """Mark given post read by given profile."""
    client.srem(make_key(post.student, profile), post.id)



def is_unread(post, profile):
    """Given post is unread by given profile (returns boolean)."""
    return client.sismember(make_key(post.student, profile), post.id)



def all_unread(student, profile):
    """Return set of post IDs in ``student`` village unread by ``profile``."""
    return client.smembers(make_key(student, profile))



def unread_count(student, profile):
    """Return count of profile's unread posts in given student's village."""
    return client.scard(make_key(student, profile))



def group_unread_count(group, profile):
    """Return count of profile's unread posts in all villages in group."""
    return sum([unread_count(s, profile) for s in group.students.all()])


def mark_village_read(student, profile):
    """Mark all posts in given student's village as read by profile."""
    client.delete(make_key(student, profile))



def make_key(student, profile):
    """Construct Redis key for given profile and student."""
    return 'unread:%s:%s' % (profile.id, student.id)
