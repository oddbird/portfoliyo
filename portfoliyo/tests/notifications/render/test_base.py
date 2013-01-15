"""Integration tests for email-sending."""
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import html
import mock
import pytest

from portfoliyo.notifications import record
from portfoliyo.notifications.render import base
from portfoliyo.tests import factories


base_url = settings.PORTFOLIYO_BASE_URL


@pytest.fixture
def recip(request, db):
    """A user who can receive notifications."""
    kw = {
        'user__email': 'foo@example.com',
        'user__is_active': True,
        'notify_new_parent': True,
        'notify_parent_text': True,
        'notify_added_to_village': True,
        'notify_joined_my_village': True,
        'notify_teacher_post': True,
        }

    if 'params' in request.funcargnames:
        params = request.getfuncargvalue('params')
        prefs = params.get('prefs', {})
        kw.update(prefs)

    # Temporarily patch the ``send_notification_email`` task to do nothing; we
    # want to trigger the actual email-sending ourselves in these tests.
    patcher = mock.patch('portfoliyo.tasks.send_notification_email')
    patcher.start()

    request.addfinalizer(patcher.stop)

    return factories.ProfileFactory.create(**kw)



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
            assert parsed_html_body.count(parsed_bit), "%s not in %s" % (
                parsed_bit, parsed_html_body)

        for text_bit in text_snippets or []:
            if snippet_context:
                text_bit = text_bit % snippet_context
            assert text_bit in email.body, "%s not in %s" % (
                text_bit, email.body)


    @pytest.mark.parametrize('params', [
            {
                'scenario': [("Teacher1", "StudentX")],
                'subject': "Teacher1 added you to StudentX's village.",
                'html': [
                    '<li>Teacher1 added you to '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    ],
                'text': [
                    "- Teacher1 added you to StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s"
                    ]
                },
            {
                'scenario': [
                    ("Teacher1", "StudentX"), ("Teacher1", "StudentY")],
                'subject': "Teacher1 added you to two villages.",
                'html': [
                    '<li>Teacher1 added you to two student villages: <ul>'
                    '<li><a href="%(StudentXUrl)s">StudentX</a></li>'
                    '<li><a href="%(StudentYUrl)s">StudentY</a></li>'
                    '</ul></li>'
                    ],
                'text': [
                    '- Teacher1 added you to two student villages:\n'
                    '-- StudentX: %(StudentXUrl)s\n'
                    '-- StudentY: %(StudentYUrl)s\n'
                    ],
                },
            {
                'scenario': [
                    ("Teacher1", "StudentX"), ("Teacher2", "StudentY")],
                'subject': "Two teachers added you to two villages.",
                'html': [
                    '<li>Teacher1 added you to '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>',
                    '<li>Teacher2 added you to '
                    '<a href="%(StudentYUrl)s">StudentY\'s village</a>.</li>',
                    ],
                'text': [
                    "- Teacher1 added you to StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s",
                    "- Teacher2 added you to StudentY's village. "
                    "Start a conversation: %(StudentYUrl)s",
                    ],
                },
            {
                'scenario': [
                    ("Teacher1", "StudentX"), ("Teacher1", "StudentY")],
                'prefs': {'notify_added_to_village': False},
                'subject': "Teacher1 added you to two villages.",
                'html': [
                    '<li>Teacher1 added you to two student villages: '
                    '<a href="%(StudentXUrl)s">StudentX</a>, '
                    'and <a href="%(StudentYUrl)s">StudentY</a>.'
                    '</li>'
                    ],
                'text': [
                    '- Teacher1 added you to two student villages: '
                    'StudentX, and StudentY.'
                    ],
                },
            {
                'scenario': [
                    ("Teacher1", "StudentW"),
                    ("Teacher1", "StudentX"),
                    ("Teacher1", "StudentY"),
                    ("Teacher1", "StudentZ"),
                    ],
                'prefs': {'notify_added_to_village': False},
                'subject': "Teacher1 added you to four villages.",
                'html': [
                    '<li>Teacher1 added you to four student villages: '
                    '<a href="%(StudentWUrl)s">StudentW</a>, '
                    '<a href="%(StudentXUrl)s">StudentX</a>, '
                    '<a href="%(StudentYUrl)s">StudentY</a>, '
                    'and one more village.'
                    '</li>'
                    ],
                'text': [
                    '- Teacher1 added you to four student villages: '
                    'StudentW, StudentX, StudentY, and one more village.'
                    ],
                },
            ])
    def test_added_to_village(self, params, recip):
        """Test subject/body for added-to-village notifications."""
        name_map = {}
        context = {}
        for teacher_name, student_name in params['scenario']:
            if teacher_name not in name_map:
                name_map[teacher_name] = factories.ProfileFactory.create(
                    name=teacher_name, school_staff=True)
            if student_name not in name_map:
                name_map[student_name] = factories.ProfileFactory.create(
                    name=student_name, school_staff=True)
                context[student_name + 'Url'] = base_url + reverse(
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
            params['subject'], params['html'], params['text'], context)


    @pytest.mark.parametrize('params', [
            {
                'scenario': (["StudentX"], ["Teacher1"]),
                'subject': "Teacher1 joined StudentX's village.",
                'html': [
                    '<li>Teacher1 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    ],
                'text': [
                    "- Teacher1 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s"
                    ],
                },
            {
                'scenario': (["StudentX", "StudentY"], ["Teacher1"]),
                'subject': "Teacher1 joined two of your villages.",
                'html': [
                    '<ul class="requested">'
                    '<li>Teacher1 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    '<li>Teacher1 joined '
                    '<a href="%(StudentYUrl)s">StudentY\'s village</a>.</li>'
                    '</ul>'
                    ],
                'text': [
                    "- Teacher1 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    "- Teacher1 joined StudentY's village. "
                    "Start a conversation: %(StudentYUrl)s\n"
                    ],
                },
            {
                'scenario': (["StudentX"], ["Teacher1", "Teacher2"]),
                'subject': "Two teachers joined StudentX's village.",
                'html': [
                    '<ul class="requested">'
                    '<li>Teacher1 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    '<li>Teacher2 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    '</ul>'
                    ],
                'text': [
                    "- Teacher1 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    "- Teacher2 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    ],
                },
            {
                'scenario': (
                    ["StudentX", "StudentY"], ["Teacher1", "Teacher2"]),
                'subject': "Two teachers joined two of your villages.",
                'html': [
                    '<ul class="requested">'
                    '<li>Teacher1 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    '<li>Teacher2 joined '
                    '<a href="%(StudentXUrl)s">StudentX\'s village</a>.</li>'
                    '<li>Teacher1 joined '
                    '<a href="%(StudentYUrl)s">StudentY\'s village</a>.</li>'
                    '<li>Teacher2 joined '
                    '<a href="%(StudentYUrl)s">StudentY\'s village</a>.</li>'
                    '</ul>'
                    ],
                'text': [
                    "- Teacher1 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    "- Teacher2 joined StudentX's village. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    "- Teacher1 joined StudentY's village. "
                    "Start a conversation: %(StudentYUrl)s\n"
                    "- Teacher2 joined StudentY's village. "
                    "Start a conversation: %(StudentYUrl)s\n"
                    ],
                },
            ])
    def test_new_teachers(self, params, recip):
        """Test subject/body for new-teacher notifications."""
        student_names, teacher_names = params['scenario']
        teacher_profiles = []
        context = {}
        for teacher_name in teacher_names:
            teacher_profiles.append(
                factories.ProfileFactory.create(name=teacher_name))
        for student_name in student_names:
            rel = factories.RelationshipFactory.create(
                from_profile=recip, to_profile__name=student_name)
            context[student_name + 'Url'] = base_url + reverse(
                'village', kwargs={'student_id': rel.to_profile_id})
            for teacher in teacher_profiles:
                factories.RelationshipFactory.create(
                    from_profile=teacher, to_profile=rel.student)
                record.new_teacher(recip, teacher, rel.student)

        assert base.send(recip.id)
        self.assert_multi_email(
            params['subject'], params['html'], params['text'], context)
