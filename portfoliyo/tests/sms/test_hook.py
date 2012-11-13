"""Tests for Village SMS code."""
from django.core import mail
import mock

from portfoliyo import model
from portfoliyo.sms import hook

from portfoliyo.tests import factories, utils


def test_create_post():
    """Creates Post (and no reply) if one associated student."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, 'foo')

    assert reply is None
    mock_create.assert_called_once_with(
        profile, rel.student, 'foo', from_sms=True)



def test_easter_egg():
    phone = '+3216430987'
    reply = hook.receive_sms(phone, 'xjgdlw')

    assert reply == (
        "Woah! You actually tried it out? A cookie for you! "
        "Email sneaky@portfoliyo.org and we'll send you a cookie."
        )



def test_activate_user():
    """Receiving SMS from inactive user activates and gives them more info."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)
    rel = factories.RelationshipFactory.create(
        from_profile=profile, to_profile__name="Jimmy Doe")

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, 'foo')

    assert utils.refresh(profile.user).is_active
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, email_notifications=False)
    assert reply == (
        "Thank you! You can text this number any time "
        "to talk with Jimmy Doe's teachers."
        )



def test_decline():
    """If an inactive user replies with 'stop', they are marked declined."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, 'stop')

    assert not utils.refresh(profile.user).is_active
    assert utils.refresh(profile).declined
    assert reply == (
        "No problem! Sorry to have bothered you."
        )
    mock_create.assert_any_call(profile, rel.student, "stop", from_sms=True)
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, email_notifications=False)



def test_active_user_decline():
    """If an active user replies with 'stop', they are marked declined."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=True, phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, 'stop')

    assert not utils.refresh(profile.user).is_active
    assert utils.refresh(profile).declined
    assert reply == (
        "No problem! Sorry to have bothered you."
        )
    mock_create.assert_any_call(profile, rel.student, "stop", from_sms=True)
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, email_notifications=False)



def test_unknown_profile():
    """Reply if profile is unknown."""
    reply = hook.receive_sms('123', 'foo')

    assert reply == (
        "Bummer, we don't recognize your invite code! "
        "Please make sure it's typed exactly as it is on the paper."
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
    """Parent can create account by texting teacher code."""
    phone = '+13216430987'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, "abcdef")

    assert reply == (
        "Thanks! What is the name of your child in Teacher Jane's class?"
        )
    profile = model.Profile.objects.get(phone=phone)
    assert profile.name == ""
    assert profile.state == model.Profile.STATE.kidname
    assert profile.invited_by == teacher
    assert not mock_create.call_count


def test_group_code_signup():
    """Parent can create account by texting group code."""
    phone = '+13216430987'
    group = factories.GroupFactory.create(
        owner__school_staff=True, owner__name="Teacher Jane", code="ABCDEFG")

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, "abcdefg")

    assert reply == (
        "Thanks! What is the name of your child in Teacher Jane's class?"
        )
    profile = model.Profile.objects.get(phone=phone)
    assert profile.name == ""
    assert profile.state == model.Profile.STATE.kidname
    assert profile.invited_by == group.owner
    assert profile.invited_in_group == group
    assert not mock_create.call_count


def test_code_signup_student_name():
    """Parent can continue code signup by providing student name."""
    phone = '+13216430987'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")
    parent = factories.ProfileFactory.create(
        name="John Doe",
        phone=phone,
        state=model.Profile.STATE.kidname,
        invited_by=teacher,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch(
                'portfoliyo.model.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    assert len(teacher.students) == 1
    assert teacher.student_relationships[0].level == 'owner'
    assert len(parent.students) == 1
    student = parent.students[0]
    mock_student_added.assert_any_call(student, teacher)
    mock_student_added.assert_any_call(student, parent)
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == teacher
    assert student.school == teacher.school
    assert set(student.elders) == set([teacher, parent])
    assert parent.state == model.Profile.STATE.relationship
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)



def test_group_code_signup_student_name():
    """Parent can continue group code signup by providing student name."""
    phone = '+13216430987'
    group = factories.GroupFactory.create(
        owner__school_staff=True, owner__name="Teacher Jane", code="ABCDEFG")
    parent = factories.ProfileFactory.create(
        name="John Doe",
        phone=phone,
        state=model.Profile.STATE.kidname,
        invited_by=group.owner,
        invited_in_group=group,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch(
                'portfoliyo.model.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    assert len(group.owner.students) == 1
    assert group.owner.student_relationships[0].level == 'owner'
    assert len(parent.students) == 1
    student = parent.students[0]
    mock_student_added.assert_any_call(student, group.owner)
    mock_student_added.assert_any_call(student, parent)
    assert set(student.student_in_groups.all()) == {group}
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == group.owner
    assert student.school == group.owner.school
    assert set(student.elders) == set([group.owner, parent])
    assert parent.state == model.Profile.STATE.relationship
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)


def test_code_signup_student_name_dupe_detection():
    """Don't create duplicate students in a teacher's class."""
    phone = '+13216430987'
    rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        to_profile__name="Jimmy Doe")
    factories.ProfileFactory.create(
        name="John Doe",
        phone=phone,
        state=model.Profile.STATE.kidname,
        invited_by=rel.elder,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        reply = hook.receive_sms(phone, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    assert len(parent.students) == 1
    student = parent.students[0]
    assert student == rel.student


def test_code_signup_role():
    """Parent can continue code signup by providing their role."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__email_notifications=True,
        from_profile__name='Jane Doe',
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe")
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
        from_profile__phone=phone,
        from_profile__state=model.Profile.STATE.relationship,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        description="",
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, "father")

    assert reply == (
        "Last question: what is your name? (So Jane Doe knows who is texting.)")
    parent = model.Profile.objects.get(phone=phone)
    assert parent.role == "father"
    assert parent.state == model.Profile.STATE.name
    parent_rel = utils.refresh(parent_rel)
    assert parent_rel.description == "father"
    student = teacher_rel.student
    # and the role is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "father", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)


def test_code_signup_name():
    """Parent can finish signup by texting their name."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__email_notifications=True,
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    factories.RelationshipFactory.create(
        from_profile__name="",
        from_profile__phone=phone,
        from_profile__state=model.Profile.STATE.name,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, "John Doe")

    assert reply == (
        "All done, thank you! You can text this number any time "
        "to talk with Jimmy Doe's teachers."
        )
    parent = model.Profile.objects.get(phone=phone)
    assert parent.name == "John Doe"
    assert parent.state == model.Profile.STATE.done
    student = teacher_rel.student
    mock_create.assert_any_call(
        parent, student, "John Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)
    # email notification of the signup is sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['teacher@example.com']



def test_code_signup_name_no_notification():
    """Finish signup sends no notification if teacher doesn't want them."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__email_notifications=False,
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
        from_profile__phone=phone,
        from_profile__state=model.Profile.STATE.name,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        hook.receive_sms(phone, "father")

    # no email notification of the signup is sent
    assert not len(mail.outbox)



class TestGetTeacherAndGroup(object):
    def test_basic(self):
        """Gets teacher if text starts with teacher code."""
        t = factories.ProfileFactory.create(school_staff=True, code='ABCDEF')

        f = hook.get_teacher_and_group
        assert f("abcdef foo") == (t, None)
        assert f("ABCDEF") == (t, None)
        assert f("ACDC bar") == (None, None)
        assert f("ABCDEF. some name") == (t, None)
        assert f("ABCDEF\nsome sig") == (t, None)

    def test_group_code(self):
        """Gets teacher and group if text starts with group code."""
        g = factories.GroupFactory.create(
            code='ABCDEFG', owner__code='ABCDEF')

        f = hook.get_teacher_and_group
        assert f("ABCDEFG") == (g.owner, g)
        assert f("ACDC foo") == (None, None)
        assert f("ABCDEFG My Name") == (g.owner, g)
        assert f("ABCDEF ") == (g.owner, None)
