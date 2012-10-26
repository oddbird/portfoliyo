"""Tests for village views."""
import datetime

from django.core import mail
from django.core.urlresolvers import reverse
from django import http
from django.utils.timezone import utc
import mock
import pytest

from portfoliyo.model import unread
from portfoliyo.view.village import views

from portfoliyo.tests import factories, utils




class GroupContextTests(object):
    """Common tests for views that maintain group context via querystring."""
    def test_maintain_group_context(self, client):
        """Can take ?group=id to maintain group nav context."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        response = client.get(
            self.url(rel.student) + '?group=%s' % group.id,
            user=rel.elder.user,
            )

        assert response.context['group'] == group


    def test_group_context_student_must_be_in_group(self, client):
        """?group=id not effective unless student is in group."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)

        response = client.get(
            self.url(rel.student) + '?group=%s' % group.id,
            user=rel.elder.user,
            )

        assert response.context['group'] is None


    def test_group_context_must_own_group(self, client):
        """?group=id not effective unless active user owns group."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        group = factories.GroupFactory.create()
        group.students.add(rel.student)

        response = client.get(
            self.url(rel.student) + '?group=%s' % group.id,
            user=rel.elder.user,
            )

        assert response.context['group'] is None


    def test_group_context_bad_id(self, client):
        """?group=id doesn't blow up with non-int id."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        response = client.get(
            self.url(rel.student) + '?group=all23',
            user=rel.elder.user,
            )

        assert response.context['group'] is None



class TestDashboard(object):
    def test_dashboard(self, client):
        """Asks user to pick a student."""
        rel = factories.RelationshipFactory(to_profile__name="Student Two")
        factories.RelationshipFactory(
            from_profile=rel.elder, to_profile__name="Student One")
        response = client.get(
            reverse('dashboard'), user=rel.elder.user, status=200)

        response.mustcontain("Please select a student")



class TestAddStudent(object):
    """Tests for add_student view."""
    def test_add_student(self, client):
        """User can add a student."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_student'), user=teacher.user).forms['add-student-form']
        form['name'] = "Some Student"
        response = form.submit()

        student = teacher.students[0]

        assert response.status_code == 302, response.body
        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': student.id}))


    def test_add_student_in_group(self, client):
        """User can add a student in a group context."""
        group = factories.GroupFactory.create(owner__school_staff=True)
        form = client.get(
            reverse('add_student_in_group', kwargs={'group_id': group.id }),
            user=group.owner.user,
            ).forms['add-student-form']
        form['name'] = "Some Student"
        response = form.submit()

        student = group.students.get()

        assert response.status_code == 302, response.body
        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': student.id}),
            ) + "?group=" + str(group.id)


    def test_validation_error(self, client):
        """Name of student must be provided."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_student'), user=teacher.user).forms['add-student-form']
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_school_staff(self, client):
        """Adding a student requires ``school_staff`` attribute."""
        someone = factories.ProfileFactory.create(school_staff=False)
        response = client.get(
            reverse('add_student'), user=someone.user, status=302).follow()

        response.mustcontain("don't have access"), response.html


    def test_anonymous_user_doesnt_blow_up(self, client):
        """Anonymous user on school-staff-required redirects gracefully."""
        response = client.get(reverse('add_student'), status=302).follow()

        assert "don't have access" in response.content



class TestEditStudent(GroupContextTests):
    """Tests for edit_student view."""
    def url(self, student=None):
        """Shortcut to get URL of edit-student view."""
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('edit_student', kwargs={'student_id': student.id})


    def test_edit_student(self, client):
        """User can edit a student."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        form = client.get(
            self.url(rel.student),
            user=rel.elder.user,
            ).forms['edit-student-form']
        form['name'] = "Some Student"
        response = form.submit(status=302)

        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': rel.student.id}))


    def test_maintain_group_context_on_redirect(self, client):
        """The group context is passed on through the form submission."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        form = client.get(
            self.url(rel.student) + '?group=%s' % group.id,
            user=rel.elder.user,
            ).forms['edit-student-form']
        form['name'] = "Some Student"
        response = form.submit().follow()

        assert response.context['group'] == group


    def test_validation_error(self, client):
        """Name of student must be provided."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        form = client.get(
            self.url(rel.student),
            user=rel.elder.user,
            ).forms['edit-student-form']
        form['name'] = ""
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_relationship(self, client):
        """Editing a student requires elder relationship."""
        someone = factories.ProfileFactory.create(school_staff=True)
        client.get(self.url(), user=someone.user, status=404)


    def test_requires_school_staff(self, client):
        """Editing a student requires ``school_staff`` attribute."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)
        response = client.get(
            self.url(rel.student), user=rel.elder.user, status=302).follow()

        response.mustcontain("don't have access"), response.html



class TestAddGroup(object):
    """Tests for add_group view."""
    def test_add_group(self, client):
        """User can add a group."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_group'), user=teacher.user).forms['add-group-form']
        form['name'] = "Some Group"
        response = form.submit(status=302)

        group = teacher.owned_groups.get()

        assert group.name == "Some Group"
        assert response['Location'] == utils.location(
            reverse('add_student_in_group', kwargs={'group_id': group.id}))


    def test_add_group_with_student(self, client):
        """User can add a group with a student."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        form = client.get(
            reverse('add_group'), user=rel.elder.user).forms['add-group-form']
        form['name'] = "Some Group"
        form['students'] = [str(rel.student.pk)]
        response = form.submit(status=302)

        group = rel.elder.owned_groups.get()

        assert set(group.students.all()) == {rel.student}
        assert response['Location'] == utils.location(
            reverse('group', kwargs={'group_id': group.id}))


    def test_validation_error(self, client):
        """Name of group must be provided."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_group'), user=teacher.user).forms['add-group-form']
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_school_staff(self, client):
        """Adding a group requires ``school_staff`` attribute."""
        someone = factories.ProfileFactory.create(school_staff=False)
        response = client.get(
            reverse('add_group'), user=someone.user, status=302).follow()

        response.mustcontain("don't have access"), response.html



class TestEditGroup(object):
    """Tests for edit_group view."""
    def url(self, group=None):
        """Shortcut to get URL of edit-group view."""
        if group is None:
            group = factories.GroupFactory.create()
        return reverse('edit_group', kwargs={'group_id': group.id})


    def test_edit_group(self, client):
        """User can edit a group."""
        group = factories.GroupFactory.create(owner__school_staff=True)
        form = client.get(
            self.url(group),
            user=group.owner.user,
            ).forms['edit-group-form']
        form['name'] = "Some Group"
        response = form.submit(status=302)

        assert response['Location'] == utils.location(
            reverse('group', kwargs={'group_id': group.id}))


    def test_validation_error(self, client):
        """Name of group must be provided."""
        group = factories.GroupFactory.create(
            owner__school_staff=True)
        form = client.get(
            self.url(group),
            user=group.owner.user,
            ).forms['edit-group-form']
        form['name'] = ""
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_owner(self, client):
        """Editing a group requires being its owner."""
        group = factories.GroupFactory.create(
            owner__school_staff=True)
        client.get(
            self.url(group),
            user=factories.ProfileFactory.create(school_staff=True).user,
            status=404,
            )



class TestInviteElders(GroupContextTests):
    """Tests for invite_elder view."""
    def url(self, student=None, group=None):
        assert student or group
        if group:
            return reverse(
                'invite_elder_to_group', kwargs=dict(group_id=group.id))
        return reverse('invite_elder', kwargs=dict(student_id=student.id))


    def test_invite_elder(self, client):
        """User can invite an elder."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        response = client.get(self.url(rel.student), user=rel.elder.user)
        form = response.forms['invite-elder-form']
        form['contact'] = "dad@example.com"
        form['relationship'] = "Father"
        response = form.submit(status=302)

        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': rel.student.id}))

        # invite email is sent to new elder
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [u'dad@example.com']

        # relationship with student is created
        assert rel.student.relationships_to.count() == 2


    def test_maintain_group_context_on_redirect(self, client):
        """The group context is passed on through the form submission."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        form = client.get(
            self.url(rel.student) + '?group=%s' % group.id,
            user=rel.elder.user,
            ).forms['invite-elder-form']
        form['contact'] = "dad@example.com"
        form['relationship'] = "Father"
        response = form.submit().follow()

        assert response.context['group'] == group


    def test_invite_elder_to_group(self, client):
        """User can invite an elder to a group."""
        group = factories.GroupFactory.create(owner__school_staff=True)
        response = client.get(self.url(group=group), user=group.owner.user)
        form = response.forms['invite-elder-form']
        form['contact'] = "dad@example.com"
        form['relationship'] = "Father"
        response = form.submit(status=302)

        assert response['Location'] == utils.location(
            reverse('group', kwargs={'group_id': group.id}))

        # group membership is created
        assert group.elders.count() == 1


    def test_neither_student_nor_group(self):
        """
        404 if neither student_id nor group_id given.

        Have to test this by calling view function directly, as the URLconf
        won't allow this to happen.

        """
        with pytest.raises(http.Http404):
            views.invite_elder(mock.Mock())


    def test_validation_error(self, client):
        """If one elder field is filled out, other must be too."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        response = client.get(self.url(rel.student), user=rel.elder.user)
        form = response.forms['invite-elder-form']
        form['contact'] = "(123)456-7890"
        form['relationship'] = ""
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_school_staff(self, client):
        """Inviting elders requires ``school_staff`` attribute."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)
        response = client.get(
            self.url(rel.student), user=rel.elder.user, status=302).follow()

        response.mustcontain("don't have access"), response.html


    def test_requires_school_staff_ajax(self, client):
        """An unauthenticated ajax request gets 403 not redirect."""
        rel = factories.RelationshipFactory.create()
        client.get(
            self.url(rel.student), user=rel.elder.user, ajax=True, status=403)


    def test_requires_relationship(self, client):
        """Only an elder of that student can invite more."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)



class TestVillage(GroupContextTests):
    """Tests for village chat view."""
    def url(self, student=None):
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('village', kwargs=dict(student_id=student.id))


    @pytest.mark.parametrize('link_target', ['invite_elder'])
    def test_link_only_if_staff(self, client, link_target):
        """Link with given target is only present for school staff."""
        parent_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)
        teacher_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=parent_rel.student)
        url = self.url(parent_rel.student)
        parent_response = client.get(url, user=parent_rel.elder.user)
        teacher_response = client.get(url, user=teacher_rel.elder.user)
        reverse_kwargs = {}
        if link_target == 'invite_elder':
            reverse_kwargs = {'student_id': parent_rel.student.id}
        target_url = reverse(link_target, kwargs=reverse_kwargs)
        parent_links = parent_response.html.findAll('a', href=target_url)
        teacher_links = teacher_response.html.findAll('a', href=target_url)

        assert len(teacher_links) == 1
        assert len(parent_links) == 0


    def test_requires_relationship(self, client):
        """Only an elder of that student can view village."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)


    def test_login_required_ajax(self, client):
        """An unauthenticated ajax request gets 403 not redirect."""
        client.get(self.url(), ajax=True, status=403)



class TestAllStudents(object):
    def url(self):
        return reverse('all_students')


    def test_all_students(self, client):
        """Can view an all-students page."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        client.get(self.url(), user=teacher.user, status=200)



class TestGroupDetail(object):
    """Tests for group chat view."""
    def url(self, group=None):
        if group is None:
            group = factories.GroupFactory.create()
        return reverse('group', kwargs=dict(group_id=group.id))


    def test_group_detail(self, client):
        """Can view a group detail page."""
        group = factories.GroupFactory.create(
            owner__school_staff=True)

        client.get(self.url(group), user=group.owner.user, status=200)


    def test_requires_ownership(self, client):
        """Only the owner of a group can view it."""
        group = factories.GroupFactory.create()
        someone = factories.ProfileFactory.create(
            school_staff=True, school=group.owner.school)

        client.get(self.url(group), user=someone.user, status=404)



class TestJsonPosts(object):
    """Tests for json_posts view."""
    def url(self, student=None, group=None):
        if student is not None:
            return reverse(
                'student_json_posts', kwargs=dict(student_id=student.id))
        elif group is not None:
            return reverse('group_json_posts', kwargs=dict(group_id=group.id))
        else:
            return reverse('json_posts')


    def test_marks_posts_read(self, client):
        """Loading the backlog marks all posts in village as read."""
        rel = factories.RelationshipFactory.create()
        post = factories.PostFactory.create(student=rel.student)
        post2 = factories.PostFactory.create(student=rel.student)
        unread.mark_unread(post, rel.elder)
        unread.mark_unread(post2, rel.elder)

        assert unread.is_unread(post, rel.elder)
        assert unread.is_unread(post2, rel.elder)

        client.get(self.url(rel.student), user=rel.elder.user)

        assert not unread.is_unread(post, rel.elder)
        assert not unread.is_unread(post2, rel.elder)


    def test_requires_relationship(self, client):
        """Only an elder of that student can get posts."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student=student), user=elder.user, status=404)


    def test_requires_group_owner(self, client):
        """Only the owner of a group can get its posts."""
        elder = factories.ProfileFactory.create(school_staff=True)
        group = factories.GroupFactory.create()

        client.get(self.url(group=group), user=elder.user, status=404)


    def test_create_post(self, no_csrf_client):
        """Creates a post and returns its JSON representation."""
        rel = factories.RelationshipFactory.create()

        response = no_csrf_client.post(
            self.url(rel.student), {'text': 'foo'}, user=rel.elder.user)

        assert response.json['success']
        posts = response.json['posts']
        assert len(posts) == 1
        post = posts[0]
        assert post['text'] == 'foo'
        assert post['author_id'] == rel.elder.id
        assert post['student_id'] == rel.student.id


    def test_create_post_with_sms_notifications(self, no_csrf_client):
        """Creates a post and sends SMSes."""
        rel = factories.RelationshipFactory.create(
            from_profile__name="Mr. Doe")
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student,
            from_profile__phone='+13216540987',
            from_profile__user__is_active=True,
            )

        target = 'portfoliyo.model.village.models.sms.send'
        with mock.patch(target) as mock_send_sms:
            response = no_csrf_client.post(
                self.url(rel.student),
                {'text': 'foo', 'sms-target': [other_rel.elder.id]},
                user=rel.elder.user,
                )

        post = response.json['posts'][0]
        assert post['meta']['sms'][0]['id'] == other_rel.elder.id
        mock_send_sms.assert_called_with("+13216540987", "foo --Mr. Doe")


    def test_create_group_post(self, no_csrf_client):
        """Creates a group post and returns its JSON representation."""
        group = factories.GroupFactory.create()

        response = no_csrf_client.post(
            self.url(group=group), {'text': 'foo'}, user=group.owner.user)

        assert response.json['success']
        posts = response.json['posts']
        assert len(posts) == 1
        post = posts[0]
        assert post['text'] == 'foo'
        assert post['author_id'] == group.owner.id
        assert post['group_id'] == group.id


    def test_create_all_students_post(self, no_csrf_client):
        """Creates an all-students post and returns its JSON representation."""
        elder = factories.ProfileFactory.create()

        response = no_csrf_client.post(
            self.url(), {'text': 'foo'}, user=elder.user)

        assert response.json['success']
        posts = response.json['posts']
        assert len(posts) == 1
        post = posts[0]
        assert post['text'] == 'foo'
        assert post['author_id'] == elder.id
        assert post['group_id'] == 'all%s' % elder.id


    def test_create_post_with_sequence_id(self, no_csrf_client):
        """Can include a sequence_id with post, will get it back."""
        rel = factories.RelationshipFactory.create()

        response = no_csrf_client.post(
            self.url(rel.student),
            {'text': 'foo', 'author_sequence_id': '5'},
            user=rel.elder.user,
            )

        assert response.json['posts'][0]['author_sequence_id'] == '5'


    def test_length_limit(self, no_csrf_client):
        """Error if post is too long."""
        rel = factories.RelationshipFactory.create(
            from_profile__name='Fred')

        response = no_csrf_client.post(
            self.url(rel.student),
            {'text': 'f' * 160},
            user=rel.elder.user,
            status=400,
            )

        # length limit is 160 - len('Fred: ')
        assert response.json == {
            'success': False,
            'error': "Posts are limited to 153 characters."
            }


    def test_get_posts(self, client):
        """Get backlog posts in chronological order."""
        rel = factories.RelationshipFactory.create(
            from_profile__name='Fred')

        post2 = factories.PostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 8, tzinfo=utc),
            author=rel.elder,
            student=rel.student,
            html_text='post2',
            )
        unread.mark_unread(post2, rel.elder)
        factories.PostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 5, tzinfo=utc),
            author=rel.elder,
            student=rel.student,
            html_text='post1',
            )
        # not in same village, shouldn't be returned
        factories.PostFactory()

        response = client.get(self.url(rel.student), user=rel.elder.user)

        posts = response.json['posts']
        assert [p['text'] for p in posts] == ['post1', 'post2']
        assert [p['unread'] for p in posts] == [False, True]


    def test_get_group_posts(self, client):
        """Get backlog group posts in chronological order."""
        group = factories.GroupFactory.create(
            owner__name='Fred')

        factories.BulkPostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 8, tzinfo=utc),
            author=group.owner,
            group=group,
            html_text='post1',
            )
        factories.BulkPostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 5, tzinfo=utc),
            author=group.owner,
            group=group,
            html_text='post2',
            )
        # not in same group, shouldn't be returned
        factories.BulkPostFactory()

        response = client.get(self.url(group=group), user=group.owner.user)

        posts = response.json['posts']
        assert [p['text'] for p in posts] == ['post2', 'post1']


    def test_get_all_student_posts(self, client):
        """Get backlog all-student posts in chronological order."""
        elder = factories.ProfileFactory.create()

        factories.BulkPostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 8, tzinfo=utc),
            author=elder,
            group=None,
            html_text='post1',
            )
        factories.BulkPostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 5, tzinfo=utc),
            author=elder,
            group=None,
            html_text='post2',
            )
        # not in all-students group, shouldn't be returned
        factories.BulkPostFactory()

        response = client.get(self.url(), user=elder.user)

        posts = response.json['posts']
        assert [p['text'] for p in posts] == ['post2', 'post1']


    def test_backlog_limit(self, client, monkeypatch):
        """There's a limit on number of posts returned."""
        rel = factories.RelationshipFactory.create(
            from_profile__name='Fred')

        factories.PostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 8, tzinfo=utc),
            author=rel.elder,
            student=rel.student,
            html_text='post1',
            )
        factories.PostFactory(
            timestamp=datetime.datetime(2012, 9, 17, 3, 5, tzinfo=utc),
            author=rel.elder,
            student=rel.student,
            html_text='post2',
            )

        monkeypatch.setattr(views, "BACKLOG_POSTS", 1)
        response = client.get(self.url(rel.student), user=rel.elder.user)

        posts = response.json['posts']
        assert [p['text'] for p in posts] == ['post1']



class TestMarkPostRead(object):
    def url(self, post):
        """URL to mark given post read."""
        return reverse('mark_post_read', kwargs={'post_id': post.id})


    def test_mark_read(self, no_csrf_client):
        """Can mark a post read with POST to dedicated URI."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        post = factories.PostFactory.create(student=rel.student)
        unread.mark_unread(post, rel.elder)

        no_csrf_client.post(
            self.url(post),
            user=rel.elder.user,
            status=202)

        assert not unread.is_unread(post, rel.elder)



class TestEditElder(object):
    def url(self, rel=None, elder=None, group=None):
        """rel is relationship between a student and elder to be edited."""
        assert elder or rel
        if rel:
            return reverse(
                'edit_elder_in_village',
                kwargs={'student_id': rel.student.id, 'elder_id': rel.elder.id},
                )
        elif group:
            return reverse(
                'edit_elder_in_group',
                kwargs={'elder_id': elder.id, 'group_id': group.id},
                )
        return reverse('edit_elder', kwargs={'elder_id': elder.id})


    def test_success(self, client):
        """School staff can edit profile of non school staff."""
        rel = factories.RelationshipFactory(
            from_profile__name='Old Name', from_profile__role='Old Role')
        editor_rel = factories.RelationshipFactory(
            from_profile__school_staff=True, to_profile=rel.to_profile)
        url = self.url(rel)

        form = client.get(
            url, user=editor_rel.elder.user).forms['edit-elder-form']
        form['name'] = 'New Name'
        form['role'] = 'New Role'
        res = form.submit(status=302)

        assert res['Location'] == utils.location(
            reverse('village', kwargs={'student_id': rel.student.id}))
        elder = utils.refresh(rel.elder)
        assert elder.name == 'New Name'
        assert elder.role == 'New Role'


    def test_error(self, client):
        """Test form redisplay with errors."""
        rel = factories.RelationshipFactory()
        editor_rel = factories.RelationshipFactory(
            from_profile__school_staff=True, to_profile=rel.to_profile)
        url = self.url(rel)

        form = client.get(
            url, user=editor_rel.elder.user).forms['edit-elder-form']
        form['name'] = 'New Name'
        form['role'] = ''
        res = form.submit(status=200)

        res.mustcontain('field is required')


    def test_in_group(self, client):
        """Can edit an elder from a group context."""
        elder = factories.ProfileFactory.create()
        editor = factories.ProfileFactory.create(
            school_staff=True, school=elder.school)
        group = factories.GroupFactory.create(owner=editor)
        group.elders.add(elder)

        form = client.get(
            self.url(elder=elder, group=group),
            user=editor.user,
            ).forms['edit-elder-form']
        form['name'] = 'New Name'
        form['role'] = 'New Role'
        form.submit()

        elder = utils.refresh(elder)
        assert elder.name == 'New Name'
        assert elder.role == 'New Role'


    def test_in_all_students_group(self, client):
        """Can edit an elder from the all-students group."""
        elder = factories.ProfileFactory.create()
        editor = factories.ProfileFactory.create(
            school_staff=True, school=elder.school)

        form = client.get(
            self.url(elder=elder), user=editor.user).forms['edit-elder-form']
        form['name'] = 'New Name'
        form['role'] = 'New Role'
        form.submit()

        elder = utils.refresh(elder)
        assert elder.name == 'New Name'
        assert elder.role == 'New Role'


    def test_school_staff_required(self, client):
        """Only school staff can access."""
        rel = factories.RelationshipFactory(
            from_profile__name='Old Name', from_profile__role='Old Role')
        editor_rel = factories.RelationshipFactory(
            from_profile__school_staff=False, to_profile=rel.to_profile)
        url = self.url(rel)

        res = client.get(
            url, user=editor_rel.elder.user, status=302).follow()

        res.mustcontain("don't have access")


    def test_cannot_edit_school_staff(self, client):
        """Cannot edit other school staff."""
        rel = factories.RelationshipFactory(
            from_profile__school_staff=True)
        editor_rel = factories.RelationshipFactory(
            from_profile__school_staff=True, to_profile=rel.to_profile)
        url = self.url(rel)

        client.get(url, user=editor_rel.elder.user, status=404)


    def test_requires_relationship(self, client):
        """Editing user must have relationship with student."""
        rel = factories.RelationshipFactory()
        editor = factories.ProfileFactory(school_staff=True)
        url = self.url(rel)

        client.get(url, user=editor.user, status=404)



class TestPdfParentInstructions(object):
    def test_basic(self, client):
        """Smoke test that we get a PDF response back and nothing breaks."""
        elder = factories.ProfileFactory.create(
            school_staff=True, code='ABCDEF')
        url = reverse('pdf_parent_instructions', kwargs={'lang': 'es'})
        resp = client.get(url, user=elder.user, status=200)

        assert resp.headers[
            'Content-Disposition'] == 'attachment; filename=instructions-es.pdf'
        assert resp.headers['Content-Type'] == 'application/pdf'


    def test_group(self, client):
        """Can get a PDF for a group code."""
        group = factories.GroupFactory.create(owner__school_staff=True)
        url = reverse(
            'pdf_parent_instructions_group',
            kwargs={'lang': 'en', 'group_id': group.id},
            )
        resp = client.get(url, user=group.owner.user, status=200)

        assert resp.headers[
            'Content-Disposition'] == 'attachment; filename=instructions-en.pdf'
        assert resp.headers['Content-Type'] == 'application/pdf'


    def test_must_own_group(self, client):
        """Can't get a PDF for a group that isn't yours."""
        group = factories.GroupFactory.create()
        someone = factories.ProfileFactory(school_staff=True)
        url = reverse(
            'pdf_parent_instructions_group',
            kwargs={'lang': 'en', 'group_id': group.id},
            )
        client.get(url, user=someone.user, status=404)


    def test_no_code(self, client):
        """Doesn't blow up if requesting user has no code."""
        elder = factories.ProfileFactory.create(school_staff=True)
        url = reverse('pdf_parent_instructions', kwargs={'lang': 'en'})
        resp = client.get(url, user=elder.user, status=200)

        assert resp.headers[
            'Content-Disposition'] == 'attachment; filename=instructions-en.pdf'
        assert resp.headers['Content-Type'] == 'application/pdf'


    def test_missing_template(self, client):
        """404 if template for requested lang is missing."""
        elder = factories.ProfileFactory.create(school_staff=True)
        url = reverse('pdf_parent_instructions', kwargs={'lang': 'en'})
        target = 'portfoliyo.view.village.views.os.path.isfile'
        with mock.patch(target) as mock_isfile:
            mock_isfile.return_value = False
            client.get(url, user=elder.user, status=404)
