"""Tests for core/home views."""
from django.core.urlresolvers import reverse

from portfoliyo.tests import factories
from portfoliyo.tests.utils import location



class TestHome(object):
    """Tests for home view."""
    @property
    def url(self):
        return reverse('home')


    def test_login_required(self, client, db):
        """Shows landing page if user is unauthenticated."""
        register_url = reverse('register')

        res = client.get(self.url, status=200)

        res.mustcontain('href="%s"' % register_url)


    def test_redirect_to_add_group(self, client, db):
        """Redirects to add-student if staff user has no students."""
        profile = factories.ProfileFactory.create(school_staff=True)
        res = client.get(self.url, user=profile.user, status=302)

        assert res['Location'] == location(reverse('add_student'))


    def test_redirect_to_no_students(self, client, db):
        """Redirects to no-students if non-staff user has no students."""
        profile = factories.ProfileFactory.create(school_staff=False)
        res = client.get(self.url, user=profile.user, status=302)

        assert res['Location'] == location(reverse('no_students'))


    def test_multiple_student_dashboard(self, client, db):
        """A user with multiple students gets redirected to dashboard."""
        rel = factories.RelationshipFactory(to_profile__name="Student One")
        factories.RelationshipFactory(
            from_profile=rel.elder, to_profile__name="Student Two")
        response = client.get(self.url, user=rel.elder.user, status=302)

        assert response['Location'] == location(reverse('dashboard'))
