"""Village SMS-handling."""
import logging

from portfoliyo import model, notifications


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
            source, profile.students, "No problem! Sorry to have bothered you.")

    activated = False
    if not profile.user.is_active:
        profile.user.is_active = True
        profile.user.save()
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

    teacher, group = get_teacher_and_group(body)
    if teacher is not None:
        return handle_subsequent_code(profile, teacher, group, signup)

    if signup is not None:
        if signup.state == model.TextSignup.STATE.kidname:
            return handle_new_student(signup, body)
        elif signup.state == model.TextSignup.STATE.relationship:
            return handle_role_update(signup, body)
        elif signup.state == model.TextSignup.STATE.name:
            return handle_name_update(signup, body)

    students = profile.students

    if not students:
        logger.warning(
            "Text from %s (has no students): %s", source, body)
        return (
            "Sorry, we can't find find any students connected to your number, "
            "so we're not able to deliver your message. "
            "Please contact your student's teacher for help."
            )

    for student in students:
        model.Post.create(profile, student, body, from_sms=True)

    if activated:
        return reply(
            source,
            students,
            interpolate_teacher_names(
                "Thank you! You can text this number to talk with %s.", profile)
        )



def handle_unknown_source(source, body):
    """Handle a text from an unknown user."""
    teacher, group = get_teacher_and_group(body)
    if teacher is not None:
        family = model.Profile.create_with_user(
            school=teacher.school,
            phone=source,
            invited_by=teacher,
            )
        model.TextSignup.objects.create(
            family=family,
            teacher=teacher,
            group=group,
            state=model.TextSignup.STATE.kidname,
            )
        return (
            "Thanks! What is the name of your child in %s's class?"
            % teacher.name
            )
    else:
        logger.warning("Unknown text from %s: %s", source, body)
        return (
            "We don't recognize your phone number, "
            "so we don't know who to send your text to! "
            "If you are just signing up, "
            "make sure your invite code is typed correctly."
            )


def handle_subsequent_code(profile, teacher, group, signup):
    """
    Handle a second code from an already-signed-up parent.

    If ``signup`` is not ``None``, it is an already-in-progress but
    not-yet-finished signup. In that case, we mark it done and transfer its
    state to the new signup so we still get answers to the questions.

    """
    student = profile.students[0] if profile.students else None
    new_signup = model.TextSignup.objects.create(
        family=profile,
        teacher=teacher,
        group=group,
        student=student,
        state=signup.state if signup else model.TextSignup.STATE.done,
        )
    notifications.new_parent(teacher, new_signup)
    for student in profile.students:
        model.Relationship.objects.get_or_create(
            from_profile=teacher,
            to_profile=student,
            defaults={'level': model.Relationship.LEVEL.owner},
            )
        if group:
            group.students.add(student)
    notifications.village_additions(profile, [teacher], profile.students)

    msg = "Ok, thanks! You can text %s at this number too." % teacher.name

    if signup:
        follow_ups = {
            model.TextSignup.STATE.kidname: " Now, what's the student's name?",
            model.TextSignup.STATE.relationship:
            " Now, what's your relationship to the student?",
            model.TextSignup.STATE.name: " Now, what's your name?",
            }
        msg = msg + follow_ups.get(signup.state, "")
        signup.state = model.TextSignup.STATE.done
        signup.save()

    return reply(profile.phone, [student] if student else [], msg)


def handle_new_student(signup, body):
    """Handle addition of a student to a just-signing-up parent's account."""
    student_name = get_answer(body)

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
        notifications=False,
        )
    return reply(
        signup.family.phone,
        [student],
        "And what is your relationship to that child (mother, father, ...)?",
        )


def handle_role_update(signup, body):
    """Handle defining role of parent in relation to student."""
    role = get_answer(body)

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
            parent, rel.student, body, from_sms=True, notifications=False)
    return reply(
        parent.phone,
        parent.students,
        "Last question: what is your name? (So %s knows who is texting.)"
        % teacher,
        )


def handle_name_update(signup, body):
    """Handle defining name of parent."""
    name = get_answer(body)

    parent = signup.family
    parent.name = name
    parent.save()
    signup.state = model.TextSignup.STATE.done
    signup.save()
    student_rels = parent.student_relationships
    for rel in student_rels:
        model.Post.create(
            parent, rel.student, body, from_sms=True, notifications=False)
    notifications.new_parent(signup.teacher, signup)
    return reply(
        parent.phone,
        parent.students,
        interpolate_teacher_names(
            "All done, thank you! You can text this number to talk with %s.",
            parent,
            )
        )



def get_teacher_and_group(body):
    """
    Return (teacher, group) tuple based on code found in text.

    If no valid code is found, both will be None. If a valid teacher code is
    found, group will be None. If a valid group code is found, both will be
    set (teacher will be set to group owner).

    """
    try:
        possible_code = body.strip().split()[0].rstrip('.,:;').upper()
    except IndexError:
        return (None, None)
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
    return (teacher, group)



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
            None, student, body, in_reply_to=phone, notifications=False)
    return body



def get_answer(msg):
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
        logger.warning(
            "Unusually long SMS question answer: %s",
            answer,
            extra={'stack': True},
            )

    return answer
