"""Tests for village views."""
from django.core import mail
from django.core.urlresolvers import reverse

import pytest

from tests import utils
from tests.users import factories



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
            reverse('chat', kwargs={'student_id': student.id}))


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
            reverse('chat', kwargs={'student_id': rel.student.id}))

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



class TestChat(object):
    """Tests for village chat view."""
    def url(self, student=None):
        if student is None:
            student = factories.ProfileFactory.create()
        return reverse('chat', kwargs=dict(student_id=student.id))


    @pytest.mark.parametrize('link_target', ['add_student', 'invite_elders'])
    def test_button_only_if_staff(self, client, link_target):
        """Button with given link target is only present for school staff."""
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


    def test_requires_relationship(self, client):
        """Only an elder of that student can view chat."""
        elder = factories.ProfileFactory.create(school_staff=True)
        student = factories.ProfileFactory.create()

        client.get(self.url(student), user=elder.user, status=404)
