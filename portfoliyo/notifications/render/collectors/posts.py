"""Post notification collector."""
from datetime import timedelta

from django.utils import timezone

from portfoliyo import model
from portfoliyo.notifications import types
from . import base



def serialize_post(post, **extra):
    """Transform ``Post`` instance into its serialized representation."""
    extra['plain_text'] = post.original_text
    extra['original_timestamp'] = post.timestamp
    return model.post_dict(post, **extra)



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
        self.new_authors = []
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
            serialize_post(notification['post'], new=True))
        author = notification['post'].author
        if author not in self.new_authors:
            self.new_authors.append(author)
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
            self._context_posts = [serialize_post(p, new=False) for p in ctx]
        return self._context_posts



class PostCollector(base.NotificationTypeCollector):
    """
    Collects post notifications.

    Template context provided:

    ``requested_villages`` is a list of ``Village`` objects containing at least
    one triggering (requested) notification.

    ``nonrequested_villages`` is a list of ``Village`` objects containing no
    triggering notifications.

    ``villages`` is the union of ``requested_villages`` and
    ``nonrequested_villages``.

    """
    type_name = types.POST
    subject_template = 'notifications/activity/_village_posts.subject.txt'
    db_lookup = {'post-id': (model.Post, 'post')}


    def __init__(self, *args, **kw):
        super(PostCollector, self).__init__(*args, **kw)
        self._populated = False
        self._villages = None
        self._requested_villages = None
        self._nonrequested_villages = None


    def populate(self):
        if self._populated:
            return

        villages = {}
        for notification in self.notifications:
            student = notification['student']
            village = villages.setdefault(student, Village(student))
            village.add(notification)

        villages = villages.values()
        requested = []
        nonrequested = []
        for village in villages:
            if village.requested:
                requested.append(village)
            else:
                nonrequested.append(village)

        self._villages = villages
        self._requested_villages = sorted(
            requested, key=lambda v: v.student.name)
        self._nonrequested_villages = sorted(
            nonrequested, key=lambda v: v.student.name)


    def get_context(self):
        self.populate()
        return {
            'villages': self._villages,
            'requested_villages': self._requested_villages,
            'nonrequested_villages': self._nonrequested_villages,
            'any_requested_posts': self.any_requested(),
            'any_nonrequested_posts': self.any_nonrequested(),
            }


    def any_requested(self):
        self.populate()
        return bool(self._requested_villages)


    def any_nonrequested(self):
        self.populate()
        return bool(self._nonrequested_villages)


    def hydrate(self, data):
        """Add 'triggering' and 'student' keys to hydrated data."""
        hydrated = super(PostCollector, self).hydrate(data)
        hydrated['student'] = hydrated['post'].student
        hydrated['triggering'] = bool(int(data.get('triggering', False)))
        return hydrated
