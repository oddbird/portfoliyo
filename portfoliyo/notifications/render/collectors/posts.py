"""Post notification collector."""
from datetime import timedelta

from django.utils import timezone

from portfoliyo import model
from portfoliyo.notifications import types
from . import base



class Village(object):
    """
    Encapsulates a village with posts (some new, some context).

    ``new_posts`` and ``context_posts`` attributes are lists of serialized post
    dictionaries with unspecified ordering.

    ``posts`` attribute is an iterable combining both ``context_posts`` and
    ``new_posts`` in chronological ordering.

    """
    def __init__(self, student):
        self.student = student
        self.new_posts = []
        self._context_posts = None
        self._new_authors = []
        self.requested = False


    def posts(self):
        """All posts (new and context) in chronological order, serialized."""
        return sorted(
            self.new_posts + self.context_posts,
            key=lambda p: p['original_timestamp']
            )


    def add(self, notification):
        """Add a post notification to this collection."""
        assert notification['student'] == self.student
        if notification['triggering']:
            self.requested = True
        self.new_posts.append(
            self._serialize(notification['post'], new=True))
        author = notification['post'].author
        if author not in self._new_authors:
            self._new_authors.append(author)
        self._context_posts = None


    @property
    def context_posts(self):
        """List of context posts."""
        if self._context_posts is None:
            cutoff = timezone.now() - timedelta(hours=48)
            # get latest five posts in village, excluding the new ones
            latest = list(
                self.student.posts_in_village.exclude(
                    pk__in=[p['post_id'] for p in self.new_posts]).order_by(
                    '-timestamp')[:5]
                )
            # only keep those within last 48 hours
            ctx = [p for p in latest if p.timestamp > cutoff]
            # if there are posts but they are all old, keep one
            if latest and not ctx:
                ctx = list(latest)[-1:]
            self._context_posts = [self._serialize(p, new=False) for p in ctx]
        return self._context_posts


    def _serialize(self, post, **extra):
        """Transform ``Post`` instance into its serialized representation."""
        extra['plain_text'] = post.original_text
        extra['original_timestamp'] = post.timestamp
        return model.post_dict(post, **extra)



class PostCollector(base.NotificationTypeCollector):
    """
    Collects post notifications.

    Template context provided:

    ``villages`` is a list of ``Village`` objects containing at least one
    triggering (requested) notification.

    ``nonrequested_villages`` is a list of ``Village`` objects containing no
    triggering notifications.

    """
    type_name = types.POST
    subject_template = 'notifications/activity/_village_posts.subject.txt'
    db_lookup = {'post-id': (model.Post, 'post')}


    def get_context(self):
        villages = {}
        for notification in self.notifications:
            student = notification['student']
            village = villages.setdefault(student, Village(student))
            village.add(notification)

        requested = []
        nonrequested = []
        for village in villages.values():
            if village.requested:
                requested.append(village)
            else:
                nonrequested.append(village)

        return {'villages': requested, 'nonrequested_villages': nonrequested}


    def hydrate(self, data):
        """Add 'triggering' and 'student' keys to hydrated data."""
        hydrated = super(PostCollector, self).hydrate(data)
        hydrated['student'] = hydrated['post'].student
        hydrated['triggering'] = bool(data.get('triggering', False))
        return hydrated
