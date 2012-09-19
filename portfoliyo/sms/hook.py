"""Village SMS-handling."""
from portfoliyo import model


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

    if not profile.user.is_active:
        profile.user.is_active = True
        profile.user.save()

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
        return (
            "You're part of more than one student's Portfoliyo Village; "
            "we're not yet able to route your texts. We'll fix that soon!"
            )
    elif not students:
        return (
            "You're not part of any student's Portfoliyo Village, "
            "so we're not able to deliver your message. Sorry!"
            )

    model.Post.create(profile, students[0], body)


def handle_unknown_source(source, body):
    """Handle a text from an unknown user."""
    teacher, parent_name = get_teacher_and_name(body)
    if teacher is not None:
        if parent_name:
            model.Profile.create_with_user(
                phone=source,
                state=model.Profile.STATE.kidname,
                invited_by=teacher,
                )
            return (
                "Thanks! What is the name of your child in %s's class?"
                % teacher.name
                )
        else:
            return "Please include your name after the code."
    else:
        return (
            "Bummer, we don't recognize your number! "
            "Have you been invited by your child's teacher "
            "to use Portfoliyo?"
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
        student = model.Profile.create_with_user(name=student_name)
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
    parent.state = model.Profile.STATE.relationship
    parent.save()
    model.Post.create(parent, student, student_name)
    return (
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
        model.Post.create(parent, student, role)
    return  (
        "All done, thank you! You can text this number any time "
        "to talk with your child's teachers."
        )



def get_teacher_and_name(body):
    """
    Try to split a text into a valid teacher code and parent name.

    On success, return tuple (teacher-profile, parent-name). Parent name can be
    empty string if entire text is teacher code.

    On failure to find valid teacher code, return (None, '').

    """
    body = body.strip()
    try:
        possible_code, parent_name = body.split(' ', 1)
    except ValueError:
        possible_code = body
        parent_name = ''
    try:
        teacher = model.Profile.objects.get(code=possible_code.upper())
    except model.Profile.DoesNotExist:
        return (None, '')
    return (teacher, parent_name)
