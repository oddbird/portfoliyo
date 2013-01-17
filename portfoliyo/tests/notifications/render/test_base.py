"""Integration tests for email-sending."""
from datetime import datetime, timedelta

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import html
from django.utils import timezone
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


    def test_footer(self, recip):
        """Footer links to profile."""
        rel = factories.RelationshipFactory.create(
            from_profile=recip, to_profile__name='A Student')
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student)

        record.new_teacher(recip, other_rel.elder, rel.student)

        assert base.send(recip.id)
        self.assert_multi_email(
            html_snippets=[
                '<p>--<br />Don\'t want email notifications? '
                '<a href="%(url)s">Edit your profile</a>.</p>'
                ],
            text_snippets=[
                "--\nDon't want email notifications? Edit your profile: %(url)s"
                ],
            snippet_context={'url': base_url + reverse('edit_profile')},
            )


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


    @pytest.mark.parametrize('params', [
            {
                'scenario': [("StudentX", "ParentX", "Dad", None),],
                'subject': "StudentX's Dad (ParentX) just signed up.",
                'html': [
                    '<li>ParentX signed up as '
                    '<a href="%(StudentXUrl)s">StudentX</a>\'s Dad.</li>'
                    ],
                'text': [
                    "- ParentX signed up as StudentX's Dad. "
                    "Start a conversation: %(StudentXUrl)s"
                    ],
                },
            {
                'scenario': [
                    ("StudentX", "ParentX", "Dad", None),
                    ("StudentY", "ParentY", "Mom", "Math"),
                    ],
                'subject': "You have two new signups.",
                'html': [
                    '<ul class="requested">'
                    '<li>ParentX signed up as '
                    '<a href="%(StudentXUrl)s">StudentX</a>\'s Dad.</li>'
                    '<li>ParentY signed up as '
                    '<a href="%(StudentYUrl)s">StudentY</a>\'s Mom '
                    'in the <a href="%(MathUrl)s">Math</a> group.</li>'
                    '</ul>'
                    ],
                'text': [
                    "- ParentX signed up as StudentX's Dad. "
                    "Start a conversation: %(StudentXUrl)s\n"
                    "- ParentY signed up as StudentY's Mom in the Math group. "
                    "Start a conversation: %(StudentYUrl)s"
                    ],
                },
            ])
    def test_new_parents(self, params, recip):
        context = {}
        for student_name, parent_name, role, group_name in params['scenario']:
            ts = factories.TextSignupFactory.create(
                teacher=recip, family__name=parent_name, family__role=role)

            ts.student = factories.RelationshipFactory.create(
                from_profile=ts.family, to_profile__name=student_name).student

            if group_name is not None:
                ts.group = factories.GroupFactory.create(name=group_name)
                context['%sUrl' % group_name] = base_url + reverse(
                    'group', kwargs={'group_id': ts.group_id})

            ts.save()

            context['%sUrl' % student_name] = base_url + reverse(
                'village', kwargs={'student_id': ts.student_id})

            record.new_parent(recip, ts)

        assert base.send(recip.id)
        self.assert_multi_email(
            params['subject'], params['html'], params['text'], context)


    @pytest.mark.parametrize('params', [
            { # simple case with a single post
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(), True),
                    ],
                'subject': "New message in StX's village.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX\'s village</a>:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Dad:</b>'
                    '<span class="fn">PaX</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX\'s village:\n'
                    '  "hello" - PaX (Dad), 1/14/2013 at 7 p.m.\n'
                    'Log in to reply: %(StXUrl)s'
                    ],
                },
            { # two new posts in a village
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(hours=1), True),
                    ('StX', 'PaX', 'Dad', 'again', timedelta(), True),
                    ],
                'subject': "New messages in StX's village.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX\'s village</a>:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Dad:</b>'
                    '<span class="fn">PaX</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T18:00:00-05:00">'
                    '1/14/2013 at 6 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Dad:</b>'
                    '<span class="fn">PaX</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: again</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX\'s village:\n'
                    '  "hello" - PaX (Dad), 1/14/2013 at 6 p.m.\n'
                    '  "again" - PaX (Dad), 1/14/2013 at 7 p.m.\n'
                    'Log in to reply: %(StXUrl)s'
                    ],
                },
            { # one new post and one context post; note "new" class gone
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(hours=1), False),
                    ('StX', 'PaX', 'Dad', 'again', timedelta(), True),
                    ],
                'subject': "New message in StX's village.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX\'s village</a>:</h2>',
                    '<article class="post">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Dad:</b>'
                    '<span class="fn">PaX</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T18:00:00-05:00">'
                    '1/14/2013 at 6 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Dad:</b>'
                    '<span class="fn">PaX</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: again</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX\'s village:\n'
                    '  "hello" - PaX (Dad), 1/14/2013 at 6 p.m.\n'
                    '  "again" - PaX (Dad), 1/14/2013 at 7 p.m.\n'
                    'Log in to reply: %(StXUrl)s'
                    ],
                },
            { # new posts in two different villages
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(hours=1), True),
                    ('StY', 'PaY', 'Mom', 'hey', timedelta(), True),
                    ],
                'subject': "New messages in two of your villages.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX\'s village</a>:</h2>',
                    '<h2>In <a href="%(StYUrl)s">StY\'s village</a>:</h2>',
                    ],
                'text': [
                    'In StX\'s village:\n',
                    'Log in to reply: %(StXUrl)s',
                    'In StY\'s village:\n',
                    'Log in to reply: %(StYUrl)s',
                    ],
                },
            { # non-requested post by single author
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(hours=1), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New message in StX's village.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from PaX.</li>'
                    ],
                'text': [
                    '- StX\'s village has new messages from PaX.'
                    ],
                },
            { # non-requested posts by two authors
                'scenario': [
                    ('StX', 'Pa1', 'Dad', 'hello', timedelta(hours=1), True),
                    ('StX', 'Pa2', 'Mom', 'hey', timedelta(), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New messages in StX's village.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from Pa1 and Pa2.</li>'
                    ],
                'text': [
                    '- StX\'s village has new messages from Pa1 and Pa2.'
                    ],
                },
            { # non-requested posts by three authors
                'scenario': [
                    ('StX', 'Pa1', 'Dad', 'hello', timedelta(hours=2), True),
                    ('StX', 'Pa2', 'Mom', 'hey', timedelta(hours=1), True),
                    ('StX', 'Pa3', 'Sis', 'yo', timedelta(), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New messages in StX's village.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from Pa1, Pa2 and Pa3.</li>'
                    ],
                'text': [
                    '- StX\'s village has new messages from Pa1, Pa2 and Pa3.'
                    ],
                },
            { # non-requested posts by four authors
                'scenario': [
                    ('StX', 'Pa1', 'Dad', 'hello', timedelta(hours=3), True),
                    ('StX', 'Pa2', 'Mom', 'hey', timedelta(hours=2), True),
                    ('StX', 'Pa3', 'Sis', 'yo', timedelta(hours=1), True),
                    ('StX', 'Pa4', 'Bro', 'sup', timedelta(), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New messages in StX's village.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from Pa1, Pa2, Pa3, and one more person.</li>'
                    ],
                'text': [
                    "- StX's village has new messages from Pa1, Pa2, Pa3, "
                    "and one more person."
                    ],
                },
            { # non-requested posts by five authors
                'scenario': [
                    ('StX', 'Pa1', 'Dad', 'hello', timedelta(hours=4), True),
                    ('StX', 'Pa2', 'Mom', 'hey', timedelta(hours=3), True),
                    ('StX', 'Pa3', 'Sis', 'yo', timedelta(hours=2), True),
                    ('StX', 'Pa4', 'Bro', 'sup', timedelta(hours=1), True),
                    ('StX', 'Pa5', 'Toad', 'burp', timedelta(), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New messages in StX's village.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from Pa1, Pa2, Pa3, and two more people.</li>'
                    ],
                'text': [
                    "- StX's village has new messages from Pa1, Pa2, Pa3, "
                    "and two more people."
                    ],
                },
            { # non-requested posts in two villages
                'scenario': [
                    ('StX', 'PaX', 'Dad', 'hello', timedelta(hours=1), True),
                    ('StY', 'PaY', 'Mom', 'hey', timedelta(hours=1), True),
                    ],
                'prefs': {'notify_parent_text': False},
                'subject': "New messages in two of your villages.",
                'html': [
                    '<li><a href="%(StXUrl)s">StX\'s village</a> has new '
                    'messages from PaX.</li>',
                    '<li><a href="%(StYUrl)s">StY\'s village</a> has new '
                    'messages from PaY.</li>',
                    ],
                'text': [
                    "- StX's village has new messages from PaX.\n"
                    "- StY's village has new messages from PaY."
                    ],
                },
            ])
    def test_posts(self, params, recip):
        context = {}
        name_map = {}
        rels = set()
        now = datetime(2013, 1, 15, tzinfo=timezone.utc)
        for st_name, author_name, role, text, ago, new in params['scenario']:
            if st_name not in name_map:
                name_map[st_name] = factories.RelationshipFactory.create(
                    from_profile=recip, to_profile__name=st_name).student
                context['%sUrl' % st_name] = base_url + reverse(
                    'village', kwargs={'student_id': name_map[st_name].id})
            if author_name not in name_map:
                name_map[author_name] = factories.ProfileFactory.create(
                    name=author_name, school_staff=False)
            student = name_map[st_name]
            author = name_map[author_name]
            if (student, author) not in rels:
                factories.RelationshipFactory.create(
                    from_profile=author, to_profile=student, description=role)
                rels.add((student, author))
            post = factories.PostFactory.create(
                author=author,
                student=student,
                original_text=text,
                html_text='html: %s' % text,
                timestamp=now - ago,
                )
            if new:
                record.post(recip, post)

        assert base.send(recip.id)
        self.assert_multi_email(
            params['subject'], params['html'], params['text'], context)


    @pytest.mark.parametrize('params', [
            { # one bulk post by one teacher, seen in one of my villages
              # (this is treated exactly like a non-bulk post)
                'scenario': [
                    ("Teacher1", ["StX"], ["StY"], "hello", timedelta())
                    ],
                'subject': "New message in StX's village.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX\'s village</a>:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teacher1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX\'s village:\n'
                    '  "hello" - Teacher1 (Teacher), 1/14/2013 at 7 p.m.\n'
                    'Log in to reply: %(StXUrl)s'
                    ],
                },
            { # one bulk post by one teacher, seen in two of my villages
                'scenario': [
                    ("Teacher1", ["StX", "StY"], [], "hello", timedelta())
                    ],
                'subject': "Teacher1 sent a message in two of your villages.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teacher1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX and StY\'s villages:\n'
                    '  "hello" - Teacher1 (Teacher), 1/14/2013 at 7 p.m.\n'
                    ],
                },
            { # two bulk posts by same teacher, seen in two of my villages
                'scenario': [
                    ("Teach1", ["StX", "StY"], [], "hello", timedelta(hours=1)),
                    ("Teach1", ["StX", "StY"], [], "again", timedelta()),
                    ],
                'subject': "Teach1 sent two messages in two of your villages.",
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T18:00:00-05:00">'
                    '1/14/2013 at 6 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: again</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX and StY\'s villages:\n'
                    '  "hello" - Teach1 (Teacher), 1/14/2013 at 6 p.m.\n'
                    '  "again" - Teach1 (Teacher), 1/14/2013 at 7 p.m.\n'
                    ],
                },
            { # bulk posts by two teachers in the same two villages
                'scenario': [
                    ("Teach1", ["StX", "StY"], [], "hello", timedelta(hours=1)),
                    ("Teach2", ["StX", "StY"], [], "hi", timedelta()),
                    ],
                'subject': (
                    "Two teachers sent two messages in "
                    "two of your villages."
                    ),
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T18:00:00-05:00">'
                    '1/14/2013 at 6 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach2</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hi</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX and StY\'s villages:\n'
                    '  "hello" - Teach1 (Teacher), 1/14/2013 at 6 p.m.\n'
                    '  "hi" - Teach2 (Teacher), 1/14/2013 at 7 p.m.\n'
                    ],
                },
            { # bulk posts by two teachers in different sets of villages
                'scenario': [
                    ("Teach1", ["StX", "StY"], [], "hello", timedelta(hours=1)),
                    ("Teach2", ["StX", "StZ"], [], "hi", timedelta()),
                    ],
                'subject': (
                    "Two teachers sent two messages in "
                    "three of your villages."
                    ),
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach1</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T18:00:00-05:00">'
                    '1/14/2013 at 6 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hello</p>'
                    '</article>',
                    '<h2>In <a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StZUrl)s">StZ</a>\'s villages:</h2>',
                    '<article class="post new">'
                    '<header class="post-meta">'
                    '<h3 class="byline vcard">'
                    '<b class="title">Teacher:</b>'
                    '<span class="fn">Teach2</span>'
                    '</h3>'
                    '<time class="pubdate" datetime="2013-01-14T19:00:00-05:00">'
                    '1/14/2013 at 7 p.m.</time>'
                    '</header>'
                    '<p class="post-text">html: hi</p>'
                    '</article>'
                    ],
                'text': [
                    'In StX and StY\'s villages:\n'
                    '  "hello" - Teach1 (Teacher), 1/14/2013 at 6 p.m.\n',
                    'In StX and StZ\'s villages:\n'
                    '  "hi" - Teach2 (Teacher), 1/14/2013 at 7 p.m.\n'
                    ],
                },
            { # a bulk post in three villages
                'scenario': [
                    (
                        "Teach1",
                        ["StX", "StY", "StZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'subject': (
                    "Teach1 sent a message in three of your villages."
                    ),
                'html': [
                    '<h2>In <a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a> and '
                    '<a href="%(StZUrl)s">StZ</a>\'s villages:</h2>',
                    ],
                'text': [
                    'In StX, StY and StZ\'s villages:\n'
                    ],
                },
            { # a bulk post in four villages
                'scenario': [
                    (
                        "Teach1",
                        ["StW", "StX", "StY", "StZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'subject': (
                    "Teach1 sent a message in four of your villages."
                    ),
                'html': [
                    '<h2>In <a href="%(StWUrl)s">StW</a>, '
                    '<a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a>, '
                    'and one more village:</h2>',
                    ],
                'text': [
                    'In StW, StX, StY, and one more village:\n'
                    ],
                },
            { # a bulk post in five villages
                'scenario': [
                    (
                        "Teach1",
                        ["StW", "StX", "StY", "StZ", "StZZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'subject': (
                    "Teach1 sent a message in five of your villages."
                    ),
                'html': [
                    '<h2>In <a href="%(StWUrl)s">StW</a>, '
                    '<a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a>, '
                    'and two more villages:</h2>',
                    ],
                'text': [
                    'In StW, StX, StY, and two more villages:\n'
                    ],
                },
            { # nonrequested bulk posts by two teachers
                'scenario': [
                    ("Teach1", ["StX", "StY"], [], "hello", timedelta(hours=1)),
                    ("Teach2", ["StX", "StY"], [], "hi", timedelta()),
                    ],
                'prefs': {'notify_teacher_post': False},
                'subject': (
                    "Two teachers sent two messages in "
                    "two of your villages."
                    ),
                'html': [
                    '<li><a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages '
                    'have two messages from '
                    'Teach1 and Teach2.</li>',
                    ],
                'text': [
                    '- StX and StY\'s villages have two messages '
                    'from Teach1 and Teach2.'
                    ],
                },
            { # nonrequested bulk posts by three teachers
                'scenario': [
                    ("Teach1", ["StX", "StY"], [], "hello", timedelta(hours=2)),
                    ("Teach2", ["StX", "StY"], [], "hi", timedelta(hours=1)),
                    ("Teach3", ["StX", "StY"], [], "sup", timedelta()),
                    ],
                'prefs': {'notify_teacher_post': False},
                'subject': (
                    "Three teachers sent three messages in "
                    "two of your villages."
                    ),
                'html': [
                    '<li><a href="%(StXUrl)s">StX</a> and '
                    '<a href="%(StYUrl)s">StY</a>\'s villages '
                    'have three messages from three teachers.</li>',
                    ],
                'text': [
                    '- StX and StY\'s villages have three messages '
                    'from three teachers.'
                    ],
                },
            { # a nonrequested bulk post in three villages
                'scenario': [
                    (
                        "Teach1",
                        ["StX", "StY", "StZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'prefs': {'notify_teacher_post': False},
                'subject': (
                    "Teach1 sent a message in three of your villages."
                    ),
                'html': [
                    '<li><a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a> and '
                    '<a href="%(StZUrl)s">StZ</a>\'s villages '
                    'have a message from Teach1.</li>'
                    ],
                'text': [
                    'StX, StY, and StZ\'s villages have a message from Teach1.'
                    ],
                },
            { # a nonrequested bulk post in four villages
                'scenario': [
                    (
                        "Teach1",
                        ["StW", "StX", "StY", "StZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'prefs': {'notify_teacher_post': False},
                'subject': (
                    "Teach1 sent a message in four of your villages."
                    ),
                'html': [
                    '<li><a href="%(StWUrl)s">StW</a>, '
                    '<a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a>, '
                    'and one more village '
                    'have a message from Teach1.</li>'
                    ],
                'text': [
                    'StW, StX, StY, and one more village '
                    'have a message from Teach1.'
                    ],
                },
            { # a nonrequested bulk post in five villages
                'scenario': [
                    (
                        "Teach1",
                        ["StW", "StX", "StY", "StZ", "StZZ"],
                        [],
                        "hello",
                        timedelta(hours=1)),
                    ],
                'prefs': {'notify_teacher_post': False},
                'subject': (
                    "Teach1 sent a message in five of your villages."
                    ),
                'html': [
                    '<li><a href="%(StWUrl)s">StW</a>, '
                    '<a href="%(StXUrl)s">StX</a>, '
                    '<a href="%(StYUrl)s">StY</a>, '
                    'and two more villages '
                    'have a message from Teach1.</li>'
                    ],
                'text': [
                    'StW, StX, StY, and two more villages '
                    'have a message from Teach1.'
                    ],
                },
            ])
    def test_bulk_posts(self, params, recip):
        context = {}
        name_map = {}
        now = datetime(2013, 1, 15, tzinfo=timezone.utc)
        for teacher_name, my_sts, other_sts, msg, ago in params['scenario']:
            if teacher_name not in name_map:
                name_map[teacher_name] = factories.ProfileFactory.create(
                    school_staff=True, name=teacher_name, role="Teacher")
            teacher = name_map[teacher_name]
            all_students = []
            for st_name in my_sts:
                if st_name not in name_map:
                    name_map[st_name] = factories.RelationshipFactory.create(
                        to_profile__name=st_name, from_profile=recip).student
                all_students.append(name_map[st_name])
            for st_name in other_sts:
                if st_name not in name_map:
                    name_map[st_name] = factories.ProfileFactory.create(
                        name=st_name)
                all_students.append(name_map[st_name])
            group = factories.GroupFactory.create(owner=teacher)
            group.students.add(*all_students)
            html_text = "html: %s" % msg
            timestamp = now - ago
            bulk_post = factories.BulkPostFactory.create(
                author=teacher,
                group=group,
                original_text=msg,
                html_text=html_text,
                timestamp=timestamp,
                )
            for student in all_students:
                context['%sUrl' % student.name] = base_url + reverse(
                    'village', kwargs={'student_id': student.id})
                factories.PostFactory.create(
                    author=teacher,
                    student=student,
                    from_bulk=bulk_post,
                    original_text=msg,
                    html_text=html_text,
                    timestamp=timestamp,
                    )
            record.bulk_post(recip, bulk_post)

        assert base.send(recip.id)
        self.assert_multi_email(
            params['subject'], params['html'], params['text'], context)
