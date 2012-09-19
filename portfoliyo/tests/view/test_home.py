"""Tests for core/home views."""
from django.core.urlresolvers import reverse

from portfoliyo.tests import factories
from portfoliyo.tests.utils import location



class TestHome(object):
    """Tests for home view."""
    @property
    def url(self):
        return reverse('home')


    def test_login_required(self, client):
        """Shows landing page if user is unauthenticated."""
        res = client.get(self.url, status=200)

        res.mustcontain('sign up!')


    def test_redirect_to_single_student(self, client):
        """Redirects to village page if user has a single student."""
        rel = factories.RelationshipFactory.create()
        res = client.get(self.url, user=rel.elder.user, status=302)

        assert res['Location'] == location(
            reverse('village', kwargs={'student_id': rel.student.id}))


    def test_redirect_to_add_student(self, client):
        """Redirects to add-student if staff user has no students."""
        profile = factories.ProfileFactory.create(school_staff=True)
        res = client.get(self.url, user=profile.user, status=302)

        assert res['Location'] == location(reverse('add_student'))


    def test_redirect_to_no_students(self, client):
        """Redirects to no-students if non-staff user has no students."""
        profile = factories.ProfileFactory.create(school_staff=False)
        res = client.get(self.url, user=profile.user, status=302)

        assert res['Location'] == location(reverse('no_students'))


    def test_multiple_student_dashboard(self, client):
        """A user with multiple students gets redirected to dashboard."""
        rel = factories.RelationshipFactory(to_profile__name="Student One")
        factories.RelationshipFactory(
            from_profile=rel.elder, to_profile__name="Student Two")
        response = client.get(self.url, user=rel.elder.user, status=302)

        assert response['Location'] == location(reverse('dashboard'))
