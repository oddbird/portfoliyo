"""Tests for landing-page admin."""
from django.core.urlresolvers import reverse

from . import factories



def test_lead_changelist(admin, client):
    """The Lead admin changelist loads successfully."""
    client.get(
        reverse("admin:landing_lead_changelist"), user=admin, status=200)


def test_lead_change(admin, client):
    """The Lead admin change page loads successfully."""
    lead = factories.LeadFactory.create()
    client.get(
        reverse("admin:landing_lead_change", args=[lead.id]),
        user=admin,
        status=200,
        )
