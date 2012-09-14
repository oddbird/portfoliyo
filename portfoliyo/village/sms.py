"""Village SMS-handling."""
from ..users import models as user_models
from . import models


def receive_sms(source, body):
    """
    Hook for when an SMS is received.

    Return None if no reply should be sent, or text of reply.

    """
    try:
        profile = user_models.Profile.objects.select_related(
            'user').get(phone=source)
    except user_models.Profile.DoesNotExist:
        # @@@ log this?
        return None

    profile.user.is_active = True
    profile.user.save()

    students = profile.students

    if len(students) > 1:
        return (
            "You're part of more than one student's Portfoliyo.org Village; "
            "we're not yet able to route your texts. Sorry!"
            )
    elif not students:
        return (
            "Sorry, you're not part of any student's Portfoliyo.org Village; "
            "we're not able to deliver your message. Sorry!"
            )

    models.Post.create(profile, students[0], body)
