"""Tests for notification-sending."""
from django.core import mail

from portfoliyo import notifications

from portfoliyo.tests import factories



def test_no_html_encoding_in_emails():
    post = factories.PostFactory.create(original_text="What's up?")
    to_notify = factories.RelationshipFactory.create(
        to_profile=post.student,
        from_profile__user__email='foo@example.com',
        ).elder

    notifications.send_post_email_notification(to_notify, post)

    email_body = mail.outbox[0].body
    assert "What's up?" in email_body, email_body
