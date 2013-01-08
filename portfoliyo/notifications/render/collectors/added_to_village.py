"""Added-to-village notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from . import base



class AddedToVillageCollector(base.NotificationTypeCollector):
    """
    Collects added-to-village notifications.

    Template context provided:

    ``added_to_village`` is a ``VillageList``.

    """
    type_name = types.ADDED_TO_VILLAGE
    subject_template = 'notifications/activity/_added_to_villages.subject.txt'
    db_lookup = {
        'added-by-id': (model.Profile, 'added_by'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {
            'added_to_villages': base.VillageList(
                [
                    base.Village(n['added_by'], n['student'])
                    for n in sorted(
                        self.notifications, key=lambda x: x['added_by'])
                    ],
                )
            }
