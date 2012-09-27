"""Tests for village views."""
import datetime

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
import mock
import pytest

from portfoliyo.view.village import views

from portfoliyo.tests import factories, utils




class TestDashboard(object):
    def test_dashboard(self, client):
        """A picklist of students."""
        rel = factories.RelationshipFactory(to_profile__name="Student Two")
        factories.RelationshipFactory(
            from_profile=rel.elder, to_profile__name="Student One")
        response = client.get(
            reverse('dashboard'), user=rel.elder.user, status=200)

        response.mustcontain("Please select a student")
        response.mustcontain("Student One")
        response.mustcontain("Student Two")
        # alphabetical ordering
        c = response.content
        assert c.index("Student One") < c.index("Student Two")



class TestAddStudent(object):
    """Tests for add_student view."""
    def test_add_student(self, client):
        """User can add a student and invite some elders."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_student'), user=teacher.user).forms['add-student-form']
        form['name'] = "Some Student"
        form['elders-0-contact'] = "(123)456-7890"
        form['elders-0-relationship'] = "Father"
        form['elders-0-school_staff'] = False
        response = form.submit()

        student = teacher.students[0]

        assert response.status_code == 302, response.body
        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': student.id}))


    def test_validation_error(self, client):
        """Name of student must be provided."""
        teacher = factories.ProfileFactory.create(school_staff=True)
        form = client.get(
            reverse('add_student'), user=teacher.user).forms['add-student-form']
        form['elders-0-contact'] = "(123)456-7890"
        form['elders-0-relationship'] = "Father"
        form['elders-0-school_staff'] = False
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_school_staff(self, client):
        """Adding a student requires ``school_staff`` attribute."""
        someone = factories.ProfileFactory.create(school_staff=False)
        response = client.get(
            reverse('add_student'), user=someone.user, status=302).follow()

        response.mustcontain("account doesn't have access"), response.html


    def test_anonymous_user_doesnt_blow_up(self, client):
        """Anonymous user on school-staff-required redirects gracefully."""
        response = client.get(reverse('add_student'), status=302).follow()

        assert not "account doesn't have access" in response.content



class TestInviteElders(object):
    """Tests for invite_elders view."""
    def url(self, student=None):
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('invite_elders', kwargs=dict(student_id=student.id))


    def test_invite_elders(self, client):
        """User can invite some elders."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        response = client.get(self.url(rel.student), user=rel.elder.user)
        form = response.forms['invite-elders-form']
        form['elders-0-contact'] = "dad@example.com"
        form['elders-0-relationship'] = "Father"
        form['elders-0-school_staff'] = False
        response = form.submit(status=302)

        assert response['Location'] == utils.location(
            reverse('village', kwargs={'student_id': rel.student.id}))

        # invite email is sent to new elder
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [u'dad@example.com']


    def test_validation_error(self, client):
        """If one elder field is filled out, other must be too."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)
        response = client.get(self.url(rel.student), user=rel.elder.user)
        form = response.forms['invite-elders-form']
        form['elders-0-contact'] = "(123)456-7890"
        form['elders-0-relationship'] = ""
        form['elders-0-school_staff'] = False
        response = form.submit(status=200)

        response.mustcontain("field is required")


    def test_requires_school_staff(self, client):
        """Inviting elders requires ``school_staff`` attribute."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)
        response = client.get(
            self.url(rel.student), user=rel.elder.user, status=302).follow()

        response.mustcontain("account doesn't have access"), response.html


    def test_requires_relationship(self, client):
        """Only an elder of that student can invite more."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)



class TestVillage(object):
    """Tests for village chat view."""
    def url(self, student=None):
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('village', kwargs=dict(student_id=student.id))


    @pytest.mark.parametrize('link_target', ['add_student', 'invite_elders'])
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
        if link_target == 'invite_elders':
            reverse_kwargs = {'student_id': parent_rel.student.id}
        target_url = reverse(link_target, kwargs=reverse_kwargs)
        parent_links = parent_response.html.findAll('a', href=target_url)
        teacher_links = teacher_response.html.findAll('a', href=target_url)

        assert len(teacher_links) == 1
        assert len(parent_links) == 0


    @pytest.mark.parametrize('button_name', ['remove'])
    def test_button_only_if_staff(self, client, button_name):
        """Button with given name is only present for school staff."""
        parent_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)
        teacher_rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True, to_profile=parent_rel.student)
        url = self.url(parent_rel.student)
        parent_response = client.get(url, user=parent_rel.elder.user)
        teacher_response = client.get(url, user=teacher_rel.elder.user)
        parent_links = parent_response.html.findAll('button', dict(name=button_name))
        teacher_links = teacher_response.html.findAll('button', dict(name=button_name))

        assert len(teacher_links) == 1
        assert len(parent_links) == 0


    def test_requires_relationship(self, client):
        """Only an elder of that student can view village."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)


    def test_remove_student(self, no_csrf_client):
        """POSTing 'remove': student-id to village view soft-deletes student."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        resp = no_csrf_client.post(
            self.url(rel.student),
            {'remove': rel.student.id},
            user=rel.elder.user,
            status=302,
            )

        assert utils.refresh(rel.student).deleted
        assert resp['Location'] == utils.location(reverse('add_student'))


    def test_remove_student_ajax(self, no_csrf_client):
        """POSTing 'remove': student-id via ajax returns JSON, not redirect."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        resp = no_csrf_client.post(
            self.url(rel.student),
            {'remove': rel.student.id},
            user=rel.elder.user,
            status=200,
            ajax=True,
            )

        assert utils.refresh(rel.student).deleted
        assert resp.json['success'] == True


    def test_remove_student_requires_school_staff(self, no_csrf_client):
        """POSTing 'remove' to village view does nothing if not school staff."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False)

        no_csrf_client.post(
            self.url(rel.student),
            {'remove': rel.student.id},
            user=rel.elder.user,
            status=302,
            )

        assert not utils.refresh(rel.student).deleted


    def test_edit_student(self, no_csrf_client):
        """POSTing 'name' to village view edits student name."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            to_profile__name='Old Name',
            )

        no_csrf_client.post(
            self.url(rel.student),
            {'name': 'New Name'},
            user=rel.elder.user,
            status=302,
            )

        assert utils.refresh(rel.student).name == u'New Name'


    def test_edit_student_requires_school_staff(self, no_csrf_client):
        """POSTing 'name' to village view does nothing if not school staff."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=False,
            to_profile__name='Old Name',
            )

        no_csrf_client.post(
            self.url(rel.student),
            {'name': 'New Name'},
            user=rel.elder.user,
            status=302,
            )

        assert utils.refresh(rel.student).name == u'Old Name'


    def test_edit_student_error(self, no_csrf_client):
        """POSTing bad name returns errors as messages."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            to_profile__name='Old Name',
            )

        res = no_csrf_client.post(
            self.url(rel.student),
            {'name': ''},
            user=rel.elder.user,
            status=302,
            ).follow()

        assert utils.refresh(rel.student).name == 'Old Name'
        res.mustcontain('This field is required')


    def test_edit_student_ajax(self, no_csrf_client):
        """POSTing 'name' via ajax edits student name and returns JSON."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            to_profile__name='Old Name',
            )

        resp = no_csrf_client.post(
            self.url(rel.student),
            {'name': 'New Name'},
            user=rel.elder.user,
            status=200,
            ajax=True,
            )

        assert utils.refresh(rel.student).name == u'New Name'
        assert resp.json == {
            'messages': [], 'success': True, 'name': 'New Name'}


    def test_edit_student_ajax_error(self, no_csrf_client):
        """POSTing bad name via ajax returns error message in JSON."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True,
            to_profile__name='Old Name',
            )

        resp = no_csrf_client.post(
            self.url(rel.student),
            {'name': ''},
            user=rel.elder.user,
            status=200,
            ajax=True,
            )

        assert utils.refresh(rel.student).name == u'Old Name'
        assert resp.json == {
            'messages': [
                {
                    'level': 40,
                    'tags': 'error',
                    'message': 'This field is required.',
                    }
                ],
            'success': False,
            'name': 'Old Name',
            }



class TestJsonPosts(object):
    """Tests for json_posts view."""
    def url(self, student=None):
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('json_posts', kwargs=dict(student_id=student.id))


    def test_requires_relationship(self, client):
        """Only an elder of that student can get posts."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)


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
            'error': "Posts are limited to 154 characters."
            }


    def test_get_posts(self, client):
        """Get backlog posts in chronological order."""
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
        # not in same village, shouldn't be returned
        factories.PostFactory()

        response = client.get(self.url(rel.student), user=rel.elder.user)

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



class TestEditElder(object):
    def url(self, rel=None):
        """rel is relationship between a student and elder to be edited."""
        if rel is None:
            rel = factories.RelationshipFactory()
        return reverse(
            'edit_elder',
            kwargs={'student_id': rel.student.id, 'elder_id': rel.elder.id},
            )


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


    def test_school_staff_required(self, client):
        """Only school staff can access."""
        rel = factories.RelationshipFactory(
            from_profile__name='Old Name', from_profile__role='Old Role')
        editor_rel = factories.RelationshipFactory(
            from_profile__school_staff=False, to_profile=rel.to_profile)
        url = self.url(rel)

        res = client.get(
            url, user=editor_rel.elder.user, status=302).follow()

        res.mustcontain("account doesn't have access")


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
        elder = factories.ProfileFactory.create(school_staff=True, code='ABCDEF')
        url = reverse('pdf_parent_instructions', kwargs={'lang': 'es'})
        resp = client.get(url, user=elder.user, status=200)

        assert resp.headers[
            'Content-Disposition'] == 'attachment; filename=instructions-es.pdf'
        assert resp.headers['Content-Type'] == 'application/pdf'


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
