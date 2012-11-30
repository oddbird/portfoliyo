"""Village SMS-handling."""
import logging

from portfoliyo import model, notifications


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
            logger.warning('User %s has multiple active signups!' % source)
            # not much we can do but just pick one arbitrarily
        signup = active_signups[0]
    else:
        signup = None

    teacher, group = get_teacher_and_group(body)
    if teacher is not None:
        return handle_subsequent_code(profile, teacher, group, signup)

    if signup is not None:
        if signup.state == model.TextSignup.STATE.kidname:
            return handle_new_student(
                signup=signup,
                student_name=body.strip(),
                )
        elif signup.state == model.TextSignup.STATE.relationship:
            return handle_role_update(signup=signup, role=body.strip())
        elif signup.state == model.TextSignup.STATE.name:
            return handle_name_update(signup=signup, name=body.strip())

    students = profile.students

    if not students:
        logger.warning(
            "Text from %s (has no students): %s" % (source, body))
        return (
            "You're not part of any student's Portfoliyo Village, "
            "so we're not able to deliver your message. Sorry!"
            )

    for student in students:
        model.Post.create(profile, student, body, from_sms=True)

    if activated:
        return reply(
            source,
            students,
            "Thank you! You can text this number any time "
            "to talk with %s's teachers." % students[0].name
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
        logger.warning("Unknown text from %s: %s" % (source, body))
        return (
            "Bummer, we don't recognize your invite code! "
            "Please make sure it's typed exactly as it is on the paper."
            )


def handle_subsequent_code(profile, teacher, group, signup):
    """
    Handle a second code from an already-signed-up parent.

    If ``signup`` is not ``None``, it is an already-in-progress but
    not-yet-finished signup. In that case, we mark it done and transfer its
    state to the new signup so we still get answers to the questions.

    """
    student = profile.students[0] if profile.students else None
    model.TextSignup.objects.create(
        family=profile,
        teacher=teacher,
        group=group,
        student=student,
        state=signup.state if signup else model.TextSignup.STATE.done,
        )
    if student:
        model.Relationship.objects.get_or_create(
            from_profile=teacher,
            to_profile=student,
            defaults={'level': model.Relationship.LEVEL.owner},
            )
        if group:
            group.students.add(student)

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


def handle_new_student(signup, student_name):
    """Handle addition of a student to a just-signing-up parent's account."""
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
        student_name,
        from_sms=True,
        email_notifications=False,
        )
    return reply(
        signup.family.phone,
        [student],
        "And what is your relationship to that child (mother, father, ...)?",
        )


def handle_role_update(signup, role):
    """Handle defining role of parent in relation to student."""
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
            parent, rel.student, role, from_sms=True, email_notifications=False)
    return reply(
        parent.phone,
        parent.students,
        "Last question: what is your name? (So %s knows who is texting.)"
        % teacher,
        )


def handle_name_update(signup, name):
    """Handle defining name of parent."""
    parent = signup.family
    parent.name = name
    parent.save()
    signup.state = model.TextSignup.STATE.done
    signup.save()
    teacher = signup.teacher
    student_rels = parent.student_relationships
    for rel in student_rels:
        model.Post.create(
            parent, rel.student, name, from_sms=True, email_notifications=False)
        if teacher and teacher.email_notifications and teacher.user.email:
            notifications.send_signup_email_notification(teacher, rel)
    return reply(
        parent.phone,
        parent.students,
        "All done, thank you! You can text this number any time "
        "to talk with %s's teachers." % rel.student.name
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

    Avoids making the total message length over 160; falls back to "student's
    teachers" with arbitrary student if necessary.

    """



def reply(phone, students, body):
    """Save given reply to given students' villages before returning it."""
    for student in students:
        model.Post.create(
            None, student, body, in_reply_to=phone, email_notifications=False)
    return body
