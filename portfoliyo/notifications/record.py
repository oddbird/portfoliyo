"""Record notifications."""
from portfoliyo import tasks
from . import store



def post(profile, post):
    """Notify ``profile`` that a parent or teacher posted ``post``."""
    pref = 'notify_%s' % (
        'teacher_post' if post.author.school_staff else 'parent_text')
    triggering = getattr(profile, pref)
    data = {'post-id': post.id}
    _record(profile, 'post', triggering=triggering, data=data)



def bulk_post(profile, bulk_post):
    """Notify ``profile`` that a teacher posted ``bulk_post``."""
    triggering = profile.notify_teacher_post
    data = {'bulk-post-id': bulk_post.id}
    _record(profile, 'bulk post', triggering=triggering, data=data)



def new_parent(profile, signup):
    """
    Notify ``profile`` that a parent signed up.

    ``signup`` should be a ``TextSignup`` model instance.

    """
    triggering = profile.notify_new_parent
    data = {'signup-id': signup.id}
    _record(profile, 'new parent', triggering=triggering, data=data)



def village_additions(added_by, teachers, students):
    """Send appropriate notifications for ``teachers`` added to ``students``."""
    teachers = set(teachers)
    teachers.discard(added_by)
    for student in students:
        for existing_teacher_rel in student.elder_relationships.filter(
                from_profile__school_staff=True).exclude(
                from_profile__in=teachers):
            for teacher in teachers:
                new_teacher(existing_teacher_rel.elder, teacher, student)
        for teacher in teachers:
            added_to_village(teacher, added_by, student)


def added_to_village(profile, added_by, student):
    """Notify ``profile`` that ``added_by`` added them to ``student`` village"""
    triggering = profile.notify_added_to_village
    data = {'teacher-id': added_by.id, 'student-id': student.id}
    _record(profile, 'added to village', triggering=triggering, data=data)



def new_teacher(profile, teacher, student):
    """Notify ``profile`` that ``teacher`` joined ``student``s village."""
    triggering = profile.notify_joined_my_village
    data = {'teacher-id': teacher.id, 'student-id': student.id}
    _record(profile, 'new teacher', triggering=triggering, data=data)



def _record(profile, name, triggering=False, data=None):
    """Record a notification for the given profile."""
    if profile.user.email is None or not profile.user.is_active:
        return
    store.store(profile.id, name, triggering=triggering, data=data)
    # @@@ later this will be only if user prefers instant notifications
    if triggering:
        tasks.send_notification.delay(profile.id)
