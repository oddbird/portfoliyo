"""Tests for landing-page forms."""
from portfoliyo.landing import forms


ERROR_MSG = u"That doesn't look like an email address; double-check it?"


def test_required_error():
    """Friendly error message if no email given."""
    form = forms.LeadForm({"email": ""})

    assert not form.is_valid()
    assert form.errors["email"] == [ERROR_MSG]


def test_invalid_error():
    """Friendly error message if invalid email given."""
    form = forms.LeadForm({"email": "foo"})

    assert not form.is_valid()
    assert form.errors["email"] == [ERROR_MSG]
