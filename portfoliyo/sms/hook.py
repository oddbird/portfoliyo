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
    if body.strip().lower().startswith('xjgdlw'):
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

    if profile.state == model.Profile.STATE.kidname and profile.invited_by:
        return handle_new_student(
            parent=profile,
            teacher=profile.invited_by,
            student_name=body.strip(),
            )
    elif profile.state == model.Profile.STATE.relationship:
        return handle_role_update(parent=profile, role=body.strip())
    elif profile.state == model.Profile.STATE.name:
        return handle_name_update(parent=profile, name=body.strip())

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
    teacher, group = get_teacher_and_group(body)
    if teacher is not None:
        model.Profile.create_with_user(
            school=teacher.school,
            phone=source,
            state=model.Profile.STATE.kidname,
            invited_by=teacher,
            invited_in_group=group,
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
            level=model.Relationship.LEVEL.owner,
            )
    if parent.invited_in_group:
        student.student_in_groups.add(parent.invited_in_group)
    parent.state = model.Profile.STATE.relationship
    parent.save()
    model.Post.create(
        parent, student, student_name, from_sms=True, email_notifications=False)
    return reply(
        parent.phone,
        [student],
        "And what is your relationship to that child (mother, father, ...)?",
        )


def handle_role_update(parent, role):
    """Handle defining role of parent in relation to student."""
    parent.relationships_from.filter(
        description=parent.role).update(description=role)
    parent.role = role
    parent.state = model.Profile.STATE.name
    parent.save()
    teacher = parent.invited_by
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


def handle_name_update(parent, name):
    """Handle defining name of parent."""
    parent.name = name
    parent.state = model.Profile.STATE.done
    parent.save()
    teacher = parent.invited_by
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
    possible_code = body.strip().split()[0].rstrip('.,:;').upper()
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



def reply(phone, students, body):
    """Save given reply to given students' villages before returning it."""
    for student in students:
        model.Post.create(
            None, student, body, in_reply_to=phone, email_notifications=False)
    return body
