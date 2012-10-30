"""Tests for API resources."""
from django.core.urlresolvers import reverse
import mock

from portfoliyo.api import resources
from portfoliyo.model import unread
from portfoliyo.tests import factories, utils


class TestYAGNI(object):
    """
    Stub tests for methods we don't actually use yet.

    These methods were parallel to other methods I did need, so I went ahead
    and implemented them while I was in the area, but we don't actually use
    them yet. These tests are to achieve 100% coverage until they are used in
    earnest.

    """
    def test_cached_obj_get_list(self):
        r = resources.PortfoliyoResource()
        request = mock.Mock()
        target = 'portfoliyo.api.resources.ModelResource.cached_obj_get_list'
        with mock.patch(target) as mock_super:
            with mock.patch.object(
                    r, 'real_is_authorized') as mock_real_is_authorized:
                r.cached_obj_get_list(request, foo='bar')

        mock_real_is_authorized.assert_called_with(request)
        mock_super.assert_called_with(request, foo='bar')


    def test_cached_obj_get(self):
        r = resources.PortfoliyoResource()
        request = mock.Mock()
        target = 'portfoliyo.api.resources.ModelResource.cached_obj_get'
        with mock.patch(target) as mock_super:
            with mock.patch.object(
                    r, 'real_is_authorized') as mock_real_is_authorized:
                r.cached_obj_get(request, foo='bar')

        mock_real_is_authorized.assert_called_with(
            request, mock_super.return_value)
        mock_super.assert_called_with(request, foo='bar')



class TestProfileResource(object):
    def test_dehydrate_email(self):
        email = 'foo@example.com'
        bundle = mock.Mock()
        bundle.obj.user.email = email

        assert resources.ProfileResource().dehydrate_email(bundle) == email


    def list_url(self):
        """Get profile list API url."""
        return reverse(
            'api_dispatch_list',
            kwargs={
                'resource_name': 'user',
                'api_name': 'v1',
                },
            )


    def detail_url(self, profile):
        """Get detail API url for given profile."""
        return reverse(
            'api_dispatch_detail',
            kwargs={
                'resource_name': 'user',
                'api_name': 'v1',
                'pk': profile.pk,
                },
            )


    def test_ordering(self, no_csrf_client):
        """Users ordered alphabetically."""
        p = factories.ProfileFactory.create(name='B', school_staff=True)
        factories.ProfileFactory.create(name='A', school=p.school)

        response = no_csrf_client.get(self.list_url(), user=p.user)
        profiles = response.json['objects']

        assert [p['name'] for p in profiles] == ['A', 'B']


    def test_only_see_same_school_users(self, no_csrf_client):
        """Users can only see other users from same school in API."""
        p1 = factories.ProfileFactory.create()
        factories.ProfileFactory.create()
        hero = factories.ProfileFactory.create(
            school_staff=True, school=p1.school)

        response = no_csrf_client.get(self.list_url(), user=hero.user)
        objects = response.json['objects']

        assert len(objects) == 2
        assert set([p['id'] for p in objects]) == set([p1.pk, hero.pk])


    def test_village_uri(self, no_csrf_client):
        """Each profile has a village_uri in the API response."""
        s = factories.ProfileFactory.create(school_staff=True)
        village_url = reverse('village', kwargs={'student_id': s.id})

        response = no_csrf_client.get(self.list_url(), user=s.user)

        assert response.json['objects'][0]['village_uri'] == village_url


    def test_relationship_uri(self, no_csrf_client):
        """relationship_uri is relationship of querying elder with student."""
        rel = factories.RelationshipFactory.create()
        rel_url = reverse(
            'api_dispatch_detail',
            kwargs={
                'api_name': 'v1',
                'resource_name': 'relationship',
                'pk': rel.id,
                },
            )

        response = no_csrf_client.get(self.list_url(), user=rel.elder.user)

        assert response.json['objects'][0]['relationship_uri'] == rel_url


    def test_unread_count(self, no_csrf_client):
        """Each profile has an unread_count in the API response."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        post = factories.PostFactory.create(student=rel.student)
        unread.mark_unread(post, rel.elder)

        response = no_csrf_client.get(self.list_url(), user=rel.elder.user)

        assert response.json['objects'][0]['unread_count'] == 1


    def test_edit_student_uri(self, no_csrf_client):
        """Each profile has an edit_student_uri in the API response."""
        s = factories.ProfileFactory.create(school_staff=True)
        edit_url = reverse('edit_student', kwargs={'student_id': s.id})

        response = no_csrf_client.get(self.list_url(), user=s.user)

        assert response.json['objects'][0]['edit_student_uri'] == edit_url


    def test_filter_by_elder(self, no_csrf_client):
        """Can filter profiles by elders."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            school=rel.elder.school, from_profile__school_staff=True)

        response = no_csrf_client.get(
            self.list_url() + '?elders=' + str(rel.elder.pk),
            user=rel2.elder.user,
            )
        objects = response.json['objects']

        assert len(objects) == 1
        assert objects[0]['id'] == rel.student.pk


    def test_filter_by_student(self, no_csrf_client):
        """Can filter profiles by students."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            school=rel.elder.school, from_profile__school_staff=True)

        response = no_csrf_client.get(
            self.list_url() + '?students=' + str(rel.student.pk),
            user=rel2.elder.user,
            )
        objects = response.json['objects']

        assert len(objects) == 1
        assert objects[0]['id'] == rel.elder.pk


    def test_filter_by_elder_in_group(self, no_csrf_client):
        """Can filter profiles by group elder memberships."""
        s1 = factories.ProfileFactory.create()
        s2 = factories.ProfileFactory.create(school=s1.school)
        group = factories.GroupFactory.create(owner__school=s1.school)
        group.students.add(s1)
        group.elders.add(s2)

        response = no_csrf_client.get(
            self.list_url() + '?elder_in_groups=' + str(group.pk),
            user=factories.ProfileFactory.create(
                school=s1.school, school_staff=True).user,
            )
        objects = response.json['objects']

        assert len(objects) == 1
        assert objects[0]['id'] == s2.pk


    def test_filter_by_student_in_group(self, no_csrf_client):
        """Can filter profiles by group student memberships."""
        s1 = factories.ProfileFactory.create()
        s2 = factories.ProfileFactory.create(school=s1.school)
        group = factories.GroupFactory.create(owner__school=s1.school)
        group.students.add(s1)
        group.elders.add(s2)

        response = no_csrf_client.get(
            self.list_url() + '?student_in_groups=' + str(group.pk),
            user=factories.ProfileFactory.create(
                school=s1.school, school_staff=True).user,
            )
        objects = response.json['objects']

        assert len(objects) == 1
        assert objects[0]['id'] == s1.pk



class TestElderRelationshipResource(object):
    def list_url(self):
        """Get relationship list API url."""
        return reverse(
            'api_dispatch_list',
            kwargs={
                'resource_name': 'relationship',
                'api_name': 'v1',
                },
            )


    def detail_url(self, rel):
        """Get detail API url for given relationship."""
        return reverse(
            'api_dispatch_detail',
            kwargs={
                'resource_name': 'relationship',
                'api_name': 'v1',
                'pk': rel.pk,
                },
            )


    def test_only_see_own_relationships(self, no_csrf_client):
        """Users can only see their own relationships."""
        rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create()

        response = no_csrf_client.get(self.list_url(), user=rel.elder.user)
        objects = response.json['objects']

        assert len(objects) == 1
        assert set([r['id'] for r in objects]) == {rel.pk}


    def test_delete_relationship(self, no_csrf_client):
        """A user may delete their own relationship."""
        rel = factories.RelationshipFactory.create()

        no_csrf_client.delete(
            self.detail_url(rel), user=rel.elder.user, status=204)

        assert utils.deleted(rel)


    def test_delete_relationships_from_list(self, no_csrf_client):
        """A user may delete their own relationship via list URL."""
        rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            from_profile=rel.elder)

        no_csrf_client.delete(
            self.list_url() + "?student=%s" % rel.student.pk,
            user=rel.elder.user,
            status=204,
            )

        assert utils.deleted(rel)
        assert not utils.deleted(other_rel)


    def test_delete_relationship_removes_from_groups(self, no_csrf_client):
        """Deleting relationship removes students from my groups, too."""
        rel = factories.RelationshipFactory.create()
        g = factories.GroupFactory.create(owner=rel.elder)
        g2 = factories.GroupFactory.create(owner__school=rel.elder.school)
        rel.student.student_in_groups.add(g, g2)

        no_csrf_client.delete(
            self.detail_url(rel), user=rel.elder.user, status=204)

        assert set(rel.student.student_in_groups.all()) == {g2}


    def test_cannot_delete_other_rel(self, no_csrf_client):
        """Another user may not delete a relationship that is not theirs."""
        rel = factories.RelationshipFactory.create()
        other = factories.ProfileFactory.create()

        no_csrf_client.delete(self.detail_url(rel), user=other.user, status=404)

        assert not utils.deleted(rel)


    def test_delete_rel_csrf_protected(self, client):
        """Deletion is CSRF-protected."""
        rel = factories.RelationshipFactory.create()

        client.delete(self.detail_url(rel), user=rel.elder.user, status=403)




class TestGroupResource(object):
    def list_url(self):
        """Get list API url."""
        return reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'group', 'api_name': 'v1'},
            )


    def detail_url(self, group):
        """Get detail API url for given group."""
        return reverse(
            'api_dispatch_detail',
            kwargs={'resource_name': 'group', 'api_name': 'v1', 'pk': group.pk},
            )


    def test_unread_count(self, no_csrf_client):
        """Each group has an unread_count in the API response."""
        rel = factories.RelationshipFactory.create()
        post = factories.PostFactory.create(student=rel.student)
        other_rel = factories.RelationshipFactory.create(from_profile=rel.elder)
        other_post = factories.PostFactory.create(student=other_rel.student)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)
        group.students.add(other_rel.student)
        unread.mark_unread(post, rel.elder)
        unread.mark_unread(other_post, rel.elder)

        response = no_csrf_client.get(self.list_url(), user=rel.elder.user)

        assert response.json['objects'][1]['unread_count'] == 2
        # all-students group also has unread count
        assert response.json['objects'][0]['unread_count'] == 2


    def test_only_see_my_groups(self, no_csrf_client):
        """User can only see their own groups in API, not even same-school."""
        g1 = factories.GroupFactory.create()
        factories.GroupFactory.create(owner__school=g1.owner.school)

        response = no_csrf_client.get(self.list_url(), user=g1.owner.user)
        objects = response.json['objects']

        assert len(objects) == 2
        assert {g['id'] for g in objects} == {g1.pk, 'all%s' % g1.owner.id}


    def test_all_students_group(self, no_csrf_client):
        """All-students group always included in groups list."""
        rel = factories.RelationshipFactory.create()

        response = no_csrf_client.get(self.list_url(), user=rel.elder.user)
        g = response.json['objects'][0]

        assert g['id'] == 'all%s' % rel.elder.id
        assert g['name'] == 'All Students'
        assert g['students_uri'] == reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'user', 'api_name': 'v1'},
            ) + '?elders=%s' % rel.elder.id
        assert g['add_student_uri'] == reverse('add_student')
        assert g['group_uri'] == reverse('all_students')
        assert g['owner'] == reverse(
            'api_dispatch_detail',
            kwargs={
                'resource_name': 'user', 'api_name': 'v1', 'pk': rel.elder.id},
            )


    def test_group_ordering(self, no_csrf_client):
        """Groups ordered alphabetically, with All Students first."""
        g = factories.GroupFactory.create(name='B')
        factories.GroupFactory.create(name='A', owner=g.owner)

        response = no_csrf_client.get(self.list_url(), user=g.owner.user)
        groups = response.json['objects']

        assert [g['name'] for g in groups] == ['All Students', 'A', 'B']


    def test_delete_group(self, no_csrf_client):
        """Owner of a group can delete it."""
        group = factories.GroupFactory.create()

        no_csrf_client.delete(
            self.detail_url(group), user=group.owner.user, status=204)

        assert utils.deleted(group)


    def test_delete_group_requires_owner(self, no_csrf_client):
        """Non-owner cannot delete a group, even if school staff."""
        group = factories.GroupFactory.create()
        profile = factories.ProfileFactory.create(school=group.owner.school)

        no_csrf_client.delete(
            self.detail_url(group), user=profile.user, status=404)

        assert not utils.deleted(group)


    def test_group_uri(self, no_csrf_client):
        """Each group has a group_uri for use in the web UI."""
        g = factories.GroupFactory.create()
        group_url = reverse('group', kwargs={'group_id': g.id})

        response = no_csrf_client.get(self.list_url(), user=g.owner.user)

        assert response.json['objects'][1]['group_uri'] == group_url


    def test_add_student_uri(self, no_csrf_client):
        """Each group has an add_student_uri for use in the web UI."""
        g = factories.GroupFactory.create()
        add_student_url = reverse(
            'add_student_in_group', kwargs={'group_id': g.id})

        response = no_csrf_client.get(self.list_url(), user=g.owner.user)

        assert response.json['objects'][1]['add_student_uri'] == add_student_url


    def test_students_uri(self, no_csrf_client):
        """Each group has a students_uri for fetching its student list."""
        g = factories.GroupFactory.create()
        students_url = reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'user', 'api_name': 'v1'},
            ) + '?student_in_groups=' + str(g.pk)

        response = no_csrf_client.get(self.list_url(), user=g.owner.user)

        assert response.json['objects'][1]['students_uri'] == students_url


    def test_edit_uri(self, no_csrf_client):
        """Each group has an edit_uri in the API response."""
        g = factories.GroupFactory.create()
        edit_url = reverse('edit_group', kwargs={'group_id': g.id})

        response = no_csrf_client.get(self.list_url(), user=g.owner.user)

        assert response.json['objects'][1]['edit_uri'] == edit_url



class TestPostResource(object):
    def list_url(self):
        """Get list API url."""
        return reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'post', 'api_name': 'v1'},
            )


    def detail_url(self, post):
        """Get detail API url for given post."""
        return reverse(
            'api_dispatch_detail',
            kwargs={'resource_name': 'post', 'api_name': 'v1', 'pk': post.pk},
            )


    def test_unread_count(self, no_csrf_client):
        """Each post has an unread boolean in the API response."""
        rel = factories.RelationshipFactory.create()
        post = factories.PostFactory.create(student=rel.student)
        unread.mark_unread(post, rel.elder)

        response = no_csrf_client.get(
            self.detail_url(post), user=rel.elder.user)

        assert response.json['unread'] == True
