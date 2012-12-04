"""Tests for Village SMS code."""
from django.core import mail
import mock
import pytest

from portfoliyo import model
from portfoliyo.sms import hook

from portfoliyo.tests import factories, utils


def test_create_post(db):
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



def test_activate_user(db):
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



def test_decline(db):
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



def test_active_user_decline(db):
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



def test_unknown_profile(db):
    """Reply if profile is unknown."""
    reply = hook.receive_sms('123', 'foo')

    assert reply == (
        "Bummer, we don't recognize your invite code! "
        "Please make sure it's typed exactly as it is on the paper."
        )


def test_multiple_students(db):
    """If multiple associated students, post goes in both villages."""
    phone = '+13216430987'
    profile = factories.ProfileFactory.create(phone=phone)
    rel1 = factories.RelationshipFactory.create(from_profile=profile)
    rel2 = factories.RelationshipFactory.create(from_profile=profile)

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, 'foo')

    mock_create.assert_any_call(profile, rel1.student, 'foo', from_sms=True)
    mock_create.assert_any_call(profile, rel2.student, 'foo', from_sms=True)
    assert reply is None


def test_no_students(db):
    """Reply if no associated students."""
    phone = '+13216430987'
    factories.ProfileFactory.create(phone=phone)

    reply = hook.receive_sms(phone, 'foo')

    assert reply == (
        "You're not part of any student's Portfoliyo Village, "
        "so we're not able to deliver your message. Sorry!"
        )


def test_code_signup(db):
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
    signup = profile.signups.get()
    assert profile.name == ""
    assert signup.state == model.TextSignup.STATE.kidname
    assert profile.invited_by == teacher
    assert signup.teacher == teacher
    assert signup.student is None
    assert signup.family == profile
    assert not mock_create.call_count


def test_group_code_signup(db):
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
    signup = profile.signups.get()
    assert profile.name == ""
    assert signup.state == model.TextSignup.STATE.kidname
    assert profile.invited_by == group.owner
    assert signup.teacher == group.owner
    assert signup.group == group
    assert signup.student is None
    assert signup.family == profile
    assert not mock_create.call_count


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
                'portfoliyo.model.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, "Jimmy Doe")

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
    mock_student_added.assert_any_call(student, teacher)
    mock_student_added.assert_any_call(student, parent)
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == teacher
    assert student.school == teacher.school
    assert set(student.elders) == set([teacher, parent])
    assert signup.state == model.TextSignup.STATE.relationship
    assert signup.student == student
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)



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
                'portfoliyo.model.events.student_added') as mock_student_added:
            reply = hook.receive_sms(phone, "Jimmy Doe")

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
    mock_student_added.assert_any_call(student, group.owner)
    mock_student_added.assert_any_call(student, parent)
    assert set(student.student_in_groups.all()) == {group}
    assert student.name == u"Jimmy Doe"
    assert student.invited_by == group.owner
    assert student.school == group.owner.school
    assert set(student.elders) == set([group.owner, parent])
    assert signup.state == model.TextSignup.STATE.relationship
    assert signup.student == student
    # and the name is sent on to the village chat as a post
    mock_create.assert_any_call(
        parent, student, "Jimmy Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)


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
        reply = hook.receive_sms(phone, "Jimmy Doe")

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
        from_profile__email_notifications=True,
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
        reply = hook.receive_sms(phone, "father")

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
        parent, student, "father", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)


def test_code_signup_name(db):
    """Parent can finish signup by texting their name."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__email_notifications=True,
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

    with mock.patch('portfoliyo.sms.hook.model.Post.create') as mock_create:
        reply = hook.receive_sms(phone, "John Doe")

    assert reply == (
        "All done, thank you! You can text this number any time "
        "to talk with Jimmy Doe's teachers."
        )
    parent = model.Profile.objects.get(phone=phone)
    signup = parent.signups.get()
    assert parent.name == "John Doe"
    assert signup.state == model.TextSignup.STATE.done
    student = teacher_rel.student
    mock_create.assert_any_call(
        parent, student, "John Doe", from_sms=True, email_notifications=False)
    # and the automated reply is also sent on to village chat
    mock_create.assert_any_call(
        None, student, reply, in_reply_to=phone, email_notifications=False)
    # email notification of the signup is sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['teacher@example.com']


def test_code_signup_name_no_notification(db):
    """Finish signup sends no notification if teacher doesn't want them."""
    phone = '+13216430987'
    teacher_rel = factories.RelationshipFactory.create(
        from_profile__school_staff=True,
        from_profile__email_notifications=False,
        from_profile__user__email='teacher@example.com',
        to_profile__name="Jimmy Doe",
        )
    parent_rel = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__role="",
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
        hook.receive_sms(phone, "father")

    # no email notification of the signup is sent
    assert not len(mail.outbox)


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

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too.")
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    assert new_signup.state == model.TextSignup.STATE.done
    assert new_signup.teacher == other_teacher
    assert new_signup.student == signup.student
    assert new_signup.group is None
    assert signup.student in other_teacher.students


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

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too.")
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    assert new_signup.state == model.TextSignup.STATE.done
    assert new_signup.teacher == group.owner
    assert new_signup.student == signup.student
    assert new_signup.group == group
    assert signup.student in group.owner.students
    assert group.students.filter(pk=signup.student.pk).exists()


def test_subsequent_signup_when_first_needs_student_name(db):
    """If first signup needs student name, second takes over there."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(
        family__phone=phone,
        state=model.TextSignup.STATE.kidname,
        )
    other_teacher = factories.ProfileFactory.create(
        code='ABCDEF', name='Ms. Doe')

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "Now, what's the student's name?"
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

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "Now, what's the student's name?"
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

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "Now, what's your relationship to the student?"
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

    reply = hook.receive_sms(phone, 'ABCDEF')

    assert reply == (
        "Ok, thanks! You can text Ms. Doe at this number too. "
        "Now, what's your name?"
        )
    new_signup = signup.family.signups.exclude(pk=signup.pk).get()
    signup = utils.refresh(signup)
    assert signup.state == model.TextSignup.STATE.done
    assert new_signup.state == model.TextSignup.STATE.name
    assert new_signup.teacher == other_teacher
    assert new_signup.student == signup.student
    assert new_signup.group is None


def test_multiple_active_signups_logs_warning(db):
    """If a user has multiple active signups, a warning is logged."""
    phone = '+13216430987'
    signup = factories.TextSignupFactory.create(family__phone=phone)
    factories.TextSignupFactory.create(family=signup.family)

    with mock.patch('portfoliyo.sms.hook.logger') as mock_logger:
        hook.receive_sms(phone, "Jimmy Doe")

    mock_logger.warning.assert_called_with(
        "User %s has multiple active signups!" % phone)


def test_bogus_signup_state_no_blowup(db):
    """An unknown signup state acts like no in-process signup."""
    phone = '+13216430987'
    factories.TextSignupFactory.create(family__phone=phone, state='foo')

    hook.receive_sms(phone, "Hello")


class TestGetTeacherAndGroup(object):
    def test_basic(self, db):
        """Gets teacher if text starts with teacher code."""
        t = factories.ProfileFactory.create(school_staff=True, code='ABCDEF')

        f = hook.get_teacher_and_group
        assert f("abcdef foo") == (t, None)
        assert f("ABCDEF") == (t, None)
        assert f("ACDC bar") == (None, None)
        assert f("ABCDEF. some name") == (t, None)
        assert f("ABCDEF\nsome sig") == (t, None)


    def test_group_code(self, db):
        """Gets teacher and group if text starts with group code."""
        g = factories.GroupFactory.create(
            code='ABCDEFG', owner__code='ABCDEF')

        f = hook.get_teacher_and_group
        assert f("ABCDEFG") == (g.owner, g)
        assert f("ACDC foo") == (None, None)
        assert f("ABCDEFG My Name") == (g.owner, g)
        assert f("ABCDEF ") == (g.owner, None)


    def test_empty(self):
        """Returns None on empty text, doesn't barf."""
        assert hook.get_teacher_and_group('') == (None, None)



class TestInterpolateTeacherNames(object):
    def test_one_teacher(self):
        parent_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Dodd",
            )

        res = hook.interpolate_teacher_names('%s', parent_rel.elder)

        assert res == "Mrs. Dodd"


    def test_two_teachers_one_student(self):
        parent_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Dodd",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mr. Todd",
            )

        res = hook.interpolate_teacher_names('%s', parent_rel.elder)

        assert res in {"Mrs. Dodd and Mr. Todd", "Mr. Todd and Mrs. Dodd"}


    def test_two_teachers_two_students(self):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel1.elder)
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name="Mrs. Dodd",
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name="Mr. Todd",
            )

        res = hook.interpolate_teacher_names('%s', rel1.elder)

        assert res in {"Mrs. Dodd and Mr. Todd", "Mr. Todd and Mrs. Dodd"}


    def test_three_teachers_one_student(self):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name="Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Dodd",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mr. Todd",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Ms. Codd",
            )

        res = hook.interpolate_teacher_names('%s', parent_rel.elder)

        assert res == "Frankie's teachers"


    def test_three_teachers_two_students(self):
        rel1 = factories.RelationshipFactory.create(
            to_profile__name="Frankie")
        rel2 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name="Maria")
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name="Mrs. Dodd",
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name="Mr. Todd",
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name="Ms. Codd",
            )

        res = hook.interpolate_teacher_names('%s', rel1.elder)

        assert res in {
            "Frankie and Maria's teachers", "Maria and Frankie's teachers"}


    def test_three_teachers_three_students(self):
        rel1 = factories.RelationshipFactory.create(
            to_profile__name="Frankie")
        rel2 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name="Maria",
            )
        rel3 = factories.RelationshipFactory.create(
            from_profile=rel1.from_profile,
            to_profile__name="Juan",
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name="Mrs. Dodd",
            )
        factories.RelationshipFactory.create(
            to_profile=rel2.to_profile,
            from_profile__name="Mr. Todd",
            )
        factories.RelationshipFactory.create(
            to_profile=rel3.to_profile,
            from_profile__name="Ms. Codd",
            )

        res = hook.interpolate_teacher_names('%s', rel1.elder)

        assert res == "your children's teachers"


    def test_two_teachers_one_student_too_long(self):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name="Frankie")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Doddkerstein-Schnitzelberger",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mr. Toddkinson-Hershberger",
            )
        prefix = ('a' * 130)
        res = hook.interpolate_teacher_names(
            prefix + '%s', parent_rel.elder)

        assert res == prefix + "Frankie's teachers"


    def test_two_teachers_one_student_way_too_long(self):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name="Frankie Finkelstein")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Doddkerstein-Schnitzelberger",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mr. Toddkinson-Hershberger",
            )
        prefix = ('a' * 150)
        res = hook.interpolate_teacher_names(
            prefix + '%s', parent_rel.elder)

        assert res == prefix + "teachers"


    def test_two_teachers_one_student_right_out(self):
        parent_rel = factories.RelationshipFactory.create(
            to_profile__name="Frankie Finkelstein")
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Doddkerstein-Schnitzelberger",
            )
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mr. Toddkinson-Hershberger",
            )
        prefix = ('a' * 159)
        with pytest.raises(ValueError):
            hook.interpolate_teacher_names(prefix + '%s', parent_rel.elder)


    def test_one_teacher_too_long(self):
        parent_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=parent_rel.to_profile,
            from_profile__name="Mrs. Finkelstein-Hershberger",
            )

        prefix = ('a' * 148)
        res = hook.interpolate_teacher_names(prefix + '%s', parent_rel.elder)

        assert res == prefix + "teachers"
