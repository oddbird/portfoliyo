from django.db import models
from django.db.models import query



class PrefetchManager(models.Manager):
    """
    Generic prefetch manager.

    Eases implementation of bulk-prefetching any type of associated data for
    each model in a queryset, whether that associated data resides in the
    database or elsewhere.

    Allows attaching a prefetch function to a queryset long before that
    queryset is evaluated. When the queryset is evaluated, the prefetch
    function will be called only with those objects in the final result set.

    """
    def get_query_set(self):
        return PrefetchQuerySet(self.model, using=self._db)


    def prefetch(self, *args, **kw):
        return self.get_query_set().prefetch(*args, **kw)



class PrefetchQuerySet(query.QuerySet):
    """Generic prefetch queryset."""
    def __init__(self, *args, **kw):
        self._prefetches = []
        self._prefetch_done = False
        super(PrefetchQuerySet, self).__init__(*args, **kw)


    def prefetch(self, attr, func, *args, **kw):
        """
        Prefetch data using any function that returns a dictionary.

        Given prefetch ``func`` should accept an iterable of model instances as
        its first argument, and any other args/kwargs given. It should return a
        dictionary where the keys are model instances; the corresponding values
        will be assigned to each instance's ``attr`` attribute.

        """
        return self._clone(
            _prefetches=self._prefetches + [(func, attr, args, kw)])


    def _clone(self, *args, **kw):
        kw.setdefault('_prefetches', self._prefetches)
        return super(PrefetchQuerySet, self)._clone(*args, **kw)


    def _needs_prefetch(self):
        return self._prefetches


    def _prefetch_prep(self):
        """
        Assemble the prefetched data.

        Called early in the prefetch, but after the queryset's result-cache is
        populated.

        """
        self._prefetch_data = {}
        for func, attr, args, kw in self._prefetches:
            self._prefetch_data[attr] = func(self._result_cache, *args, **kw)


    def _prefetch_populate(self, obj):
        """Populate the given ``obj`` model instance with prefetched data. """
        for attr, values_dict in self._prefetch_data.iteritems():
            setattr(obj, attr, values_dict.get(obj, None))


    def _do_prefetch(self):
        """Execute prefetch (if any); called on iteration of the queryset."""
        if self._prefetch_done or not self._needs_prefetch():
            # nothing to do
            return

        # result cache must be filled first if it is not already
        if self._result_cache is None:
            # easy efficient way to populate the result cache
            len(self)

        self._prefetch_prep()

        for obj in self._result_cache:
            self._prefetch_populate(obj)

        self._prefetch_done = True


    def __iter__(self):
        self._do_prefetch()
        return super(PrefetchQuerySet, self).__iter__()



class ProfileManager(PrefetchManager):
    def get_query_set(self):
        return ProfileQuerySet(self.model, using=self._db)


    def prefetch_elders(self):
        return self.get_query_set().prefetch_elders()


    def prefetch_students(self):
        return self.get_query_set().prefetch_students()


    def prefetch_relationships(self):
        return self.get_query_set().prefetch_relationships()



class ProfileQuerySet(PrefetchQuerySet):
    def __init__(self, *args, **kw):
        self._prefetch_elders = False
        self._prefetch_students = False
        self._prefetch_done = False
        super(ProfileQuerySet, self).__init__(*args, **kw)


    def prefetch_elders(self):
        return self._clone(_prefetch_elders=True)


    def prefetch_students(self):
        return self._clone(_prefetch_students=True)


    def prefetch_relationships(self):
        return self._clone(_prefetch_elders=True, _prefetch_students=True)


    def _clone(self, *args, **kw):
        kw.setdefault('_prefetch_elders', self._prefetch_elders)
        kw.setdefault('_prefetch_students', self._prefetch_students)
        return super(ProfileQuerySet, self)._clone(*args, **kw)


    def _needs_prefetch(self):
        return (
            self._prefetch_elders or
            self._prefetch_students or
            super(ProfileQuerySet, self)._needs_prefetch()
            )


    def _prefetch_prep(self):
        super(ProfileQuerySet, self)._prefetch_prep()

        Relationship = self.model._meta.get_field_by_name(
            'relationships_to')[0].model

        filters = models.Q()
        if self._prefetch_elders:
            filters = filters | models.Q(to_profile__in=self._result_cache)
        if self._prefetch_elders:
            filters = filters | models.Q(from_profile__in=self._result_cache)

        elder_rels = Relationship.objects.filter(filters).select_related(
            'from_profile__user', 'to_profile__user')
        self._prefetch_elders_by_student = {}
        self._prefetch_students_by_elder = {}
        for rel in elder_rels:
            self._prefetch_elders_by_student.setdefault(
                rel.student, []).append(rel)
            self._prefetch_students_by_elder.setdefault(
                rel.elder, []).append(rel)


    def _prefetch_populate(self, obj):
        super(ProfileQuerySet, self)._prefetch_populate(obj)

        if self._prefetch_elders:
            qs = obj.elder_relationships
            qs._result_cache = sorted(
                self._prefetch_elders_by_student.get(obj, []),
                key=lambda er: er.elder.name,
                )
            obj._cached_elder_relationships = qs
        if self._prefetch_students:
            qs = obj.student_relationships
            qs._result_cache = sorted(
                self._prefetch_students_by_elder.get(obj, []),
                key=lambda sr: sr.student.name,
                )
            obj._cached_student_relationships = qs
