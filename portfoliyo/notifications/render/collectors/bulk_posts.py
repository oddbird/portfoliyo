"""Bulk-post notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from . import base


class VillageSet(object):
    """A set of villages that all received one or more bulk posts."""
    def __init__(self, students):
        self.students = students
        # bulk-post objects, in unspecified order
        self._posts = []


class BulkPostCollector(base.NotificationTypeCollector):
    """
    Collects bulk-post notifications.

    Template context provided:

    @@@

    """
    type_name = types.BULK_POST
    subject_template = 'notifications/activity/_bulk_posts.subject.txt'
    db_lookup = {'bulk-post-id': (model.BulkPost, 'bulk-post')}


    def get_context(self):
        return {}
