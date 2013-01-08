"""New-teacher notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from .base import NotificationTypeCollector



class NewTeacherVillage(object):
    """Encapsulates addition of a single teacher to a single village."""
    def __init__(self, teacher, student):
        self.teacher = teacher
        self.student = student


class NewTeacherVillageList(object):
    """Provides summary data about a list of ``NewTeacherVillage`` instances."""
    def __init__(self, villages):
        self.villages = villages

        self.teachers = set()
        self.teachers_by_student = {}
        self.students = set()
        self.students_by_teacher = {}

        for v in self.villages:
            self.teachers.add(v.teacher)
            self.students.add(v.student)
            self.teachers_by_student.setdefault(v.student, set()).add(v.teacher)
            self.students_by_teacher.setdefault(v.teacher, set()).add(v.student)



class NewTeacherCollector(NotificationTypeCollector):
    """
    Collects new-teacher notifications.

    Template context provided:

    ``new_teacher_villages`` is a ``NewTeacherVillageList``, which acts like a
    list of ``NewTeacherVillage`` instances, each with a ``teacher`` and
    ``student`` attribute, and also provides summary ``teachers``,
    ``students``, ``teachers_by_student``, and ``students_by_teacher``
    attributes.

    """
    type_name = types.NEW_TEACHER
    subject_template = 'notifications/activity/_new_teachers.subject.txt'
    db_lookup = {
        'teacher-id': (model.Profile, 'teacher'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {
            'new_teacher_villages': NewTeacherVillageList(
                [
                    NewTeacherVillage(n['teacher'], n['student'])
                    for n in self.notifications
                    ]
                )
            }
