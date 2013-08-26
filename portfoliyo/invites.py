"""Sending invites to prospective users by email or SMS."""
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.http import int_to_base36

from portfoliyo import email



def send_invite_email(profile, template_name, extra_context=None,
                      token_generator=default_token_generator):
    """Generates a one-use invite link and sends to the user."""
    c = {
        'uidb36': int_to_base36(profile.user.id),
        'profile': profile,
        'token': token_generator.make_token(profile.user),
        'base_url': settings.PORTFOLIYO_BASE_URL,
    }
    c.update(extra_context or {})

    email.send_templated_multipart(template_name, c, [profile.user.email])



def send_invite_sms(profile, template_name, extra_context):
    """Sends an invite SMS to a user."""
    c = {'profile': profile}
    c.update(extra_context or {})
    body = loader.render_to_string(template_name, c).strip()
    if len(body) <= 160:
        messages = [body.replace("\n", " ")]
    else:
        messages = body.split("\n")
    for body in messages:
        profile.send_sms(body)
