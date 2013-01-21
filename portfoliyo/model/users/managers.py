from django.db import models
from django.db.models import query



class ProfileManager(models.Manager):
    def get_query_set(self):
        return ProfileQuerySet(self.model, using=self._db)


    def prefetch_elders(self):
        return self.get_query_set().prefetch_elders()


    def prefetch_students(self):
        return self.get_query_set().prefetch_students()


    def prefetch_relationships(self):
        return self.get_query_set().prefetch_relationships()



class ProfileQuerySet(query.QuerySet):
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


    def _do_prefetch(self):
        if self._prefetch_done or not (
                self._prefetch_elders or self._prefetch_students):
            # nothing to do
            return

        # result cache must be filled first if it is not already
        if self._result_cache is None:
            # easy efficient way to populate the result cache
            len(self)

        Relationship = self.model._meta.get_field_by_name(
            'relationships_to')[0].model

        filters = models.Q()
        if self._prefetch_elders:
            filters = filters | models.Q(to_profile__in=self._result_cache)
        if self._prefetch_elders:
            filters = filters | models.Q(from_profile__in=self._result_cache)

        elder_rels = Relationship.objects.filter(filters).select_related(
            'from_profile__user', 'to_profile__user')
        elders_by_student = {}
        students_by_elder = {}
        for rel in elder_rels:
            elders_by_student.setdefault(rel.student, []).append(rel)
            students_by_elder.setdefault(rel.elder, []).append(rel)
        for profile in self._result_cache:
            if self._prefetch_elders:
                qs = profile.elder_relationships
                qs._result_cache = sorted(
                    elders_by_student.get(profile, []),
                    key=lambda er: er.elder.name,
                    )
                profile._cached_elder_relationships = qs
            if self._prefetch_students:
                qs = profile.student_relationships
                qs._result_cache = sorted(
                    students_by_elder.get(profile, []),
                    key=lambda sr: sr.student.name,
                    )
                profile._cached_student_relationships = qs

        self._prefetch_done = True


    def __iter__(self):
        self._do_prefetch()
        return super(ProfileQuerySet, self).__iter__()
