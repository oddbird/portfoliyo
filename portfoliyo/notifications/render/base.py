"""Rendering and sending of notifications."""
import re

from django.template.loader import render_to_string

from portfoliyo import email
from portfoliyo import model
from . import collect


HTML_TEMPLATE = 'notifications/activity.html'
TEXT_TEMPLATE = 'notifications/activity.txt'


consecutive_newlines = re.compile('\n+')


def send(profile_id):
    """
    Send activity notification(s) to user with given profile ID.

    Return ``True`` if email was sent, ``False`` otherwise.

    """
    profile = model.Profile.objects.select_related('user').get(pk=profile_id)
    user = profile.user
    # bail out if user can't receive notification emails anyway
    if not (user.email and user.is_active):
        return False

    collection = collect.NotificationCollection(profile)

    # bail out if there's nothing to do
    if not collection:
        return False

    subject = render_to_string(
        collection.get_subject_template(), collection.context)

    text = consecutive_newlines.sub(
        '\n', render_to_string(TEXT_TEMPLATE, collection.context))
    html = render_to_string(HTML_TEMPLATE, collection.context)

    email.send_multipart(subject, text, html, [profile.user.email])

    return True
