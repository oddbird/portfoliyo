"""Rendering and sending of notifications."""
import re

from django.conf import settings
from django.template.loader import render_to_string
import premailer

from portfoliyo import email
from portfoliyo import model
from . import collect


HTML_TEMPLATE = 'notifications/activity.html'
TEXT_TEMPLATE = 'notifications/activity.txt'


consecutive_newlines = re.compile('\n\n+')



class NothingToDo(Exception):
    pass



def send(profile_id, clear=True):
    """
    Send activity notification(s) to user with given profile ID.

    If ``clear`` is ``True`` (the default), clear all notifications for this
    profile ID.

    Return ``True`` if email was sent, ``False`` otherwise.

    """
    profile = model.Profile.objects.select_related('user').get(pk=profile_id)
    user = profile.user
    # bail out if user can't receive notification emails anyway
    if not (user.email and user.is_active):
        return False

    try:
        subject, text, html = render(profile, clear=clear)
    except NothingToDo:
        return False

    email.send_multipart(subject, text, html, [profile.user.email])

    return True



def render(profile, clear=True):
    """
    Render notification email for given profile; return (subject, text, html).

    If ``clear`` is set to ``False``, will not clear rendered notifications.

    Raise ``NothingToDo`` if there are no notifications to render.

    """
    collection = collect.NotificationCollection(profile, clear=clear)

    # bail out if there's nothing to do
    if not collection:
        raise NothingToDo()

    context = collection.context
    context['BASE_URL'] = settings.PORTFOLIYO_BASE_URL

    subject = render_to_string(collection.get_subject_template(), context)

    text = consecutive_newlines.sub(
        '\n\n', render_to_string(TEXT_TEMPLATE, context))
    html = premailer.transform(
        render_to_string(HTML_TEMPLATE, context),
        base_url=settings.PORTFOLIYO_BASE_URL,
        )

    return subject, text, html
