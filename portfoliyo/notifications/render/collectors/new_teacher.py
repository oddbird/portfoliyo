"""New-teacher notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from . import base



class NewTeacherCollector(base.NotificationTypeCollector):
    """
    Collects new-teacher notifications.

    Template context provided:

    ``new_teacher_villages`` is a ``VillageList``.

    """
    type_name = types.NEW_TEACHER
    subject_template = 'notifications/activity/_new_teachers.subject.txt'
    db_lookup = {
        'teacher-id': (model.Profile, 'teacher'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {
            'new_teacher_villages': base.VillageList(
                [
                    base.Village(n['teacher'], n['student'])
                    for n in self.notifications
                    ]
                )
            }
