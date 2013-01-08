"""New-teacher notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from .base import NotificationTypeCollector



class NewTeacherCollector(NotificationTypeCollector):
    """
    Collects new-teacher notifications.

    Template context provided:

    @@@

    """
    type_name = types.NEW_TEACHER
    subject_template = 'notifications/activity/_new_teachers.subject.txt'
    db_lookup = {
        'teacher-id': (model.Profile, 'teacher'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {}
