"""Tests for Village SMS code."""
import mock

from portfoliyo import model
from portfoliyo.sms import hook

from portfoliyo.tests import factories, utils


@mock.patch('portfoliyo.sms.hook.model.Post')
def test_create_post(mock_Post):
    """Creates Post (and no reply) if one associated student."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    reply = hook.receive_sms(phone, 'foo')

    assert reply is None
    mock_Post.create.assert_called_with(profile, rel.student, 'foo')



def test_activate_user():
    """Receiving an SMS from a user activates that user."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)

    hook.receive_sms(phone, 'foo')

    assert utils.refresh(profile.user).is_active



def test_unknown_profile():
    """Reply if profile is unknown."""
    reply = hook.receive_sms('123', 'foo')

    assert reply == (
        "Bummer, we don't recognize your number! "
        "Have you been invited by your child's teacher to use Portfoliyo?"
        )


def test_multiple_students():
    """Reply if multiple associated students."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    factories.RelationshipFactory.create(from_profile=profile)
    factories.RelationshipFactory.create(from_profile=profile)

    reply = hook.receive_sms(phone, 'foo')

    assert reply == (
        "You're part of more than one student's Portfoliyo Village; "
        "we're not yet able to route your texts. We'll fix that soon!"
        )


def test_no_students():
    """Reply if no associated students."""
    phone = '+13216430987'
    factories.ProfileFactory.create(phone=phone)

    reply = hook.receive_sms(phone, 'foo')

    assert reply == (
        "You're not part of any student's Portfoliyo Village, "
        "so we're not able to deliver your message. Sorry!"
        )


def test_code_signup():
    """Parent can create account by texting teacher code and their name."""
    phone = '+13216430987'
    factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")

    reply = hook.receive_sms(phone, "abcdef John Doe")

    assert reply == (
        "Thanks! What is the name of your child in Teacher Jane's class?"
        )
    profile = model.Profile.objects.get(phone=phone)
    assert profile.state == model.Profile.STATE.kidname


def test_code_signup_lacks_name():
    """If parent texts valid teacher code but omits name, they get help."""
    phone = '+13216430987'
    factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")

    reply = hook.receive_sms(phone, "ABCDEF")

    assert reply == (
        "Please include your name after the code."
        )


def test_get_teacher_and_name():
    """Gets teacher and parent name if text starts with teacher code."""
    teacher = factories.ProfileFactory.create(school_staff=True, code="ABCDEF")

    assert hook.get_teacher_and_name("abcdef foo") == (teacher, "foo")
    assert hook.get_teacher_and_name("ABCDEF") == (teacher, '')
    assert hook.get_teacher_and_name("ACDC bar") == (None, '')
