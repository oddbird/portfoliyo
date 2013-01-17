"""Bulk-post notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from . import base
from .posts import serialize_post



class VillageSet(object):
    """A set of villages that all received the same bulk posts."""
    def __init__(self, students):
        self.students = sorted(students, key=lambda s: s.name)
        # serialized bulk-posts, in unspecified order
        self._posts = []
        # teachers who authored the bulk posts
        self.teachers = []


    def add(self, bulk_post):
        """Add ``bulk_post``."""
        self._posts.append(serialize_post(bulk_post, new=True))
        if bulk_post.author not in self.teachers:
            self.teachers.append(bulk_post.author)


    def __len__(self):
        return len(self._posts)


    @property
    def posts(self):
        """Posts in chronological order."""
        return sorted(
            self._posts,
            key=lambda p: p['original_timestamp']
            )



class BulkPostCollection(object):
    """Organizes all bulk posts by teacher and village-set."""
    def __init__(self):
        # VillageSets by set of students
        self.village_sets = {}

        self.num_posts = 0
        self.students = set()
        self._teacher_set = set()
        self._teachers = None


    def add(self, bulk_post, students):
        student_set = frozenset(students)
        village_set = self.village_sets.setdefault(
            student_set, VillageSet(students))

        self.students.update(student_set)
        self.num_posts += 1
        self._teachers = None

        village_set.add(bulk_post)
        self._teacher_set.add(bulk_post.author)


    @property
    def teachers(self):
        if self._teachers is None:
            self._teachers = sorted(self._teacher_set, key=lambda t: t.name)
        return self._teachers


    def __len__(self):
        return self.num_posts



class BulkPostCollector(base.NotificationTypeCollector):
    """
    Collects bulk-post notifications.

    Template context provided:

    ``bulk_post_villagesets`` is a ``BulkPostCollection``.

    """
    type_name = types.BULK_POST
    subject_template = 'notifications/activity/_bulk_posts.subject.txt'
    db_lookup = {'bulk-post-id': (model.BulkPost, 'bulk-post')}


    def get_context(self):
        collection = BulkPostCollection()
        for n in self.notifications:
            collection.add(n['bulk-post'], n['students'])
        return {'bulk_posts': collection}


    def hydrate(self, data):
        """Determine how many villages I see this post in."""
        hydrated = super(BulkPostCollector, self).hydrate(data)
        bulk_post = hydrated['bulk-post']
        # triggered individual posts that are in villages I am in
        visible = list(
            bulk_post.triggered.filter(
                student__relationships_to__from_profile=self.profile).distinct(
                ).select_related('student')
            )
        # if only one triggered post is visible, treat it as a non-bulk post
        if len(visible) == 1:
            from .. import collect
            raise collect.SwitchType(
                types.POST,
                {'post-id': visible[0].id, 'triggering': data['triggering']}
                )
        elif not visible:
            raise base.RehydrationFailed()

        hydrated['students'] = [p.student for p in visible]

        return hydrated


    def get_students(self):
        return [s for n in self.notifications for s in n['students']]
