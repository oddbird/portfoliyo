"""Tests for user models."""
from django.contrib.auth import models as auth_models
from django.db import IntegrityError
import pytest

from .. import utils
from . import factories


class TestUser(object):
    """Tests for our monkeypatches to User model."""
    def test_unicode_email(self):
        """Unicode representation is email address, if present."""
        user = factories.UserFactory.build(email="foo@example.com")

        assert unicode(user) == u"foo@example.com"


    def test_unicode_name(self):
        """If no email, unicode representation is name."""
        profile = factories.ProfileFactory.create(
            user__email=None, name="John Doe")

        assert unicode(profile.user) == u"John Doe"


    def test_unicode_phone(self):
        """If no email or name, unicode representation is phone."""
        profile = factories.ProfileFactory.create(
            user__email=None, name="", phone="+13216540987")

        assert unicode(profile.user) == u"+13216540987"


    def test_unicode_fallback(self):
        """If no email/name/phone, unicode representation is <unknown>."""
        profile = factories.ProfileFactory.create(
            user__email=None, name="", phone=None)

        assert unicode(profile.user) == u"<unknown>"


    def test_email_can_be_None(self):
        """Email can be set to None."""
        user = factories.UserFactory.create(email=None)

        assert utils.refresh(user).email == None


    def test_email_can_be_long(self):
        """Email can be longer than 75 chars without truncation."""
        long_email = ('f' * 75) + '@example.com'
        user = factories.UserFactory.create(email=long_email)

        assert utils.refresh(user).email == long_email


    def test_email_unique(self):
        """Email must be unique."""
        factories.UserFactory.create(email="foo@example.com")

        with pytest.raises(IntegrityError):
            factories.UserFactory.create(email="foo@example.com")



class TestProfile(object):
    """Tests for Profile model."""
    def test_unicode(self):
        """Unicode representation of a Profile is its name."""
        profile = factories.ProfileFactory.build(name="Some Name")

        assert unicode(profile) == u"Some Name"


    def test_profile_autocreated(self):
        """A User without a profile gets one automatically on first access."""
        user = factories.UserFactory.create()

        assert user.profile is not None


    def test_profile_autocreated_even_after_select_related(self):
        """select_related('profile') doesn't break profile autocreation."""
        factories.UserFactory.create()
        user = auth_models.User.objects.select_related('profile').get()

        assert user.profile is not None


    def test_double_profile_access_after_select_related(self):
        """select_related('profile') doesn't break two profile accesses."""
        factories.UserFactory.create()
        user = auth_models.User.objects.select_related('profile').get()

        assert user.profile is not None
        assert user.profile is not None


    def test_site_staff_are_school_staff(self):
        """Any user with is_staff is also school_staff."""
        user = factories.UserFactory.create(is_staff=True)
        profile = factories.ProfileFactory.create(user=user)

        assert profile.school_staff


    def test_elder_relationships(self):
        """elder_relationships property is QS of Relationship objects."""
        rel = factories.RelationshipFactory.create()

        assert list(rel.student.elder_relationships) == [rel]


    def test_student_relationships(self):
        """student_relationships property is QS of Relationship objects."""
        rel = factories.RelationshipFactory.create()

        assert list(rel.elder.student_relationships) == [rel]


    def test_elders(self):
        """elders property is list of profiles."""
        rel = factories.RelationshipFactory.create()

        assert rel.student.elders == [rel.elder]


    def test_students(self):
        """student_relationships property is list of profiles."""
        rel = factories.RelationshipFactory.create()

        assert rel.elder.students == [rel.student]



class TestRelationship(object):
    """Tests for Relationship model."""
    def test_unicode(self):
        """Unicode representation includes all the things!"""
        rel = factories.RelationshipFactory.create(
            from_profile__name="Mom",
            to_profile__name="Kid",
            description="mother",
            )

        assert unicode(rel) == u"Mom is elder (mother) to Kid"


    def test_description_or_role(self):
        """description_or_role uses description if present"""
        rel = factories.RelationshipFactory.build(description="Foo")

        assert rel.description_or_role == u"Foo"


    def test_description_or_role_fallback(self):
        """description_or_role uses from_profile role if no description"""
        rel = factories.RelationshipFactory.build(
            from_profile__role="Bar", description="")

        assert rel.description_or_role == u"Bar"


    def test_elder(self):
        """elder property is alias for from_profile."""
        rel = factories.RelationshipFactory.build()

        assert rel.elder is rel.from_profile


    def test_student(self):
        """student property is alias for to_profile."""
        rel = factories.RelationshipFactory.build()

        assert rel.student is rel.to_profile
