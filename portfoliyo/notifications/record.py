"""Record notifications."""
from portfoliyo import tasks
from . import store



def parent_post(profile, post):
    """Notify ``profile`` that a parent posted ``post``."""
    triggering = profile.notify_parent_text
    data = {'post-id': post.id}
    _record(profile, 'parent post', triggering=triggering, data=data)



def teacher_post(profile, post):
    """Notify ``profile`` that a teacher posted ``post``."""
    triggering = profile.notify_teacher_post
    data = {'post-id': post.id}
    _record(profile, 'teacher post', triggering=triggering, data=data)



def new_parent(profile, signup):
    """
    Notify ``profile`` that a parent signed up.

    ``signup`` should be a ``TextSignup`` model instance.

    """
    triggering = profile.notify_new_parent
    data = {'signup-id': signup.id}
    _record(profile, 'new parent', triggering=triggering, data=data)



def added_to_village(profile, teacher, student):
    """Notify ``profile`` that ``teacher`` added them to ``student`` village."""
    triggering = profile.notify_added_to_village
    data = {'teacher-id': teacher.id, 'student-id': student.id}
    _record(profile, 'added to village', triggering=triggering, data=data)



def new_teacher(profile, teacher, student):
    """Notify ``profile`` that ``teacher`` joined ``student``s village."""
    triggering = profile.notify_joined_my_village
    data = {'teacher-id': teacher.id, 'student-id': student.id}
    _record(profile, 'new teacher', triggering=triggering, data=data)



def _record(profile, name, triggering=False, data=None):
    """Record a notification for the given profile."""
    store.store(profile.id, name, triggering=triggering, data=data)
    # @@@ later this will be only if user prefers instant notifications
    if triggering:
        tasks.send_notification.delay(profile.id)
