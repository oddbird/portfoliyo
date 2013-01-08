"""Integration tests for email-sending."""
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import html
import pytest

from portfoliyo.notifications import record
from portfoliyo.notifications.render import base
from portfoliyo.tests import factories



@pytest.fixture
def recip(request, db):
    """A user who can receive notifications."""
    # Turn all notification triggers off; we want to trigger sending manually
    return factories.ProfileFactory.create(
        user__email='foo@example.com',
        user__is_active=True,
        notify_new_parent=False,
        notify_parent_text=False,
        notify_added_to_village=False,
        notify_joined_my_village=False,
        notify_teacher_post=False,
        )



class TestSend(object):
    def test_send_only_if_email(self, db):
        """If user has no email, notifications not queried or sent."""
        p = factories.ProfileFactory.create(user__email=None)
        assert not base.send(p.id)


    def test_send_only_if_active(self, db):
        """If user is inactive, notifications not queried or sent."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=False)
        assert not base.send(p.id)


    def test_send_only_if_notifications(self, db, redis):
        """If there are no notifications, don't try to send an email."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=True)
        assert not base.send(p.id)


    def test_generic_subject_single_student(self, recip):
        """Generic subject if multiple notification types, single student."""
        rel = factories.RelationshipFactory.create(
            from_profile=recip, to_profile__name='A Student')
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student)

        record.added_to_village(recip, other_rel.elder, rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in A Student's village."


    def test_generic_subject_multiple_students(self, recip):
        """Generic subject if multiple notification types, multiple students."""
        rel = factories.RelationshipFactory.create(from_profile=recip)
        other_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            from_profile=recip, to_profile=other_rel.student)

        record.added_to_village(recip, other_rel.elder, other_rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in two of your villages."


    def assert_multi_email(self,
                           subject=None,
                           html_snippets=None,
                           text_snippets=None,
                           snippet_context=None,
                           ):
        """
        Make assertions about a multipart/alternatives email.

        Assert that there is only one email in the testing outbox, that it's
        subject is ``subject``, and that all the snippets in ``html_snippets``
        and ``text_snippets`` (both lists) are found in the HTML and text
        portions of the email body, respectively.

        If ``snippet_context`` is set, it is used as the context for a % string
        interpolation on each snippet.

        """
        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        if subject is not None:
            assert email.subject == subject

        assert len(email.alternatives) == 1
        assert email.alternatives[0][1] == 'text/html'
        parsed_html_body = html.parse_html(email.alternatives[0][0])

        for html_bit in html_snippets or []:
            if snippet_context:
                html_bit = html_bit % snippet_context
            parsed_bit = html.parse_html(html_bit)
            assert parsed_html_body.count(parsed_bit)

        for text_bit in text_snippets or []:
            if snippet_context:
                text_bit = text_bit % snippet_context
            assert text_bit in email.body


    @pytest.mark.parametrize('params', [
            (
                [("Teacher1", "StudentX")],
                "Teacher1 added you to StudentX's village.",
                ['<li>Teacher1 added you to '
                 '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'],
                ["Teacher1 added you to StudentX's village. "
                 "Start a conversation: %(StudentXUrl)s"]
                ),
            (
                [("Teacher1", "StudentX"), ("Teacher1", "StudentY")],
                "Teacher1 added you to two villages.",
                [],
                [],
                ),
            (
                [("Teacher1", "StudentX"), ("Teacher2", "StudentY")],
                "Two teachers added you to two villages.",
                [],
                [],
                ),
            ])
    def test_added_to_village(self, params, recip):
        """Test subject/body for added-to-village notifications."""
        combos, expected_subject, expected_html, expected_text = params
        name_map = {}
        context = {}
        for teacher_name, student_name in combos:
            if teacher_name not in name_map:
                name_map[teacher_name] = factories.ProfileFactory.create(
                    name=teacher_name, school_staff=True)
            if student_name not in name_map:
                name_map[student_name] = factories.ProfileFactory.create(
                    name=student_name, school_staff=True)
                context[student_name + 'Url'] = reverse(
                    'village', kwargs={'student_id': name_map[student_name].id})
                factories.RelationshipFactory.create(
                    from_profile=recip, to_profile=name_map[student_name])
            teacher = name_map[teacher_name]
            student = name_map[student_name]
            factories.RelationshipFactory.create(
                from_profile=teacher, to_profile=student)
            record.added_to_village(recip, teacher, student)

        assert base.send(recip.id)
        self.assert_multi_email(
            expected_subject, expected_html, expected_text, context)


    @pytest.mark.parametrize('params', [
            (["StudentX"], ["Teacher1"], "Teacher1 joined StudentX's village."),
            (
                ["StudentX", "StudentY"], ["Teacher1"],
                "Teacher1 joined two of your villages."
                ),
            (
                ["StudentX"], ["Teacher1", "Teacher2"],
                "Two teachers joined StudentX's village."
                ),
            (
                ["StudentX", "StudentY"], ["Teacher1", "Teacher2"],
                "Two teachers joined two of your villages."
                ),
            ])
    def test_only_new_teachers_subject(self, params, recip):
        """Test subject/body for new-teacher notifications."""
        student_names, teacher_names, expected = params
        teacher_profiles = []
        for teacher_name in teacher_names:
            teacher_profiles.append(
                factories.ProfileFactory.create(name=teacher_name))
        for student_name in student_names:
            rel = factories.RelationshipFactory.create(
                from_profile=recip, to_profile__name=student_name)
            for teacher in teacher_profiles:
                factories.RelationshipFactory.create(
                    from_profile=teacher, to_profile=rel.student)
                record.new_teacher(recip, teacher, rel.student)

        assert base.send(recip.id)
        self.assert_multi_email(expected)
