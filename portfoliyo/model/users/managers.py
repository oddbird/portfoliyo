from django.db import models
from django.db.models import query



class ProfileManager(models.Manager):
    def get_query_set(self):
        return ProfileQuerySet(self.model, using=self._db)


    def prefetch_elders(self):
        return self.get_query_set().prefetch_elders()



class ProfileQuerySet(query.QuerySet):
    def __init__(self, *args, **kw):
        self._prefetch_elders = False
        self._prefetch_done = False
        super(ProfileQuerySet, self).__init__(*args, **kw)


    def prefetch_elders(self):
        return self._clone(_prefetch_elders=True)


    def _do_prefetch(self):
        if self._prefetch_done or not self._prefetch_elders:
            # nothing to do
            return

        # result cache must be filled
        if self._result_cache is None:
            # efficient way to populate the result cache
            len(self)

        Relationship = self.model._meta.get_field_by_name(
            'relationships_to')[0].model
        elder_rels = Relationship.objects.filter(
            to_profile__in=self._result_cache).order_by(
            'from_profile__name').select_related(
            'from_profile__user', 'to_profile__user')
        by_student = {}
        for rel in elder_rels:
            by_student.setdefault(rel.student, []).append(rel)
        for student in self._result_cache:
            qs = student.elder_relationships
            qs._result_cache = by_student.get(student, [])
            student._cached_elder_relationships = qs

        self._prefetch_done = True


    def __iter__(self):
        self._do_prefetch()
        return super(ProfileQuerySet, self).__iter__()
