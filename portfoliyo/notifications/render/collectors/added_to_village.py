"""Added-to-village notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from .base import NotificationTypeCollector



class AddedToVillage(object):
    def __init__(self, added_by, student):
        self.added_by = added_by
        self.student = student



class AddedToVillageCollector(NotificationTypeCollector):
    """
    Collects added-to-village notifications.

    Template context provided:

    ``added_to_village`` is a list of ``AddedToVillage`` instances, each with
    an ``added_by`` and ``student`` attribute, sorted by ``added_by``.

    """
    type_name = types.ADDED_TO_VILLAGE
    subject_template = 'notifications/activity/_added_to_villages.subject.txt'
    db_lookup = {
        'added-by-id': (model.Profile, 'added_by'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {
            'added_to_villages': [
                AddedToVillage(n['added_by'], n['student'])
                for n in sorted(
                    self.notifications, key=lambda x: x['added_by'])
                ],
            }
