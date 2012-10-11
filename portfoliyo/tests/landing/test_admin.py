"""Tests for landing-page admin."""
from django.core.urlresolvers import reverse

from portfoliyo.tests import factories
from portfoliyo.tests.landing.factories import LeadFactory



def test_lead_changelist(client):
    """The Lead admin changelist loads successfully."""
    admin = factories.ProfileFactory.create(
        user__is_staff=True, user__is_superuser=True)
    client.get(
        reverse("admin:landing_lead_changelist"), user=admin.user, status=200)


def test_lead_change(client):
    """The Lead admin change page loads successfully."""
    admin = factories.ProfileFactory.create(
        user__is_staff=True, user__is_superuser=True)
    lead = LeadFactory.create()
    client.get(
        reverse("admin:landing_lead_change", args=[lead.id]),
        user=admin.user,
        status=200,
        )
