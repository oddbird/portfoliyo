"""
Email-sending.

"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def send_templated_multipart(template_name, context, recipients,
                             sender=None, fail_silently=False):
    """
    Send a templated multi-part e-mail with both HTML and text parts.

    ``template_name`` should not include an extension. Both HTML (``.html``)
    and text (``.txt``) versions must exist, as well as ``.subject.txt`` for
    the subject. For example, 'emails/public_submit' will use
    ``public_submit.html``, ``public_submit.txt``, and
    ``public_submit.subject.txt``.

    ``context`` should be a dictionary; all three templates (HTML,
    text, and subject) are rendered with this same context.

    Other arguments are the same as the ``send_multipart`` function in this
    module.

    """
    text_part = render_to_string('%s.txt' % template_name, context)
    html_part = render_to_string('%s.html' % template_name, context)
    subject = render_to_string('%s.subject.txt' % template_name, context)

    return send_multipart(
        subject, text_part, html_part, recipients, sender, fail_silently)




def send_multipart(subject, text_part, html_part, recipients,
                   sender=None, fail_silently=False):
    """
    Send a multi-part email with both HTML and text parts.

    ``subject`` should be the email subject as a string (newlines will be
    replaced with spaces).

    ``text_part`` and ``html_part`` should be text and HTML versions of the
    email body, as strings.

    ``recipients`` should be a list of email addresses.

    ``sender`` can be an email, 'Name <email>' or None. If unspecified, the
    ``DEFAULT_FROM_EMAIL`` setting will be used.

    """
    sender = sender or settings.DEFAULT_FROM_EMAIL

    # collapse newlines in subject to spaces
    subject = u" ".join(subject.splitlines()).strip()
    msg = EmailMultiAlternatives(subject, text_part, sender, recipients)
    msg.attach_alternative(html_part, "text/html")
    return msg.send(fail_silently)
