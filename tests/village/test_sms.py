"""Tests for Village SMS code."""
from portfoliyo.village.sms import receive_sms

from tests import utils
from tests.users import factories



def test_activate_user():
    """Receiving an SMS from a user activates that user."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)

    receive_sms(phone, 'foo')

    assert utils.refresh(profile.user).is_active



def test_unknown_profile():
    """No error if profile is unknown."""
    receive_sms('123', 'foo')
