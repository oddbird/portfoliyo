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


def unread_counts(students, profile):
    """
    Return profile's unread counts for all given students.

    Return dict mapping student to unread count.

    """
    student = list(students)
    p = client.pipeline()
    for student in students:
        p.scard(make_key(student, profile))
    return dict(zip(students, p.execute()))


def group_unread_count(group, profile):
    """Return count of profile's unread posts in all villages in group."""
    p = client.pipeline()
    for student in group.students.all():
        p.scard(make_key(student, profile))
    return sum(p.execute())


def group_unread_counts(groups, profile):
    """
    Return counts of profile's unread posts in all given groups.

    Return a dictionary mapping groups to counts.

    """
    # the algorithm here relies on consistent ordering
    groups = list(groups)
    p = client.pipeline()
    # map each group to a count of villages in that group.
    village_counts = {}
    for group in groups:
        count = 0
        for student in group.students.all():
            count += 1
            p.scard(make_key(student, profile))
        village_counts[group] = count
    # flat list of all per-village unread counts
    raw = p.execute()
    results = {}
    for group in groups:
        count = village_counts[group]
        # pop off and sum the right number of per-village unread counts
        total, raw = sum(raw[:count]), raw[count:]
        results[group] = total
    return results


def mark_village_read(student, profile):
    """Mark all posts in given student's village as read by profile."""
    client.delete(make_key(student, profile))



def make_key(student, profile):
    """Construct Redis key for given profile and student."""
    return 'unread:%s:%s' % (profile.id, student.id)
