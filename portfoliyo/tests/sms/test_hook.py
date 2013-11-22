# -*- coding: utf-8 -*-
"""Tests for SMS-handling code."""
from datetime import datetime

from django.conf import settings
from django.utils.timezone import get_current_timezone
import mock

from portfoliyo import model
from portfoliyo.sms import hook

from portfoliyo.tests import factories, utils


def test_create_post(db):
    """Creates Post (and no reply) if one associated student."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)
    # prevent this from being a "no teachers" situation
    factories.RelationshipFactory.create(
        from_profile__school_staff=True, to_profile=rel.student)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'foo')

    assert reply is None
    mock_create.assert_called_once_with(
        profile, rel.student, 'foo', from_sms=True)



def test_activate_user(db):
    """Receiving SMS from inactive user activates and gives them more info."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone, declined=True)
    rel = factories.RelationshipFactory.create(
        from_profile=profile, to_profile__name="Jimmy Doe")
    # prevent this from being a "no teachers" situation
    factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name='Ms. Johns',
        to_profile=rel.student,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'foo')

    profile = utils.refresh(profile)
    assert profile.user.is_active
    assert not profile.declined
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, notifications=False)
    assert reply == (
        "You can text this number "
        "to talk with Ms. Johns."
        )



def test_decline(db):
    """If an inactive user replies with 'stop', they are marked declined."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=False, phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'stop')

    assert not utils.refresh(profile.user).is_active
    assert utils.refresh(profile).declined
    assert reply == (
        "No problem! Sorry to have bothered you. "
        "Text this number anytime to re-start."
        )
    mock_create.assert_any_call(profile, rel.student, "stop", from_sms=True)
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, notifications=False)



def test_active_user_decline(db):
    """If an active user replies with 'stop', they are marked declined."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(
        user__is_active=True, phone=phone)
    rel = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'stop')

    assert not utils.refresh(profile.user).is_active
    assert utils.refresh(profile).declined
    assert reply == (
        "No problem! Sorry to have bothered you. "
        "Text this number anytime to re-start."
        )
    mock_create.assert_any_call(profile, rel.student, "stop", from_sms=True)
    mock_create.assert_any_call(
        None, rel.student, reply, in_reply_to=phone, notifications=False)



def test_unknown_profile(db):
    """Reply if profile is unknown."""
    reply = hook.receive_sms('123', settings.DEFAULT_NUMBER, 'foo')

    assert reply == (
        "We don't recognize your phone number, "
        "so we don't know who to send your text to! "
        "If you are just signing up, "
        "make sure your invite code is typed correctly."
        )


def test_multiple_students(db):
    """If multiple associated students, check for matching pyo_phone."""
    phone = '+13216430987'
    pyo_phone_1 = '+12222222222'
    pyo_phone_2 = '+13333333333'
    profile = factories.ProfileFactory.create(phone=phone)
    rel1 = factories.RelationshipFactory.create(
        from_profile=profile, pyo_phone=pyo_phone_1)
    factories.RelationshipFactory.create(
        from_profile=profile, pyo_phone=pyo_phone_2)
    # prevent this from being a "no teachers" situation
    factories.RelationshipFactory.create(
        from_profile__school_staff=True, to_profile=rel1.student)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, pyo_phone_1, 'foo')

    mock_create.assert_called_once_with(
        profile, rel1.student, 'foo', from_sms=True)
    assert reply is None


def test_no_students(db):
    """Reply if no associated students."""
    phone = '+13216430987'
    factories.ProfileFactory.create(phone=phone)

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'foo')

    assert reply == (
        "Sorry, we can't find any students connected to your number, "
        "so we can't deliver your message. "
        "Please text a teacher code to connect with that teacher."
        )


def test_orphan_student(db):
    """Reply if no student has a teacher."""
    phone = '+13216430987'
    factories.RelationshipFactory.create(
        from_profile__phone=phone)

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'foo')

    assert reply == (
        "Sorry, we can't find any teachers connected to your number, "
        "so we can't deliver your message. "
        "Please text a teacher code to connect with that teacher."
        )



def test_code_signup(db):
    """Parent can create account by texting teacher code."""
    phone = '+13216430987'
    source_phone = '+13336660000'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF", country_code='ca')

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch('portfoliyo.sms.hook.track_signup') as mock_track:
            reply = hook.receive_sms(phone, source_phone, "abcdef")

    assert reply == (
        "Thanks! What is the first and last name of your child in Teacher Jane's class?"
        )
    profile = model.Profile.objects.get(phone=phone)
    signup = profile.signups.get()
    assert profile.name == ""
    assert profile.country_code == 'ca'
    assert profile.source_phone == source_phone
    assert signup.state == model.TextSignup.STATE.kidname
    assert profile.invited_by == teacher
    assert signup.teacher == teacher
    assert signup.student is None
    assert signup.family == profile
    assert not mock_create.call_count
    mock_track.assert_called_with(profile, teacher, None)


def test_code_signup_with_language(db):
    """Parent can include language code in starting code signup."""
    phone = '+13216430987'
    factories.ProfileFactory.create(
        school_staff=True, name="Teacher Joe", code="ABCDEF")

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "abcdef ES")

    assert reply == (
        u"¡Gracias! ¿Cuál es el nombre de su hijo en la clase del Teacher Joe?")
    profile = model.Profile.objects.get(phone=phone)
    assert profile.lang_code == 'es'



def test_group_code_signup(db):
    """Parent can create account by texting group code."""
    phone = '+13216430987'
    group = factories.GroupFactory.create(
        owner__school_staff=True, owner__name="Teacher Jane", code="ABCDEFG")

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch('portfoliyo.sms.hook.track_signup') as mock_track:
            reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "abcdefg")

    assert reply == (
        "Thanks! What is the first and last name of your child in Teacher Jane's class?"
        )
    profile = model.Profile.objects.get(phone=phone)
    signup = profile.signups.get()
    assert profile.name == ""
    assert signup.state == model.TextSignup.STATE.kidname
    assert profile.invited_by == group.owner
    assert signup.teacher == group.owner
    assert signup.group == group
    assert signup.student is None
    assert signup.family == profile
    assert not mock_create.call_count
    mock_track.assert_called_with(profile, group.owner, group)


def test_code_signup_student_name(db):
    """Parent can continue code signup by providing student name."""
    phone = '+13216430987'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")
    factories.TextSignupFactory.create(
        family__name="John Doe",
        family__phone=phone,
        family__invited_by=teacher,
        state=model.TextSignup.STATE.kidname,
        teacher=teacher,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch(
                'portfoliyo.pusher.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert len(teacher.students) == 1
    assert teacher.student_relationships[0].level == 'owner'
    assert len(parent.students) == 1
    student = parent.students[0]
    mock_student_added.assert_any_call(student.id, [teacher.id])
    mock_student_added.assert_any_call(student.id, [parent.id])
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == teacher
    assert student.school == teacher.school
    assert set(student.elders) == set([teacher, parent])
    assert signup.state == model.TextSignup.STATE.relationship
    assert signup.student == student
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, notifications=False)


def test_code_signup_student_name_strips_extra_lines(db):
    """Extra lines (eg SMS auto-sig) not included in student name."""
    phone = '+13216430987'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")
    factories.TextSignupFactory.create(
        family__name="John Doe",
        family__phone=phone,
        family__invited_by=teacher,
        state=model.TextSignup.STATE.kidname,
        teacher=teacher,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        hook.receive_sms(
            phone, settings.DEFAULT_NUMBER, "Jimmy Doe\nLook at me!")

    parent = model.Profile.objects.get(phone=phone)
    student = parent.students[0]
    assert student.name == u"Jimmy Doe"
    mock_create.assert_any_call(
        parent,
        student,
        "Jimmy Doe\nLook at me!",
        from_sms=True,
        notifications=False,
        )


def test_unusually_long_student_name_tracked(db):
    """If a student name is unusually long, it is tracked."""
    phone = '+13216430987'
    teacher = factories.ProfileFactory.create(
        school_staff=True, name="Teacher Jane", code="ABCDEF")
    factories.TextSignupFactory.create(
        family__name="John Doe",
        family__phone=phone,
        family__invited_by=teacher,
        state=model.TextSignup.STATE.kidname,
        teacher=teacher,
        )

    msg = "Hi there Ms. Waggoner this is Joe Smith how is Jimmy doing?"
    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        with mock.patch('portfoliyo.sms.hook.track_sms') as mock_track:
            hook.receive_sms(phone, settings.DEFAULT_NUMBER, msg)

    mock_track.assert_called_with("long answer", phone, msg)



def test_group_code_signup_student_name(db):
    """Parent can continue group code signup by providing student name."""
    phone = '+13216430987'
    group = factories.GroupFactory.create(
        owner__school_staff=True, owner__name="Teacher Jane", code="ABCDEFG")
    factories.TextSignupFactory.create(
        family__name="John Doe",
        family__phone=phone,
        family__invited_by=group.owner,
        group=group,
        teacher=group.owner,
        state=model.TextSignup.STATE.kidname,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        with mock.patch(
                'portfoliyo.pusher.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert len(group.owner.students) == 1
    assert group.owner.student_relationships[0].level == 'owner'
    assert len(parent.students) == 1
    student = parent.students[0]
    mock_student_added.assert_any_call(student.id, [group.owner.id])
    mock_student_added.assert_any_call(student.id, [parent.id])
    assert set(student.student_in_groups.all()) == {group}
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == group.owner
    assert student.school == group.owner.school
    assert set(student.elders) == set([group.owner, parent])
    assert signup.state == model.TextSignup.STATE.relationship
    assert signup.student == student
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, notifications=False)


def test_code_signup_student_name_dupe_detection(db):
    """Don't create duplicate students in a teacher's class."""
    phone = '+13216430987'
    rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        to_profile__name="Jimmy Doe")
    factories.TextSignupFactory.create(
        family__name="John Doe",
        family__phone=phone,
        family__invited_by=rel.elder,
        teacher=rel.elder,
        state=model.TextSignup.STATE.kidname,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "Jimmy Doe")

    assert reply == (
        "And what is your relationship to that child "
        "(mother, father, ...)?"
        )
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert len(parent.students) == 1
    student = parent.students[0]
    assert student == rel.student
    assert signup.student == rel.student


def test_code_signup_role(db):
    """Parent can continue code signup by providing their role."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name='Jane Doe',
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe")
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        description="",
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        student=parent_rel.student,
        teacher=teacher_rel.elder,
        state=model.TextSignup.STATE.relationship,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "father")

    assert reply == (
        "Last question: what is your name? (So Jane Doe knows who is texting.)")
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert parent.role == "father"
    assert signup.state == model.TextSignup.STATE.name
    parent_rel = utils.refresh(parent_rel)
    assert parent_rel.description == "father"
    student = teacher_rel.student
    # and the role is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "father", from_sms=True, notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, notifications=False)


def test_code_signup_role_strips_extra_lines(db):
    """Extra lines (eg SMS auto-sig) not included in parent role."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name='Jane Doe',
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe")
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        description="",
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        student=parent_rel.student,
        teacher=teacher_rel.elder,
        state=model.TextSignup.STATE.relationship,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        hook.receive_sms(phone, settings.DEFAULT_NUMBER, "father\nI'm a sig!")

    parent = model.Profile.objects.get(phone=phone)
    assert parent.role == "father"


def test_unusually_long_role_tracked(db):
    """If a family member role is unusually long, it is tracked."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name='Jane Doe',
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe")
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        description="",
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        student=parent_rel.student,
        teacher=teacher_rel.elder,
        state=model.TextSignup.STATE.relationship,
        )

    msg = "Hi there Ms. Waggoner this is Joe Smith how is Jimmy doing?"
    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        with mock.patch('portfoliyo.sms.hook.track_sms') as mock_track:
            hook.receive_sms(phone, settings.DEFAULT_NUMBER, msg)

    mock_track.assert_called_with('long answer', phone, msg)


def test_code_signup_name(db):
    """Parent can finish signup by texting their name."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__notify_new_parent=True,
        from_profile__name="Teacher Jane",
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        teacher=teacher_rel.elder,
        student=teacher_rel.student,
        state=model.TextSignup.STATE.name,
        )

    record_notification_path = 'portfoliyo.tasks.record_notification.delay'
    with mock.patch(record_notification_path) as mock_record_notification:
        with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
            reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, "John Doe")

    assert reply == (
        "All done, thank you! You can text this number "
        "to talk with Teacher Jane."
        )
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert parent.name == "John Doe"
    assert signup.state == model.TextSignup.STATE.done
    student = teacher_rel.student
    mock_create.assert_any_call(
        parent, student, "John Doe", from_sms=True, notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, notifications=False)
    mock_record_notification.assert_called_with('new_parent', teacher_rel.elder, signup)


def test_code_signup_name_strips_extra_lines(db):
    """Extra lines (e.g. SMS auto-sig) excluded from parent name."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name="Teacher Jane",
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        teacher=teacher_rel.elder,
        student=teacher_rel.student,
        state=model.TextSignup.STATE.name,
        )

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        hook.receive_sms(
            phone, settings.DEFAULT_NUMBER, "\n John Doe\nI'm a sig too!")

    parent = model.Profile.objects.get(phone=phone)
    assert parent.name == "John Doe"


def test_unusually_long_parent_name_tracked(db):
    """If a family member name is unusually long, it is tracked."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__name="Teacher Jane",
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="",
        from_profile__phone=phone,
        from_profile__invited_by=teacher_rel.elder,
        to_profile=teacher_rel.student,
        )
    factories.TextSignupFactory.create(
        family=parent_rel.elder,
        teacher=teacher_rel.elder,
        student=teacher_rel.student,
        state=model.TextSignup.STATE.name,
        )

    msg = "Hi there Ms. Waggoner this is Joe Smith how is Jimmy doing?"
    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        with mock.patch('portfoliyo.sms.hook.track_sms') as mock_track:
            hook.receive_sms(phone, settings.DEFAULT_NUMBER, msg)

    mock_track.assert_called_with('long answer', phone, msg)


def test_subsequent_signup(db):
    """A parent can send a second code after completing first signup."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.done,
        student=factories.ProfileFactory.create(),
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)
    other_teacher = factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    rn_tgt = 'portfoliyo.tasks.record_notification.delay'
    create_tgt = 'portfoliyo.sms.hook.model.Post.create'
    with mock.patch('portfoliyo.sms.hook.track_signup') as mock_track:
        with mock.patch(rn_tgt) as mock_record_notification:
            with mock.patch(create_tgt) as mock_create:
                reply = hook.receive_sms(
                    phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too.")
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    assert new_signup.state == model.TextSignup.STATE.done
    assert new_signup.teacher == other_teacher
    assert new_signup.student == signup.student
    assert new_signup.group is None
    assert signup.student in other_teacher.students
    # both incoming text and reply are recorded in village
    assert mock_create.call_count == 2
    mock_create.assert_any_call(
        signup.family,
        signup.student,
        "ABCDEF",
        from_sms=True,
        )
    mock_create.assert_any_call(
        None,
        signup.student,
        reply,
        in_reply_to=u'+13216430987',
        notifications=False,
        )
    assert mock_record_notification.call_count == 2
    mock_record_notification.assert_any_call(
        'village_additions', signup.family, [other_teacher], [signup.student])
    mock_record_notification.assert_any_call(
        'new_parent', other_teacher, new_signup)
    mock_track.assert_called_with(signup.family, other_teacher, None)



def test_subsequent_signup_with_language(db):
    """A parent can update their language with their second code."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        family__lang_code='en',
        state=model.TextSignup.STATE.done,
        student=factories.ProfileFactory.create(),
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)
    factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    with mock.patch('portfoliyo.sms.hook.model.Post.create'):
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF Es')

    profile = utils.refresh(signup.family)
    assert profile.lang_code == 'es'
    assert reply == (
        u"¡Ok, gracias! Usted puede texto del Ms. Doe en este número también.")


def test_subsequent_signup_when_teacher_already_in_village(db):
    """If parent sends a second code for a teacher already there, no reply."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.done,
        student=factories.ProfileFactory.create(),
        teacher__code='ABCDEF',
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)

    rn_tgt = 'portfoliyo.tasks.record_notification.delay'
    create_tgt = 'portfoliyo.sms.hook.model.Post.create'
    with mock.patch(rn_tgt) as mock_record_notification:
        with mock.patch(create_tgt) as mock_create:
            reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply is None
    assert signup.family.signups.count() == 1
    # incoming text is recorded in village
    mock_create.assert_called_with(
        signup.family,
        signup.student,
        "ABCDEF",
        from_sms=True,
        )
    assert mock_record_notification.call_count == 0



def test_subsequent_group_signup(db):
    """A parent can send a group code after completing first signup."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.done,
        student=factories.ProfileFactory.create(),
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)
    group = factories.GroupFactory.create(
        code='ABCDEF', owner__name='Ms. Doe')

    with mock.patch('portfoliyo.sms.hook.track_signup') as mock_track:
        reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too.")
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    assert new_signup.state == model.TextSignup.STATE.done
    assert new_signup.teacher == group.owner
    assert new_signup.student == signup.student
    assert new_signup.group == group
    assert signup.student in group.owner.students
    assert group.students.filter(pk=signup.student.pk).exists()
    mock_track.assert_called_with(signup.family, group.owner, group)


def test_subsequent_signup_when_first_needs_student_name(db):
    """If first signup needs student name, second takes over there."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.kidname,
        )
    other_teacher = factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "And what's the student's first and last name?"
        )
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    signup = utils.refresh(signup)
    assert signup.state == model.TextSignup.STATE.done
    assert new_signup.state == model.TextSignup.STATE.kidname
    assert new_signup.teacher == other_teacher
    assert new_signup.student is None
    assert new_signup.group is None


def test_subsequent_group_signup_when_first_needs_student_name(db):
    """If first signup needs student name, second takes over there."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.kidname,
        )
    group = factories.GroupFactory.create(
        code='ABCDEF', owner__name='Ms. Doe')

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "And what's the student's first and last name?"
        )
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    signup = utils.refresh(signup)
    assert signup.state == model.TextSignup.STATE.done
    assert new_signup.state == model.TextSignup.STATE.kidname
    assert new_signup.teacher == group.owner
    assert new_signup.student is None
    assert new_signup.group == group


def test_subsequent_signup_when_first_needs_role(db):
    """If first signup needs role, second takes over where it left off."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.relationship,
        student=factories.ProfileFactory.create(),
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)
    other_teacher = factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "And what's your relationship to the student?"
        )
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    signup = utils.refresh(signup)
    assert signup.state == model.TextSignup.STATE.done
    assert new_signup.state == model.TextSignup.STATE.relationship
    assert new_signup.teacher == other_teacher
    assert new_signup.student == signup.student
    assert new_signup.group is None


def test_subsequent_signup_when_first_needs_name(db):
    """If first signup needs name, second takes over where it left off."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.name,
        student=factories.ProfileFactory.create(),
        )
    factories.RelationshipFactory.create(
        from_profile=signup.teacher, to_profile=signup.student)
    factories.RelationshipFactory.create(
        from_profile=signup.family, to_profile=signup.student)
    other_teacher = factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "And what's your name?"
        )
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    signup = utils.refresh(signup)
    assert signup.state == model.TextSignup.STATE.done
    assert new_signup.state == model.TextSignup.STATE.name
    assert new_signup.teacher == other_teacher
    assert new_signup.student == signup.student
    assert new_signup.group is None


def test_subsequent_signup_when_no_students(db):
    """If a parent has no students they can text a code to start over."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        teacher__code='ABCDEF',
        teacher__name='Ms. Doe',
        state=model.TextSignup.STATE.done,
        )

    reply = hook.receive_sms(phone, settings.DEFAULT_NUMBER, 'ABCDEF')

    assert reply == (
        "Thanks! What is the first and last name of your child in Ms. Doe's class?")
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    assert new_signup.state == model.TextSignup.STATE.kidname
    assert new_signup.teacher == signup.teacher
    assert new_signup.group is None


def test_multiple_active_signups_logs_warning(db):
    """If a user has multiple active signups, a warning is logged."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(family__phone=phone)
    factories.TextSignupFactory.create(family=signup.family)

    with mock.patch('portfoliyo.sms.hook.logger') as mock_logger:
        hook.receive_sms(phone, settings.DEFAULT_NUMBER, "Jimmy Doe")

    mock_logger.warning.assert_called_with(
        "User %s has multiple active signups!", phone)


def test_bogus_signup_state_no_blowup(db):
    """An unknown signup state acts like no in-process signup."""
    phone = '+13216430987'
    factories.TextSignupFactory.create(family__phone=phone, state='foo')

    hook.receive_sms(phone, settings.DEFAULT_NUMBER, "Hello")



class TestParseCode(object):
    def test_basic(self, db):
        """Gets teacher if text starts with teacher code."""
        t = factories.ProfileFactory.create(school_staff=True, code='ABCDEF')

        f = hook.parse_code
        assert f("abcdef foo") == (t, None, 'en')
        assert f("ABCDEF") == (t, None, 'en')
        assert f("ACDC bar") == (None, None, None)
        assert f("ABCDEF. some name") == (t, None, 'en')
        assert f("ABCDEF\nsome sig") == (t, None, 'en')


    def test_group_code(self, db):
        """Gets teacher and group if text starts with group code."""
        g = factories.GroupFactory.create(
            code='ABCDEFG', owner__code='ABCDEF')

        f = hook.parse_code
        assert f("ABCDEFG") == (g.owner, g, 'en')
        assert f("ACDC foo") == (None, None, None)
        assert f("ABCDEFG My Name") == (g.owner, g, 'en')
        assert f("ABCDEF ") == (g.owner, None, 'en')


    def test_empty(self):
        """Returns None on empty text, doesn't barf."""
        assert hook.parse_code('') == (None, None, None)


    def test_lang(self, db):
        """Can specify language with teacher or group code."""
        g = factories.GroupFactory.create(
            code='ABCDEFG', owner__code='ABCDEF')

        f = hook.parse_code
        assert f("ABCDEFG es") == (g.owner, g, 'es')
        assert f("ABCDEF ES") == (g.owner, None, 'es')
        assert f("ABCDEF es foo") == (g.owner, None, 'es')
        assert f("ABCDEFG foo") == (g.owner, g, 'en')
        assert f("ABCDEF es;") == (g.owner, None, 'es')



class TestInterpolateTeacherNames(object):
    def test_no_students(self, db):
        parent = factories.ProfileFactory.create()

        res = hook.interpolate_teacher_names(u'%s', parent)

        assert res == u"teachers"

    def test_one_teacher(self, db):
        parent_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Dodd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', parent_rel.elder)

        assert res == u"Mrs. Dodd"


    def test_two_teachers_one_student(self, db):
        parent_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', parent_rel.elder)

        assert res in {u"Mrs. Dodd & Mr. Todd", u"Mr. Todd & Mrs. Dodd"}


    def test_two_teachers_two_students(self, db):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel1.elder)
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', rel1.elder)

        assert res in {u"Mrs. Dodd & Mr. Todd", u"Mr. Todd & Mrs. Dodd"}


    def test_three_teachers_one_student(self, db):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Ms. Codd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', parent_rel.elder)

        assert res == u"Frankie's teachers"


    def test_three_teachers_two_students(self, db):
        rel1 = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        rel2 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name=u"Maria")
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name=u"Ms. Codd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', rel1.elder)

        assert res in {
            u"Frankie & Maria's teachers", u"Maria & Frankie's teachers"}


    def test_three_teachers_three_students(self, db):
        rel1 = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        rel2 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name=u"Maria",
            )
        rel3 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name=u"Juan",
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=rel3.to_profile,
            from_profile__name=u"Ms. Codd",
            from_profile__school_staff=True,
            )

        res = hook.interpolate_teacher_names(u'%s', rel1.elder)

        assert res == u"your students' teachers"


    def test_two_teachers_one_student_too_long(self, db):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mrs. Doddkerstein-Schnitzelberger",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mr. Toddkinson-Hershberger",
            from_profile__school_staff=True,
            )
        prefix = (u'a' * 130)
        res = hook.interpolate_teacher_names(
            prefix + '%s', parent_rel.elder)

        assert res == prefix + u"Frankie's teachers"


    def test_one_teacher_one_student_too_long(self, db):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mrs. Doddkerstein-Schnitzelberger",
            from_profile__school_staff=True,
            )
        prefix = (u'a' * 140)
        res = hook.interpolate_teacher_names(
            prefix + '%s', parent_rel.elder)

        assert res == prefix + u"Frankie's teacher"


    def test_everything_too_long(self, db):
        """If all options are too long, take the best regardless of length."""
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name=u"Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mrs. Dodd",
            from_profile__school_staff=True,
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name=u"Mr. Todd",
            from_profile__school_staff=True,
            )
        prefix = (u'a' * 155)
        res = hook.interpolate_teacher_names(
            prefix + '%s', parent_rel.elder)

        assert res in {
            prefix + u"Mrs. Dodd & Mr. Todd",
            prefix + u"Mr. Todd & Mrs. Dodd",
            }



def test_track_sms():
    """Calls mixpanel.track with appropriate args."""
    phone = '+13216540987'
    with mock.patch('portfoliyo.mixpanel.track') as mock_track:
        hook.track_sms('event', phone, 'body', foo='bar')

    mock_track.assert_called_with(
        'sms: event',
        {'distinct_id': phone, 'phone': phone, 'message': 'body', 'foo': 'bar'},
        )



def test_track_signup(db):
    """Records data about parent signup."""
    phone = '+13216540987'
    parent = factories.ProfileFactory.create(phone=phone)
    teacher = factories.ProfileFactory.create()
    with mock.patch('portfoliyo.mixpanel.track') as mock_track:
        with mock.patch('portfoliyo.mixpanel.people_increment') as mock_incr:
            with mock.patch('portfoliyo.mixpanel.people_set') as mock_set:
                with mock.patch('portfoliyo.sms.hook.timezone.now') as mock_now:
                    mock_now.return_value = datetime(
                        2013, 1, 14, 12, 2, 3, tzinfo=get_current_timezone())
                    hook.track_signup(parent, teacher)

    mock_track.assert_called_with(
        'parent signup', {'distinct_id': teacher.user.id, 'phone': phone})
    mock_incr.assert_called_with(teacher.user.id, {'parentSignups': 1})
    mock_set.assert_called_with(
        teacher.user.id, {'lastParentSignup': '2013-01-14T12:02:03'})



def test_track_group_signup(db):
    """Records extra data about parent signup in group."""
    phone = '+13216540987'
    parent = factories.ProfileFactory.create(phone=phone)
    group = factories.GroupFactory.create()
    with mock.patch('portfoliyo.mixpanel.track') as mock_track:
        hook.track_signup(parent, group.owner, group)

    mock_track.assert_called_with(
        'parent signup',
        {
            'distinct_id': group.owner.user.id,
            'phone': phone,
            'groupId': group.id,
            'groupName': group.name,
            },
        )
