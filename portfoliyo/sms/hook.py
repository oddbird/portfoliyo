"""Village SMS-handling."""
import logging

from django.conf import settings
from django.utils import timezone

from portfoliyo import model, notifications, tasks
from . import messages


# The maximum expected length (in words) of a name or role
# Setting a fairly low bar for starters to get more data, since it's only
# warning us, not affecting the user
MAX_EXPECTED_ANSWER_LENGTH = 5


logger = logging.getLogger(__name__)



def receive_sms(source, body):
    """
    Hook for when an SMS is received.

    Return None if no reply should be sent, or text of reply.

    """
    # handle landing page easter egg
    if body.strip().lower() == 'xjgdlw':
        return (
            "Woah! You actually tried it out? A cookie for you! "
            "Email sneaky@portfoliyo.org and we'll send you a cookie."
            )

    try:
        profile = model.Profile.objects.select_related(
            'user').get(phone=source)
    except model.Profile.DoesNotExist:
        return handle_unknown_source(source, body)

    if body.strip().lower() == 'stop':
        profile.declined = True
        profile.save()
        profile.user.is_active = False
        profile.user.save()
        for student in profile.students:
            model.Post.create(profile, student, body, from_sms=True)
        return reply(
            source,
            profile.students,
            messages.get('ACK_STOP', profile.lang_code)
            )

    activated = False
    if not profile.user.is_active:
        profile.user.is_active = True
        profile.user.save()
        activated = True
    if profile.declined:
        profile.declined = False
        profile.save()
        activated = True

    active_signups = profile.signups.exclude(state=model.TextSignup.STATE.done)

    if active_signups:
        if len(active_signups) > 1:
            # shouldn't happen, since second signup sets first to done
            logger.warning('User %s has multiple active signups!', source)
            # not much we can do but just pick one arbitrarily
        signup = active_signups[0]
    else:
        signup = None

    teacher, group, lang = parse_code(body)
    if teacher is not None:
        return handle_subsequent_code(
            profile, body, teacher, group, lang, signup)

    if signup is not None:
        if signup.state == model.TextSignup.STATE.kidname:
            return handle_new_student(signup, body)
        elif signup.state == model.TextSignup.STATE.relationship:
            return handle_role_update(signup, body)
        elif signup.state == model.TextSignup.STATE.name:
            return handle_name_update(signup, body)

    students = profile.students

    if not students:
        track_sms('no students', source, body)
        return messages.get('NO_STUDENTS', profile.lang_code)

    for student in students:
        model.Post.create(profile, student, body, from_sms=True)

    teachers = model.Profile.objects.filter(
        school_staff=True, relationships_from__to_profile__in=students)
    if not teachers.exists():
        return messages.get('NO_TEACHERS', profile.lang_code)

    if activated:
        return reply(
            source,
            students,
            interpolate_teacher_names(
                messages.get('ACTIVATED', profile.lang_code), profile)
        )



def handle_unknown_source(source, body):
    """Handle a text from an unknown user."""
    teacher, group, lang = parse_code(body)
    if teacher is not None:
        family = model.Profile.create_with_user(
            school=teacher.school,
            phone=source,
            invited_by=teacher,
            lang_code=lang,
            )
        model.TextSignup.objects.create(
            family=family,
            teacher=teacher,
            group=group,
            state=model.TextSignup.STATE.kidname,
            )
        track_signup(family, teacher, group)
        return messages.get('STUDENT_NAME', family.lang_code) % teacher.name
    else:
        track_sms('unknown', source, body)
        # we don't know what language to use here, so we use the default. We
        # still use messages.get just so this message is kept with all the
        # others.
        return messages.get('UNKNOWN', settings.LANGUAGE_CODE)


def handle_subsequent_code(profile, body, teacher, group, lang, signup):
    """
    Handle a second code from an already-signed-up parent.

    If ``signup`` is not ``None``, it is an already-in-progress but
    not-yet-finished signup. In that case, we mark it done and transfer its
    state to the new signup so we still get answers to the questions.

    """
    student = profile.students[0] if profile.students else None

    if profile.lang_code != lang:
        profile.lang_code = lang
        profile.save()

    # This goes before the teacher-already-in-village check, because in any
    # case we want to add student to group if this is a group code, and pass
    # post on to village
    if student or signup:
        next_state = signup.state if signup else model.TextSignup.STATE.done
        msg = messages.get(
            'SUBSEQUENT_CODE_DONE', profile.lang_code) % teacher.name
    else:
        next_state = model.TextSignup.STATE.kidname
        msg = messages.get('STUDENT_NAME', profile.lang_code) % teacher.name

    if signup:
        follow_ups = {
            model.TextSignup.STATE.kidname:
                messages.get('STUDENT_NAME_FOLLOWUP', profile.lang_code),
            model.TextSignup.STATE.relationship:
                messages.get('RELATIONSHIP_FOLLOWUP', profile.lang_code),
            model.TextSignup.STATE.name:
                messages.get('NAME_FOLLOWUP', profile.lang_code),
            }
        msg = msg + " " + follow_ups.get(signup.state, "")
        signup.state = model.TextSignup.STATE.done
        signup.save()

    if student:
        rel, created = model.Relationship.objects.get_or_create(
            from_profile=teacher,
            to_profile=student,
            defaults={'level': model.Relationship.LEVEL.owner},
            )
        if group:
            group.students.add(student)
        model.Post.create(profile, student, body, from_sms=True)

    # don't reply, track, or create new signup if already connected to teacher
    if (signup and teacher == signup.teacher) or (student and not created):
        return None

    track_signup(profile, teacher, group)

    model.TextSignup.objects.create(
        family=profile,
        teacher=teacher,
        group=group,
        student=student,
        state=next_state,
        )

    return reply(profile.phone, [student] if student else [], msg)


def handle_new_student(signup, body):
    """Handle addition of a student to a just-signing-up parent's account."""
    student_name = get_answer(body, signup.family.phone)

    possible_dupes = model.Profile.objects.filter(
        name__iexact=student_name,
        relationships_to__from_profile=signup.teacher,
        )
    if possible_dupes:
        dupe_found = True
        student = possible_dupes[0]
    else:
        dupe_found = False
        student = model.Profile.create_with_user(
            name=student_name,
            invited_by=signup.teacher,
            school=signup.teacher.school,
            )
    model.Relationship.objects.create(
        from_profile=signup.family,
        to_profile=student,
        kind=model.Relationship.KIND.elder,
        )
    if not dupe_found:
        model.Relationship.objects.create(
            from_profile=signup.teacher,
            to_profile=student,
            kind=model.Relationship.KIND.elder,
            level=model.Relationship.LEVEL.owner,
            )
    if signup.group:
        student.student_in_groups.add(signup.group)
    signup.state = model.TextSignup.STATE.relationship
    signup.student = student
    signup.save()
    model.Post.create(
        signup.family,
        student,
        body,
        from_sms=True,
        email_notifications=False,
        )
    return reply(
        signup.family.phone,
        [student],
        messages.get('RELATIONSHIP', signup.family.lang_code),
        )


def handle_role_update(signup, body):
    """Handle defining role of parent in relation to student."""
    role = get_answer(body, signup.family.phone)

    parent = signup.family
    parent.relationships_from.filter(
        description=parent.role).update(description=role)
    parent.role = role
    parent.save()
    signup.state = model.TextSignup.STATE.name
    signup.save()
    teacher = signup.teacher
    student_rels = parent.student_relationships
    for rel in student_rels:
        model.Post.create(
            parent, rel.student, body, from_sms=True, email_notifications=False)
    return reply(
        parent.phone,
        parent.students,
        messages.get('NAME', parent.lang_code) % teacher,
        )


def handle_name_update(signup, body):
    """Handle defining name of parent."""
    name = get_answer(body, signup.family.phone)

    parent = signup.family
    parent.name = name
    parent.save()
    signup.state = model.TextSignup.STATE.done
    signup.save()
    teacher = signup.teacher
    student_rels = parent.student_relationships
    for rel in student_rels:
        model.Post.create(
            parent, rel.student, body, from_sms=True, email_notifications=False)
        if teacher and teacher.notify_new_parent and teacher.user.email:
            notifications.send_signup_email_notification(teacher, rel)
    return reply(
        parent.phone,
        parent.students,
        interpolate_teacher_names(
            messages.get('ALL_DONE', parent.lang_code),
            parent,
            )
        )



def parse_code(body):
    """
    Return (teacher, group, lang) tuple based on code found in text.

    If no valid code is found, all will be None. If a valid teacher code is
    found, group will be None. If a valid group code is found, both teacher and
    group will be set (teacher will be set to group owner). If no valid
    language code (i.e. one found in ``settings.LANGUAGES``) follows the code,
    the default language code (``settings.LANGUAGE_CODE``) will be returned.

    """
    bits = body.strip().split()
    if not bits:
        return (None, None, None)
    elif len(bits) > 1:
        lang = bits[1].lower().rstrip('.,:;')
        if lang not in settings.LANGUAGE_DICT:
            lang = settings.LANGUAGE_CODE
    else:
        lang = settings.LANGUAGE_CODE
    possible_code = bits[0].rstrip('.,:;').upper()
    try:
        group = model.Group.objects.get(code=possible_code)
    except model.Group.DoesNotExist:
        group = None
        try:
            teacher = model.Profile.objects.get(code=possible_code)
        except model.Profile.DoesNotExist:
            teacher = None
    else:
        teacher = group.owner
    if teacher is None:
        lang = None
    return (teacher, group, lang)



def interpolate_teacher_names(msg, parent):
    """
    Interpolate teachers of parent's students into msg's %s placeholder.

    Avoids making the total message length over 160 if possible.

    """
    students = parent.students
    if not students:
        return msg % u"teachers"
    teachers = list(
        model.Profile.objects.filter(
            school_staff=True,
            relationships_from__to_profile__in=students
            ).distinct()
        )

    if len(students) > 2:
        student_possessive = u"your students'"
    elif len(students) == 2:
        student_possessive = u"%s & %s's" % (
            students[0], students[1])
    else:
        student_possessive = u"%s's" % (students[0])

    # Set up some wording options in order of preference
    options = []
    student_possessive_full = u"%s teachers" % student_possessive
    if len(teachers) == 2:
        options.append(u"%s & %s" % (teachers[0], teachers[1]))
    elif len(teachers) == 1:
        options.append(unicode(teachers[0]))
        student_possessive_full = u"%s teacher" % student_possessive
    options.append(student_possessive_full)

    # Take the first option that results in a message shorter than 160
    # characters. If all options are too long, revert to the first one.
    first = None
    for o in options:
        interpolated = msg % o
        if first is None:
            first = interpolated
        if len(interpolated) <= 160:
            return interpolated
    return first



def reply(phone, students, body):
    """Save given reply to given students' villages before returning it."""
    for student in students:
        model.Post.create(
            None, student, body, in_reply_to=phone, email_notifications=False)
    return body



def get_answer(msg, source):
    """
    Extract an answer to a question from an incoming text.

    Assume that the expected answer is a single name or short phrase.

    Strips leading and trailing whitespace, ignores all lines except the first
    non-empty one.

    """
    stripped_lines = (l.strip() for l in msg.splitlines())
    non_empty_lines = [l for l in stripped_lines if l]
    answer = non_empty_lines[0] if non_empty_lines else ""

    if len(answer.split()) > MAX_EXPECTED_ANSWER_LENGTH:
        track_sms('long answer', source, msg)

    return answer



def track_sms(event, source, body, **extra):
    """Track ``event`` regarding SMS ``body`` from ``source``."""
    properties = {
        'distinct_id': source,
        'phone': source,
        'message': body,
        }
    properties.update(extra)

    tasks.mixpanel.delay('track', 'sms: %s' % event, properties)



def track_signup(parent, teacher, group=None):
    """Track that ``parent`` signed up with ``teacher`` (in ``group``)."""
    properties = {
        'distinct_id': teacher.user_id,
        'phone': parent.phone,
        }
    if group is not None:
        properties.update(
            {
                'groupId': group.id,
                'groupName': group.name,
                },
            )

    # Track it as a 'parent signup' event
    tasks.mixpanel.delay('track', 'parent signup', properties)
    # increment a parentSignups counter on the teacher
    tasks.mixpanel.delay(
        'people_increment', teacher.user_id, {'parentSignups': 1})
    # ... and set a lastParentSignup date on the teacher
    now = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M:%S')
    tasks.mixpanel.delay(
        'people_set', teacher.user_id, {'lastParentSignup': now})
