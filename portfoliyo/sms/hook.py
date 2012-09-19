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

    if not profile.user.is_active:
        profile.user.is_active = True
        profile.user.save()

    if profile.state == model.Profile.STATE.kidname:
        student = model.Profile.create_with_user(name=body)
        model.Relationship.objects.create(
            from_profile=profile,
            to_profile=student,
            kind=model.Relationship.KIND.elder,
            )
        if profile.invited_by:
            model.Relationship.objects.create(
                from_profile=profile.invited_by,
                to_profile=student,
                kind=model.Relationship.KIND.elder,
                )
        profile.state = model.Profile.STATE.relationship
        profile.save()
        return (
            "Last question: what is your relationship to that child "
            "(mother, father, ...)?"
            )

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
