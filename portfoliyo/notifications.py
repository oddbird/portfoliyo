"""Notifications."""
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import loader


def send_email_notification(profile, post):
    """Notify user about post."""
    rel = post.get_relationship()
    role = rel.description_or_role if rel else post.author.role
    c = {
        'profile': profile,
        'post': post,
        'author_role': role,
        'village_url': (
            settings.PORTFOLIYO_BASE_URL +
            reverse('village', kwargs={'student_id': post.student.id})
            ),
        'profile_url': settings.PORTFOLIYO_BASE_URL + reverse('edit_profile'),
    }

    subject = loader.render_to_string('notifications/new_post_subject.txt', c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string('notifications/new_post_email.txt', c)
    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [profile.user.email])
