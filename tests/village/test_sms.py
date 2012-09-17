"""Tests for Village SMS code."""
import mock

from portfoliyo.village.sms import receive_sms

from tests import utils
from tests.users import factories


@mock.patch('portfoliyo.village.sms.models.Post')
def test_create_post(mock_Post):
    """Creates Post (and no reply) if one associated student."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    reply = receive_sms(phone, 'foo')

    assert reply is None
    mock_Post.create.assert_called_with(profile, rel.student, 'foo')



def test_activate_user():
    """Receiving an SMS from a user activates that user."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)

    receive_sms(phone, 'foo')

    assert utils.refresh(profile.user).is_active



def test_unknown_profile():
    """Reply if profile is unknown."""
    reply = receive_sms('123', 'foo')

    assert reply == (
        "Bummer, we don't recognize your number! "
        "Are you signed up as a user at portfoliyo.org?"
        )


def test_multiple_students():
    """Reply if multiple associated students."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    factories.RelationshipFactory.create(from_profile=profile)
    factories.RelationshipFactory.create(from_profile=profile)

    reply = receive_sms(phone, 'foo')

    assert reply == (
        "You're part of more than one student's Portfoliyo.org Village; "
        "we're not yet able to route your texts. We'll fix that soon!"
        )


def test_no_students():
    """Reply if no associated students."""
    phone = '+13216430987'
    factories.ProfileFactory.create(phone=phone)

    reply = receive_sms(phone, 'foo')

    assert reply == (
        "You're not part of any student's Portfoliyo.org Village, "
        "so we're not able to deliver your message. Sorry!"
        )
