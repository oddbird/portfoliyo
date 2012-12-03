"""Tests for user models."""
from django.db import IntegrityError
import mock
import pytest

from portfoliyo import model
from portfoliyo.model.users.models import generate_code
from portfoliyo.tests import factories, utils



class TestSchool(object):
    def test_unicode(self):
        """Unicode representation is school name."""
        s = factories.SchoolFactory.build(name="Some School")

        assert unicode(s) == u"Some School"



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


    def test_unicode_email(self):
        """If no name, unicode of a Profile is email."""
        profile = factories.ProfileFactory.create(user__email="foo@example.com")

        assert unicode(profile) == u"foo@example.com"


    def test_unicode_role_in_context(self):
        """If no name/email, unicode of a Profile is its role_in_context."""
        profile = factories.ProfileFactory.build()
        profile.role_in_context = u"Foo"

        assert unicode(profile) == u"Foo"


    def test_unicode_role(self):
        """If no name/email/role_in_context, unicode Profile is its role."""
        profile = factories.ProfileFactory.build(role="Foo")

        assert unicode(profile) == u"Foo"


    def test_unicode_phone(self):
        """If no name/email/role, unicode of a Profile is its phone."""
        profile = factories.ProfileFactory.build(phone="+13216540987")

        assert unicode(profile) == u"+13216540987"


    def test_unicode_unknown(self):
        """If no name/role/phone/email, unicode of a Profile is <unknown>."""
        profile = factories.ProfileFactory.build()

        assert unicode(profile) == u"<unknown>"


    def test_name_or_role(self):
        """name_or_role property is name if present."""
        profile = factories.ProfileFactory.build(name="Foo")

        assert profile.name_or_role == u"Foo"


    def test_name_or_role_no_name(self):
        """name_or_role property is role if no name."""
        profile = factories.ProfileFactory.build(role="Role")

        assert profile.name_or_role == u"Role"


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

        assert list(rel.student.elders) == [rel.elder]


    def test_students(self):
        """student_relationships property is list of profiles."""
        rel = factories.RelationshipFactory.create()

        assert rel.elder.students == [rel.student]


    def test_create_dupe_code(self):
        """Robust against off-chance of duplicate teacher code."""
        school = factories.SchoolFactory()
        target = 'portfoliyo.model.users.models.generate_code'
        # we need the first two calls to return the same thing, and the
        # third call something different.
        calls = []
        def _mock_generate_code(seed, length):
            returns = ['ABCDEF', 'ABCDEF', 'FADCBE']
            calls.append(seed)
            return returns[len(calls)-1]
        with mock.patch(target, _mock_generate_code):
            p1 = model.Profile.create_with_user(school, school_staff=True)
            p2 = model.Profile.create_with_user(school, school_staff=True)

        assert p1.code != p2.code
        # different username passed to generate_code each time
        assert len(set(calls)) == 3


    def test_create_dupe_code_other_integrity_error(self):
        """If we get some other integrity error, just re-raise it."""
        school = factories.SchoolFactory()
        target = 'portfoliyo.model.users.models.Profile.save'
        with mock.patch(target) as mock_save:
            mock_save.side_effect = IntegrityError('foo')
            with pytest.raises(IntegrityError):
                model.Profile.create_with_user(school)


    def test_create_dupe_code_give_up(self):
        """If we get 10 dupes in a row, we give up and raise the error."""
        school = factories.SchoolFactory()
        target = 'portfoliyo.model.users.models.generate_code'
        with mock.patch(target) as mock_generate_code:
            mock_generate_code.return_value = 'ABCDEF'
            model.Profile.create_with_user(school, school_staff=True)
            with pytest.raises(IntegrityError):
                model.Profile.create_with_user(school, school_staff=True)



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


    def test_name_or_role(self):
        """name_or_role property is elder name if present."""
        rel = factories.RelationshipFactory.build(from_profile__name="Foo")

        assert rel.name_or_role == u"Foo"


    def test_name_or_role_no_name(self):
        """name_or_role property is description_or_role if no name."""
        rel = factories.RelationshipFactory.build(
            from_profile__name="", description="Desc")

        assert rel.name_or_role == u"Desc"


    def test_elder(self):
        """elder property is alias for from_profile."""
        rel = factories.RelationshipFactory.build()

        assert rel.elder is rel.from_profile


    def test_student(self):
        """student property is alias for to_profile."""
        rel = factories.RelationshipFactory.build()

        assert rel.student is rel.to_profile


    def test_delete_circularity(self):
        """Can delete a profile that has relationships."""
        rel = factories.RelationshipFactory.create()
        rel.elder.delete()


    def test_deletes_orphaned_student(self):
        """If deleting rel leaves student w/ no teachers, delete the student."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        rel.delete()

        assert utils.deleted(rel.student)



class TestGroup(object):
    """Tests for Group model."""
    def test_unicode(self):
        """Unicode representation is the name."""
        g = factories.GroupFactory.create(name="foo")

        assert unicode(g) == u"foo"


    def test_all_elders(self):
        """Queryset of elders of students in group, ordered by name."""
        rel = factories.RelationshipFactory.create(from_profile__name='B')
        e = factories.ProfileFactory.create(name='A')
        s = factories.ProfileFactory.create()
        g = factories.GroupFactory(owner=rel.elder)
        g.students.add(s, rel.student)
        g.elders.add(e)

        # alphabetically ordered by name
        assert [e.name for e in g.all_elders] == ['A', 'B']


    def test_elder_relationships(self):
        """elder_relationships prop is all relationships of group students."""
        rel = factories.RelationshipFactory()
        e = factories.ProfileFactory()
        s = factories.ProfileFactory()
        g = factories.GroupFactory()
        g.students.add(s, rel.student)
        g.elders.add(e)

        exp = set([(e, s), (e, rel.student), (rel.elder, rel.student)])
        assert set([(r.elder, r.student) for r in g.elder_relationships]) == exp


    def test_group_creates_relationships(self):
        """A group creates relationships between its students and elders."""
        s = factories.ProfileFactory.create()
        e = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        g.students.add(s)
        g.elders.add(e)

        rel = g.relationships.get()

        assert rel.elder == e
        assert rel.student == s
        assert not rel.direct
        assert set(rel.groups.all()) == {g}


    def test_no_create_dupe_relationship(self):
        """If a relationship already exists, don't re-create it."""
        rel = factories.RelationshipFactory.create()
        g = factories.GroupFactory.create()
        g.students.add(rel.student)
        g.elders.add(rel.elder)

        rel = utils.refresh(rel)

        assert rel.direct
        assert set(rel.groups.all()) == {g}


    def test_group_removes_relationships(self):
        """
        Removing group member removes matching relationships.

        (And does not remove non-group-originated relationships).

        """
        rel = factories.RelationshipFactory.create()
        s = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        g.students.add(s)
        g.elders.add(rel.elder)
        g.elders.remove(rel.elder)

        assert rel.elder.relationships_from.get() == rel


    def test_clears_relationships(self):
        """
        Clearing group members clears matching relationships.

        (And does not remove non-group-originated relationships).

        """
        rel = factories.RelationshipFactory.create()
        s = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        g.students.add(s)
        g.elders.add(rel.elder)
        g.elders.clear()

        assert rel.elder.relationships_from.get() == rel


    def test_double_group_relationships(self):
        """
        If student+elder in two groups, removing one doesn't remove relationship

        """
        e = factories.ProfileFactory.create()
        s = factories.ProfileFactory.create(school=e.school)
        g1 = factories.GroupFactory.create()
        g2 = factories.GroupFactory.create()
        g1.students.add(s)
        g1.elders.add(e)
        g2.students.add(s)
        g2.elders.add(e)
        g1.elders.clear()


        assert e.relationships_from.get().student == s


    def test_reverse_add_creates_relationship(self):
        """Adding a group to a student creates relationship."""
        s = factories.ProfileFactory.create()
        e = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        s.student_in_groups.add(g)
        e.elder_in_groups.add(g)

        rel = g.relationships.get()

        assert rel.elder == e
        assert rel.student == s
        assert not rel.direct
        assert set(rel.groups.all()) == {g}


    def test_reverse_add_no_dupe_relationship(self):
        """Adding a group to a student doesn't re-create dupe relationship."""
        rel = factories.RelationshipFactory.create()
        g = factories.GroupFactory.create()
        rel.student.student_in_groups.add(g)
        rel.elder.elder_in_groups.add(g)

        rel = utils.refresh(rel)

        assert rel.direct
        assert set(rel.groups.all()) == {g}


    def test_reverse_remove_removes_relationship(self):
        """
        Removing a group from an elder removes matching relationships.

        (And does not remove non-group-originated relationships).

        """
        s = factories.ProfileFactory.create()
        rel = factories.RelationshipFactory.create()
        g = factories.GroupFactory.create()
        s.student_in_groups.add(g)
        rel.elder.elder_in_groups.add(g)
        rel.elder.elder_in_groups.remove(g)

        assert rel.elder.relationships_from.get() == rel


    def test_reverse_clear_clears_relationships(self):
        """
        Clearing student groups clears matching relationships.

        (And does not remove non-group-originated relationships).

        (And calls events.student_removed for each cleared relationship.)

        """
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        e = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        g.students.add(rel.student)
        g.elders.add(e)

        target = 'portfoliyo.model.events.student_removed'
        with mock.patch(target) as mock_student_removed:
            rel.student.student_in_groups.clear()

        assert rel.student.relationships_to.get() == rel
        mock_student_removed.assert_called_with(rel.student, e)


    def test_create_dupe_code(self):
        """Robust against off-chance of duplicate group code."""
        target = 'portfoliyo.model.users.models.generate_code'
        # we need the first two calls to return the same thing, and the
        # third call something different.
        calls = []
        def _mock_generate_code(seed, length):
            returns = ['ABCDEFG', 'ABCDEFG', 'FADCBEA']
            calls.append(seed)
            return returns[len(calls)-1]
        with mock.patch(target, _mock_generate_code):
            g1 = factories.GroupFactory.create()
            g2 = factories.GroupFactory.create()

        assert g1.code != g2.code
        # different seed passed to generate_code each time
        assert len(set(calls)) == 3


    def test_create_dupe_code_other_integrity_error(self):
        """If we get some other integrity error, just re-raise it."""
        target = 'portfoliyo.model.users.models.models.Model.save'
        with mock.patch(target) as mock_save:
            mock_save.side_effect = IntegrityError('foo')
            with pytest.raises(IntegrityError):
                factories.GroupFactory.create()


    def test_create_dupe_code_give_up(self):
        """If we get 10 dupes in a row, we give up and raise the error."""
        target = 'portfoliyo.model.users.models.generate_code'
        with mock.patch(target) as mock_generate_code:
            mock_generate_code.return_value = 'ABCDEFG'
            factories.GroupFactory.create()
            with pytest.raises(IntegrityError):
                factories.GroupFactory.create()


    def test_delete_group_fires_event(self):
        """Pusher event is fired when group is deleted."""
        g = factories.GroupFactory.create()
        target = 'portfoliyo.model.events.group_removed'
        with mock.patch(target) as mock_group_removed:
            g.delete()

        mock_group_removed.assert_called_with(g)


    def test_create_group_fires_event(self):
        """Pusher event is fired when group is created."""
        target = 'portfoliyo.model.events.group_added'
        with mock.patch(target) as mock_group_added:
            g = factories.GroupFactory.create()

        mock_group_added.assert_called_with(g)


    def test_delete_relationship_removes_from_groups(self):
        """Deleting a relationship removes student from elder's groups."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        other_elder = factories.ProfileFactory.create()
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)
        group.elders.add(other_elder)

        rel.delete()

        assert not group.students.count()
        assert not other_elder.students


    def test_delete_relationship_does_not_cause_infinite_recursion(self):
        """Deleting rel doesn't cause infinite recursion if elder has groups."""
        rel = factories.RelationshipFactory.create()
        other_elder = factories.ProfileFactory.create()
        factories.GroupFactory.create(owner=other_elder)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)
        group.elders.add(other_elder)

        rel.delete()

        assert not group.students.count()
        assert not other_elder.students


    def test_add_student_to_group_event(self):
        """Adding a student to a group fires an event."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()

        target = 'portfoliyo.model.events.student_added_to_group'
        with mock.patch(target) as mock_student_added_to_group:
            g.students.add(s)

        mock_student_added_to_group.assert_called_with(g.owner, [s], [g])


    def test_add_student_to_group_reverse_event(self):
        """Adding a student to a group from the student fires an event."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()

        target = 'portfoliyo.model.events.student_added_to_group'
        with mock.patch(target) as mock_student_added_to_group:
            s.student_in_groups.add(g)

        mock_student_added_to_group.assert_called_with(g.owner, [s], [g])


    def test_remove_student_from_group_event(self):
        """Removing a student from a group fires an event."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()
        g.students.add(s)

        target = 'portfoliyo.model.events.student_removed_from_group'
        with mock.patch(target) as mock_student_removed_from_group:
            g.students.remove(s)

        mock_student_removed_from_group.assert_called_with(g.owner, [s], [g])


    def test_remove_student_from_group_reverse_event(self):
        """Removing a student from a group, via the student, fires an event."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()
        g.students.add(s)

        target = 'portfoliyo.model.events.student_removed_from_group'
        with mock.patch(target) as mock_student_removed_from_group:
            s.student_in_groups.remove(g)

        mock_student_removed_from_group.assert_called_with(g.owner, [s], [g])


    def test_clear_student_from_group_event(self):
        """Clearing students from a group fires events."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()
        g.students.add(s)

        target = 'portfoliyo.model.events.student_removed_from_group'
        with mock.patch(target) as mock_student_removed_from_group:
            g.students.clear()

        mock_student_removed_from_group.assert_called_with(g.owner, [s], [g])


    def test_clear_student_from_group_reverse_event(self):
        """Clearing groups from a student fires events."""
        g = factories.GroupFactory.create()
        s = factories.ProfileFactory.create()
        g.students.add(s)

        target = 'portfoliyo.model.events.student_removed_from_group'
        with mock.patch(target) as mock_student_removed_from_group:
            s.student_in_groups.clear()

        mock_student_removed_from_group.assert_called_with(g.owner, [s], [g])



class TestAllStudentsGroup(object):
    def test_elder_relationships(self):
        """Can get all elder relationships for all students."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel.elder)
        rel3 = factories.RelationshipFactory.create(to_profile=rel.student)
        g = model.AllStudentsGroup(rel.elder)

        assert set(g.elder_relationships) == set([rel, rel2, rel3])


    def test_students(self):
        """Can get all students in group."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel.elder)
        factories.RelationshipFactory.create(to_profile=rel.student)
        g = model.AllStudentsGroup(rel.elder)

        assert set(g.students) == set([rel.student, rel2.student])


    def test_all_elders(self):
        """Queryset of elders of students in group, ordered by name."""
        rel = factories.RelationshipFactory.create(from_profile__name='B')
        factories.RelationshipFactory.create(from_profile=rel.elder)
        factories.RelationshipFactory.create(
            from_profile__name='A', to_profile=rel.student)
        g = model.AllStudentsGroup(rel.elder)

        # alphabetically ordered by name
        assert [e.name for e in g.all_elders] == ['A', 'B']



class TestContextualizedElders(object):
    def test_relationships(self):
        """Given relationships, yields elders with role_in_context."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__role='foo')
        rel2 = factories.RelationshipFactory.create(
            description='bar')
        qs = model.contextualized_elders(model.Relationship.objects.all())

        assert set(qs) == {rel1.elder, rel2.elder}
        assert set([e.role_in_context for e in qs]) == {'foo', 'bar'}


    def test_profiles(self):
        """Given profiles, yields them with role_in_context."""
        elder1 = factories.ProfileFactory.create(role='foo')
        elder2 = factories.ProfileFactory.create(role='bar')
        qs = model.contextualized_elders(model.Profile.objects.all())

        assert set(qs) == {elder1, elder2}
        assert set([e.role_in_context for e in qs]) == {'foo', 'bar'}


    def test_must_be_profiles_or_relationships(self):
        """Raises ValueError if given unrecognized queryset."""
        with pytest.raises(ValueError):
            model.contextualized_elders(model.Group.objects.all())


    def test_can_filter_exclude(self):
        """Can filter/exclude a contextualized queryset of relationships."""
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create()
        qs = model.contextualized_elders(model.Relationship.objects.all())

        qs = qs.filter(
            pk__in=[rel1.elder.pk, rel2.elder.pk]
            ).exclude(pk=rel2.elder.pk)

        assert set(qs) == {rel1.elder}


    def test_can_order(self):
        """Can order a contextualized queryset of relationships."""
        rel1 = factories.RelationshipFactory.create(from_profile__name='B')
        rel2 = factories.RelationshipFactory.create(from_profile__name='A')
        qs = model.contextualized_elders(model.Relationship.objects.all())

        qs = qs.order_by('name')

        assert list(qs) == [rel2.elder, rel1.elder]



class TestGenerateCode(object):
    def test_too_many_ambiguous(self):
        """If most of original code is bad chars, maintain min length."""
        target = 'portfoliyo.model.users.models.base64.b32encode'
        with mock.patch(target) as mock_b32encode:
            mock_b32encode.return_value = '22222222222ABC'
            code = generate_code('foo', 6)

        assert code == 'ABCABC'
