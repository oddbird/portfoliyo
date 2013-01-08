"""Collect notifications and provide rendering info (templates and context)."""
import logging

from portfoliyo.notifications import store
from .collectors import COLLECTOR_CLASSES



logger = logging.getLogger(__name__)



DEFAULT_SUBJECT_TEMPLATE = 'notifications/activity.subject.txt'



class NotificationCollection(object):
    """Collects and aggregates all pending notifications for a given profile."""
    def __init__(self, profile_id):
        self.profile_id = profile_id

        self._notification_data = None
        self._hydrated = False
        self._collectors = None
        self._context = None


    @property
    def notification_data(self):
        """Raw notification data from storage."""
        if self._notification_data is None:
            self._notification_data = store.get_and_clear_all(self.profile_id)
        return self._notification_data


    @property
    def collectors(self):
        """Maps notification type names to ``NotificationTypeCollector``s."""
        if not self._hydrated:
            self._hydrate()
        return self._collectors


    @property
    def context(self):
        """Template context for rendering this collection of notifications."""
        if not self._hydrated:
            self._hydrate()
        return self._context


    def get_subject_template(self):
        """Get template name for email subject."""
        if len(self.collectors) > 1:
            subject_template = DEFAULT_SUBJECT_TEMPLATE
        else:
            collector = self.collectors.values()[0]
            subject_template = collector.subject_template

        return subject_template


    def _hydrate(self):
        collectors = {}
        for data in self.notification_data:
            name = data.pop('name', None)
            try:
                collector_class = COLLECTOR_CLASSES[name]
            except KeyError:
                logger.warning("Unknown notification type '%s'", name)
                continue
            # @@@ transform bulk posts that I only see in one village to single post
            collector = collectors.setdefault(name, collector_class())
            collector.add(data)

        # - clear out any empty collectors (e.g. from invalid data)
        # - populate template-rendering context and set of affected students
        context = {}
        students = set()
        for type_name, collector in collectors.items():
            if not collector:
                del collectors[type_name]
            context.update(collector.get_context())
            students.update(collector.get_students())

        context['students'] = students

        self._collectors = collectors
        self._context = context
        self._hydrated = True


    def __nonzero__(self):
        return bool(self.collectors)
