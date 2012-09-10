"""Tests for user models."""
from . import factories


def test_profile_unicode():
    """Unicode representation of a Profile is its name."""
    profile = factories.ProfileFactory.build(name="Some Name")

    assert unicode(profile) == u"Some Name"
