"""
Email-sending.

"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def send_multipart(template_name, context, recipients,
                   sender=None, fail_silently=False):
    """
    Send a multi-part e-mail with both HTML and text parts.

    ``template_name`` should not include an extension. Both HTML (``.html``)
    and text (``.txt``) versions must exist, as well as ``.subject.txt`` for
    the subject. For example, 'emails/public_submit' will use
    ``public_submit.html``, ``public_submit.txt``, and
    ``public_submit.subject.txt``.

    ``context`` should be a dictionary; all three templates (HTML,
    text, and subject) are rendered with this same context.

    ``recipients`` should be a list of email addresses, e.g. ['a@b.com',
    'c@d.com'].

    ``sender`` can be an email, 'Name <email>' or None. If unspecified, the
    ``DEFAULT_FROM_EMAIL`` setting will be used.

    """

    sender = sender or settings.DEFAULT_FROM_EMAIL

    text_part = render_to_string('%s.txt' % template_name, context)
    html_part = render_to_string('%s.html' % template_name, context)
    # collapse newlines in subject to spaces
    subject = u" ".join(
        render_to_string(
            '%s.subject.txt' % template_name, context).splitlines()
        )

    msg = EmailMultiAlternatives(subject, text_part, sender, recipients)
    msg.attach_alternative(html_part, "text/html")
    return msg.send(fail_silently)
