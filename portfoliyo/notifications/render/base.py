"""Rendering and sending of notifications."""
from django.template.loader import render_to_string

from portfoliyo import email
from portfoliyo import model
from . import collect



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

    collection = collect.NotificationCollection(profile_id)

    # bail out if there's nothing to do
    if not collection:
        return False

    subject = render_to_string(
        collection.get_subject_template(), collection.context)

    # @@@ strip consecutive newlines from textual templates
    text = ''
    html = ''

    email.send_multipart(subject, text, html, [profile.user.email])

    return True
