"""Sending invites to prospective users by email or SMS."""
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template import loader
from django.utils.http import int_to_base36

from portfoliyo import sms



def send_invite_email(user,
                      subject_template_name,
                      email_template_name,
                      use_https=False,
                      token_generator=default_token_generator,
                      from_email=None,
                      extra_context=None,
                      ):
    """Generates a one-use invite link and sends to the user."""
    c = {
        'uid': int_to_base36(user.id),
        'user': user,
        'token': token_generator.make_token(user),
        'protocol': use_https and 'https' or 'http',
    }
    c.update(extra_context or {})

    subject = loader.render_to_string(subject_template_name, c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template_name, c)
    send_mail(subject, email, from_email, [user.email])



def send_invite_sms(user, template_name, extra_context):
    """Sends an invite SMS to a user."""
    c = {'user': user}
    c.update(extra_context or {})
    body = loader.render_to_string(template_name, c).strip()
    if len(body) <= 160:
        messages = [body.replace("\n", " ")]
    else:
        messages = body.split("\n")
    for body in messages:
        sms.send(user.profile.phone, body)
