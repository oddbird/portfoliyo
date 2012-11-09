"""Tests for model factories."""
from portfoliyo.tests import factories


class TestRelationshipFactory(object):
    def test_same_school(self):
        """Relationship factory creates elder and student in same school."""
        rel = factories.RelationshipFactory.create()

        assert rel.elder.school == rel.student.school


    def test_explicit_student(self):
        """Same school if student explicitly specified."""
        rel = factories.RelationshipFactory.create(
            to_profile=factories.ProfileFactory())

        assert rel.elder.school == rel.student.school


    def test_specify_school(self):
        """Can specify school as if attribute of Relationship."""
        school = factories.SchoolFactory.create()
        rel = factories.RelationshipFactory.create(school=school)

        assert rel.student.school == school
        assert rel.elder.school == school
