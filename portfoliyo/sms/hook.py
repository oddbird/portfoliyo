"""Village SMS-handling."""
import logging

from portfoliyo import model


logger = logging.getLogger(__name__)



def receive_sms(source, body):
    """
    Hook for when an SMS is received.

    Return None if no reply should be sent, or text of reply.

    """
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

    if profile.state == model.Profile.STATE.kidname and profile.invited_by:
        return handle_new_student(
            parent=profile,
            teacher=profile.invited_by,
            student_name=body.strip(),
            )
    elif profile.state == model.Profile.STATE.relationship:
        return handle_role_update(parent=profile, role=body.strip())

    students = profile.students

    if len(students) > 1:
        logger.warning(
            "Text from %s (has multiple students): %s" % (source, body))
        return (
            "You're part of more than one student's Portfoliyo Village; "
            "we're not yet able to route your texts. We'll fix that soon!"
            )
    elif not students:
        logger.warning(
            "Text from %s (has no students): %s" % (source, body))
        return (
            "You're not part of any student's Portfoliyo Village, "
            "so we're not able to deliver your message. Sorry!"
            )

    model.Post.create(profile, students[0], body, from_sms=True)

    if activated:
        return reply(
            source,
            profile.students,
            "Thank you! You can text this number any time "
            "to talk with %s's teachers." % students[0].name
        )



def handle_unknown_source(source, body):
    """Handle a text from an unknown user."""
    teacher, group, parent_name = get_teacher_group_and_name(body)
    if teacher is not None:
        if parent_name:
            model.Profile.create_with_user(
                school=teacher.school,
                phone=source,
                name=parent_name,
                state=model.Profile.STATE.kidname,
                invited_by=teacher,
                invited_in_group=group,
                )
            return (
                "Thanks! What is the name of your child in %s's class?"
                % teacher.name
                )
        else:
            return "Please include your name after the code."
    else:
        logger.error("Unknown text from %s: %s" % (source, body))
        return (
            "Bummer, we don't recognize your invite code! "
            "Please make sure it's typed exactly as it is on the paper, "
            "followed by a space and then your name."
            )



def handle_new_student(parent, teacher, student_name):
    """Handle addition of a student to a just-signing-up parent's account."""
    possible_dupes = model.Profile.objects.filter(
        name__iexact=student_name,
        relationships_to__from_profile=teacher,
        )
    if possible_dupes:
        dupe_found = True
        student = possible_dupes[0]
    else:
        dupe_found = False
        student = model.Profile.create_with_user(
            name=student_name, invited_by=teacher, school=teacher.school)
    model.Relationship.objects.create(
        from_profile=parent,
        to_profile=student,
        kind=model.Relationship.KIND.elder,
        )
    if not dupe_found:
        model.Relationship.objects.create(
            from_profile=teacher,
            to_profile=student,
            kind=model.Relationship.KIND.elder,
            )
    if parent.invited_in_group:
        student.student_in_groups.add(parent.invited_in_group)
    parent.state = model.Profile.STATE.relationship
    parent.save()
    model.Post.create(parent, student, student_name, from_sms=True)
    return reply(
        parent.phone,
        [student],
        "Last question: what is your relationship to that child "
        "(mother, father, ...)?"
        )


def handle_role_update(parent, role):
    """Handle defining role of parent in relation to student."""
    parent.relationships_from.filter(
        description=parent.role).update(description=role)
    parent.role = role
    parent.state = model.Profile.STATE.done
    parent.save()
    students = parent.students
    for student in students:
        model.Post.create(parent, student, role, from_sms=True)
    return reply(
        parent.phone,
        parent.students,
        "All done, thank you! You can text this number any time "
        "to talk with %s's teachers." % students[0].name
        )



def get_teacher_group_and_name(body):
    """
    Try to split a text into a valid teacher/group code and parent name.

    On success, return tuple (teacher-profile, group, parent-name). Parent name
    can be empty string if entire text is code. Group can be ``None`` if code
    is teacher code.

    On failure to find valid code, return (None, None, '').

    """
    body = body.strip()
    try:
        possible_code, parent_name = body.split(' ', 1)
    except ValueError:
        possible_code = body
        parent_name = ''
    possible_code = possible_code.rstrip('.,:;').upper()
    try:
        group = model.Group.objects.get(code=possible_code)
    except model.Group.DoesNotExist:
        group = None
        try:
            teacher = model.Profile.objects.get(code=possible_code)
        except model.Profile.DoesNotExist:
            teacher = None
            parent_name = ''
    else:
        teacher = group.owner
    return (teacher, group, parent_name)



def reply(phone, students, body):
    """Save given reply to given students' villages before returning it."""
    for student in students:
        model.Post.create(None, student, body, in_reply_to=phone)
    return body
