"""Record notifications."""
from django.conf import settings

from portfoliyo import tasks
from . import store, types



def post_all(p):
    """Send all appropriate notifications for creation of given post."""
    if not p.author:
        return
    record_func = bulk_post if p.is_bulk else post
    for profile in p.elders_in_context.exclude(pk=p.author.pk):
        record_func(profile, p)



def post(profile, post):
    """Notify ``profile`` that a parent or teacher posted ``post``."""
    pref = 'notify_%s' % (
        'teacher_post' if post.author.school_staff else 'parent_text')
    triggering = getattr(profile, pref)
    data = {'post-id': post.id}
    _record(profile, types.POST, triggering=triggering, data=data)



def bulk_post(profile, bulk_post):
    """Notify ``profile`` that a teacher posted ``bulk_post``."""
    triggering = profile.notify_teacher_post
    data = {'bulk-post-id': bulk_post.id}
    _record(profile, types.BULK_POST, triggering=triggering, data=data)



def new_parent(profile, signup):
    """
    Notify ``profile`` that a parent signed up.

    ``signup`` should be a ``TextSignup`` model instance.

    """
    triggering = profile.notify_new_parent
    data = {'signup-id': signup.id}
    _record(profile, types.NEW_PARENT, triggering=triggering, data=data)



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
    data = {'added-by-id': added_by.id, 'student-id': student.id}
    _record(profile, types.ADDED_TO_VILLAGE, triggering=triggering, data=data)



def new_teacher(profile, teacher, student):
    """Notify ``profile`` that ``teacher`` joined ``student``s village."""
    triggering = profile.notify_joined_my_village
    data = {'teacher-id': teacher.id, 'student-id': student.id}
    _record(profile, types.NEW_TEACHER, triggering=triggering, data=data)



def _record(profile, name, triggering=False, data=None):
    """Record a notification for the given profile."""
    if profile.user.email is None or not profile.user.is_active:
        return
    store.store(profile.id, name, triggering=triggering, data=data)
    # @@@ later this will be only if user prefers instant notifications
    if triggering and not getattr(settings, 'PORTFOLIYO_NO_EMAILS', False):
        tasks.send_notification_email.delay(profile.id)
