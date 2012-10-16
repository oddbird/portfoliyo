"""Tests for model factories."""
import pytest

from portfoliyo.tests import factories


class TestRelationshipFactory(object):
    def test_same_school(self):
        """Relationship factory creates elder and student in same school."""
        rel = factories.RelationshipFactory.create()

        assert rel.elder.school == rel.student.school


    def test_same_explicit_elder_school(self):
        """Same school if elder school specified."""
        rel = factories.RelationshipFactory.create(
            from_profile__school=factories.SchoolFactory())

        assert rel.elder.school == rel.student.school


    def test_same_explicit_student_school(self):
        """Same school if student school specified."""
        rel = factories.RelationshipFactory.create(
            to_profile__school=factories.SchoolFactory())

        assert rel.elder.school == rel.student.school


    def test_explicit_student(self):
        """Same school if student explicitly specified."""
        rel = factories.RelationshipFactory.create(
            to_profile=factories.ProfileFactory())

        assert rel.elder.school == rel.student.school


    def test_cross_school_error(self):
        """Error on attempt to create cross-school relationship."""
        with pytest.raises(ValueError):
            factories.RelationshipFactory.create(
                to_profile=factories.ProfileFactory(),
                from_profile=factories.ProfileFactory(),
                )


    def test_specify_school(self):
        """Can specify school as if attribute of Relationship."""
        school = factories.SchoolFactory.create()
        rel = factories.RelationshipFactory.create(school=school)

        assert rel.student.school == school
        assert rel.elder.school == school
