"""Tests for landing-page view."""
from django.core.urlresolvers import reverse

from portfoliyo.landing.models import Lead


def test_signup(client):
    """User can sign up with email; gets friendly message, stored as Lead."""
    form = client.get(reverse('home')).forms["landing-form"]
    form["email"] = "foo@example.com"
    response = form.submit().follow()

    assert "Thanks for your interest" in response.body
    assert Lead.objects.get().email == u"foo@example.com"


def test_bad_email(client):
    """If user submits a bad email, they get a friendlyish error."""
    form = client.get(reverse('home')).forms["landing-form"]
    form["email"] = "foo"
    response = form.submit()

    assert "look like an email address" in response.body
    assert Lead.objects.count() == 0
