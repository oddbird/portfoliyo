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
    p = client.pipeline()

    # track list of student IDs for each group
    student_ids_by_group = {}
    # we need an ordered list of student IDs to match them up with the pipeline
    # results, but we also need the set for fast membership tests
    student_ids_seen = set()
    ordered_student_ids = []

    for group in groups:
        student_ids = student_ids_by_group.setdefault(group, set())
        for student in group.students.all():
            student_ids.add(student.id)
            if student.id not in student_ids_seen:
                ordered_student_ids.append(student.id)
                student_ids_seen.add(student.id)
                p.scard(make_key(student, profile))
    unread_counts_by_student_id = dict(zip(ordered_student_ids, p.execute()))
    return {
        group: sum(
            unread_counts_by_student_id[sid]
            for sid in student_ids_by_group[group]
            )
        for group in groups
        }


def mark_village_read(student, profile):
    """Mark all posts in given student's village as read by profile."""
    client.delete(make_key(student, profile))



def make_key(student, profile):
    """Construct Redis key for given profile and student."""
    return 'unread:%s:%s' % (profile.id, student.id)
