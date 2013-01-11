"""Tests for village models and related functions."""
import datetime

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
import mock
import pytest
import re


from portfoliyo.model.users.models import contextualized_elders
from portfoliyo.model.village import models, unread

from portfoliyo.tests import factories, utils




def test_unicode():
    """Unicode representation of Post is its original text."""
    p = factories.PostFactory.build(original_text='foo')

    assert unicode(p) == u'foo'


def test_sms():
    """sms property is true if either from_sms or to_sms or both."""
    assert not factories.PostFactory.build(from_sms=False, to_sms=False).sms
    assert factories.PostFactory.build(from_sms=True, to_sms=False).sms
    assert factories.PostFactory.build(from_sms=False, to_sms=True).sms
    assert factories.PostFactory.build(from_sms=True, to_sms=True).sms



def test_post_dict(db):
    """post_dict returns dictionary of post data."""
    rel = factories.RelationshipFactory.create(
        from_profile__name='The Teacher', description='desc')
    post = factories.PostFactory.create(
        author=rel.elder,
        student=rel.student,
        timestamp=datetime.datetime(2012, 9, 17, 5, 30, tzinfo=utc),
        html_text='Foo',
        )

    assert models.post_dict(post, extra="extra") == {
        'post_id': post.id,
        'author_id': rel.elder.id,
        'student_id': rel.student.id,
        'author': 'The Teacher',
        'role': u'desc',
        'timestamp': '2012-09-17T01:30:00-04:00',
        'date': u'9/17/2012',
        'time': u'1:30 a.m.',
        'text': 'Foo',
        'extra': 'extra',
        'sms': False,
        'to_sms': False,
        'from_sms': False,
        'meta': {'sms': []},
        }



def test_post_dict_no_author():
    """Special handling for author-less (automated) posts."""
    student = factories.ProfileFactory.build()
    post = factories.PostFactory.build(author=None, student=student)

    d = models.post_dict(post)

    assert d['author_id'] == 0
    assert d['author'] == ""
    assert d['role'] == "Portfoliyo"



def test_post_dict_no_relationship(db):
    """If relationship is gone, uses author's role instead."""
    rel = factories.RelationshipFactory.create(
        from_profile__name='The Teacher',
        from_profile__role='role',
        description='desc',
        )
    post = factories.PostFactory.create(
        author=rel.elder,
        student=rel.student,
        )
    rel.delete()

    assert models.post_dict(post)['role'] == 'role'



def test_get_absolute_url(db):
    """A Post's absolute-url is its village URL. (For admin view-on-site.)"""
    post = factories.PostFactory.create()

    assert post.get_absolute_url() == reverse(
        'village', kwargs={'student_id': post.student_id})




class TestPostCreate(object):
    def test_creates_post(self, db):
        """Actually creates and returns a Post object."""
        rel = factories.RelationshipFactory.create()

        target = 'portfoliyo.model.village.models.timezone.now'
        with mock.patch(target) as mock_now:
            mock_now.return_value = datetime.datetime(
                2012, 9, 17, 6, 25, tzinfo=utc)
            post = models.Post.create(rel.elder, rel.student, 'Foo\n')

        assert post.author == rel.elder
        assert post.student == rel.student
        assert post.timestamp == mock_now.return_value
        assert post.original_text == 'Foo\n'
        assert post.html_text == 'Foo<br>'
        assert post.from_sms == False
        assert post.to_sms == False
        assert post.meta == {'sms': [], 'highlights': []}


    def test_highlights(self, db):
        """Highlight info is stored in meta['highlights']."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            description="Father",
            from_profile__name="John Doe",
            from_profile__user__email="john@example.com",
            to_profile=rel.student,
            )

        post = models.Post.create(rel.elder, rel.student, 'Hello @father')

        assert post.meta['highlights'] == [
            {
                'id': rel2.elder.id,
                'mentioned_as': ['father'],
                'role': "Father",
                'name': "John Doe",
                'email': "john@example.com",
                'phone': None,
                },
            ]


    def test_new_post_unread_for_all_web_users_in_village(self, db):
        """New post is marked unread for all non-author web users in village."""
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='foo@example.com')
        rel2 = factories.RelationshipFactory.create(
            from_profile__user__email='bar@example.com', to_profile=rel.student)
        rel3 = factories.RelationshipFactory.create(
            from_profile__user__email=None, to_profile=rel.student)

        post = models.Post.create(rel.elder, rel.student, 'Foo')

        assert not unread.is_unread(post, rel.elder)
        assert unread.is_unread(post, rel2.elder)
        # web users only
        assert not unread.is_unread(post, rel3.elder)


    def test_creates_post_from_sms(self, db):
        """Post object can have from_sms set to True."""
        rel = factories.RelationshipFactory.create()

        post = models.Post.create(
            rel.elder, rel.student, 'Foo\n', from_sms=True)

        assert post.from_sms == True
        assert post.to_sms == False


    def test_sms_sends_email_notification(self, db):
        """SMS post sends email notifications to those who want them."""
        # Will author the post (and has no email), thus no notification
        rel = factories.RelationshipFactory.create(
            from_profile__phone='+13216540987',
            from_profile__notify_parent_text=True,
            )
        # Will get an email notification
        rel2 = factories.RelationshipFactory.create(
            from_profile__user__email='two@example.com',
            from_profile__notify_parent_text=True,
            to_profile=rel.student,
            )
        # Not related to student - no notification
        factories.RelationshipFactory.create(
            from_profile__user__email='three@example.com',
            from_profile__notify_parent_text=True,
            )
        # Doesn't want email notifications
        factories.RelationshipFactory.create(
            from_profile__user__email='four@example.com',
            from_profile__notify_parent_text=False,
            to_profile=rel.student,
            )
        # Has no email - no notification
        factories.RelationshipFactory.create(
            from_profile__user__email=None,
            from_profile__notify_parent_text=True,
            to_profile=rel.student,
            )

        models.Post.create(rel.elder, rel.student, 'Foo', from_sms=True)

        assert [m.to for m in mail.outbox] == [[rel2.elder.user.email]]


    def test_web_post_sends_email_notification(self, db):
        """Web post sends email notifications to those who want them."""
        # Will author the post, thus no email notification
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='one@example.com',
            from_profile__notify_teacher_post=True,
            )
        # Will get an email notification
        rel2 = factories.RelationshipFactory.create(
            from_profile__user__email='two@example.com',
            from_profile__notify_teacher_post=True,
            to_profile=rel.student,
            )
        # Not related to student - no notification
        factories.RelationshipFactory.create(
            from_profile__user__email='three@example.com',
            from_profile__notify_teacher_post=True,
            )
        # Doesn't want email notifications
        factories.RelationshipFactory.create(
            from_profile__user__email='four@example.com',
            from_profile__notify_teacher_post=False,
            to_profile=rel.student,
            )
        # Inactive - no notifications
        factories.RelationshipFactory.create(
            from_profile__user__email='five@example.com',
            from_profile__user__is_active=False,
            from_profile__notify_teacher_post=True,
            to_profile=rel.student,
            )
        # Has no email - no notification
        factories.RelationshipFactory.create(
            from_profile__user__email=None,
            from_profile__notify_teacher_post=True,
            to_profile=rel.student,
            )

        models.Post.create(rel.elder, rel.student, 'Foo')

        assert [m.to for m in mail.outbox] == [[rel2.elder.user.email]]


    def test_no_email_notification_for_system_posts(self, db):
        """No email notifications for system-generated posts."""
        # Would otherwise get an email notification
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='one@example.com',
            from_profile__notify_parent_text=True,
            from_profile__notify_teacher_post=True,
            )

        models.Post.create(None, rel.student, 'Foo')

        assert len(mail.outbox) == 0


    def test_create_post_without_email_notification(self, db):
        """Can pass a flag to avoid email notifications."""
        # Would otherwise get an email notification
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='one@example.com',
            from_profile__notify_parent_text=True,
            from_profile__notify_teacher_post=True,
            )
        author_rel = factories.RelationshipFactory.create(
            to_profile=rel.student)

        models.Post.create(
            author_rel.elder, rel.student, 'Foo', email_notifications=False)

        assert len(mail.outbox) == 0


    def test_triggers_pusher_event(self, db):
        """Triggers a pusher event."""
        rel = factories.RelationshipFactory.create()

        target = 'portfoliyo.pusher.events.trigger'
        with mock.patch(target) as mock_trigger:
            post = models.Post.create(
                rel.elder, rel.student, 'Foo\n', sequence_id='33')

        args = mock_trigger.call_args[0]
        post_data = args[2]['posts'][0]

        assert args[0] == 'student_%s' % rel.student.id
        assert args[1] == 'message_posted'
        assert post_data['author_sequence_id'] == '33'
        assert post_data['author_id'] == rel.elder.id
        assert post_data['student_id'] == rel.student.id
        assert post_data['mark_read_url'] == reverse(
            'mark_post_read', kwargs={'post_id': post.id})


    def test_notifies_selected_mobile_users(self, db):
        """Sends text to selected active mobile users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            from_profile__name="Jim Smith",
            description="Father",
            )

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.Post.create(
                rel1.elder,
                rel1.student,
                'Hey dad',
                sms_profile_ids=[rel2.elder.id],
                )

        mock_send_sms.assert_called_with(
            "+13216540987", "Hey dad --John Doe")
        assert post.to_sms == True
        assert post.meta['sms'] == [
            {
                'id': rel2.elder.id,
                'role': "Father",
                'name': "Jim Smith",
                'phone': "+13216540987",
                }
            ]


    def test_sending_sms_flips_to_done(self, db):
        """If a user in signup process gets a text, we flip them to done."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            )
        signup = factories.TextSignupFactory.create(
            teacher=rel1.elder,
            family=rel2.elder,
            student=rel1.student,
            state='kidname',
            )

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            models.Post.create(
                rel1.elder,
                rel1.student,
                'Hey dad',
                sms_profile_ids=[rel2.elder.id],
                )

        mock_send_sms.assert_called_with(
            "+13216540987", "Hey dad --John Doe")
        assert utils.refresh(signup).state == 'done'


    def test_only_notifies_active_mobile_users(self, db):
        """Sends text only to active users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=False,
            )

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.Post.create(
                rel1.elder,
                rel1.student,
                'Hey dad',
                sms_profile_ids=[rel2.elder.id],
                )

        assert mock_send_sms.call_count == 0
        assert post.to_sms == False
        assert post.meta['sms'] == []


    def test_only_notifies_mobile_users(self, db):
        """Sends text only to users with phone numbers."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__phone=None)
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone=None,
            from_profile__user__is_active=True,
            )

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.Post.create(
                rel1.elder,
                rel1.student,
                'Hey dad',
                sms_profile_ids=[rel2.elder.id],
                )

        assert mock_send_sms.call_count == 0
        assert post.to_sms == False
        assert post.meta['sms'] == []


    def test_can_create_autoreply_post(self, db):
        """Auto-reply sends no notification to that phone."""
        rel = factories.RelationshipFactory.create(
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            description="Father",
            )

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.Post.create(
                None,
                rel.student,
                'Thank you!',
                in_reply_to="+13216540987",
                )

        assert mock_send_sms.call_count == 0
        assert post.original_text == "Thank you!"
        # With in_reply_to we assume that an SMS was sent by the caller
        assert post.meta['sms'][0]['id'] == rel.elder.id
        assert post.to_sms == True



class TestBulkPost(object):
    def test_create(self, db):
        """Creates a bulk post and posts in individual villages."""
        rel = factories.RelationshipFactory()
        rel2 = factories.RelationshipFactory(from_profile=rel.elder)
        factories.RelationshipFactory(from_profile=rel.elder)
        g = factories.GroupFactory()
        g.students.add(rel.student, rel2.student)
        post = models.BulkPost.create(rel.elder, g, "Hallo")

        exp = set([
                p.student for p in
                models.Post.objects.filter(from_bulk=post)
                ])
        assert set([rel.student, rel2.student]) == exp


    def test_triggers_pusher_event(self, db):
        """Triggers pusher events for both self and sub-posts."""
        rel = factories.RelationshipFactory.create()

        target = 'portfoliyo.pusher.events.trigger'
        with mock.patch(target) as mock_trigger:
            models.BulkPost.create(rel.elder, None, 'Foo\n', sequence_id='33')

        student_args = mock_trigger.call_args_list[0][0]
        student_post_data = student_args[2]['posts'][0]
        group_args = mock_trigger.call_args_list[1][0]
        group_post_data = group_args[2]['posts'][0]

        assert student_args[0] == 'student_%s' % rel.student.id
        assert group_args[0] == 'group_all%s' % rel.elder.id
        assert student_args[1] == group_args[1] == 'message_posted'
        assert student_post_data['author_sequence_id'] == '33'
        assert student_post_data['author_id'] == rel.elder.id
        assert group_post_data['author_sequence_id'] == '33'
        assert group_post_data['author_id'] == rel.elder.id
        assert student_post_data['student_id'] == rel.student.id
        assert group_post_data['group_id'] == 'all%s' % rel.elder.id


    def test_new_post_unread_for_all_web_users_in_village_but_author(self, db):
        """Sub-post marked unread for all web users in village except author."""
        rel = factories.RelationshipFactory.create(
            from_profile__user__email='foo@example.com')
        rel2 = factories.RelationshipFactory.create(
            from_profile__user__email='bar@example.com', to_profile=rel.student)
        rel3 = factories.RelationshipFactory.create(
            from_profile__user__email=None, to_profile=rel.student)
        group = factories.GroupFactory.create(owner=rel.elder)
        group.students.add(rel.student)

        models.BulkPost.create(rel.elder, group, 'Foo')
        sub = rel.student.posts_in_village.get()

        assert unread.is_unread(sub, rel2.elder)
        # not unread for author
        assert not unread.is_unread(sub, rel.elder)
        # web users only
        assert not unread.is_unread(sub, rel3.elder)


    def test_all_students(self, db):
        """group=None sends to all author's students."""
        rel = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(from_profile=rel.elder)
        rel3 = factories.RelationshipFactory.create(from_profile=rel.elder)
        post = models.BulkPost.create(rel.elder, None, "Hallo")

        exp = set([
                p.student for p in
                models.Post.objects.filter(from_bulk=post)
                ])
        assert set([rel.student, rel2.student, rel3.student]) == exp


    def test_no_author_no_group(self):
        """Either group or author is required."""
        with pytest.raises(ValueError):
            models.BulkPost.create(None, None, '')


    def test_only_one_email_notification(self, db):
        """A bulk post sends only one email notification to a given user."""
        author_rel = factories.RelationshipFactory.create()
        other_rel = factories.RelationshipFactory.create(
            to_profile=author_rel.student,
            from_profile__notify_teacher_post=True,
            from_profile__user__email='foo@example.com',
            )
        author_second = factories.RelationshipFactory.create(
            from_profile=author_rel.elder)
        factories.RelationshipFactory.create(
            from_profile=other_rel.elder,
            to_profile=author_second.student,
            )

        models.BulkPost.create(author_rel.elder, None, "Hello?")

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['foo@example.com']


    def test_notifies_selected_mobile_users(self, db):
        """Sends text to selected active mobile users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            from_profile__role="Father",
            from_profile__name="Jim Smith",
            )
        group = factories.GroupFactory.create()
        group.students.add(rel1.student)

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.BulkPost.create(
                rel1.elder, group, 'Hey dad', sms_profile_ids=[rel2.elder.id])

        mock_send_sms.assert_called_with(
            "+13216540987", "Hey dad --John Doe")
        assert post.to_sms == True
        assert post.meta['sms'] == [
            {
                'id': rel2.elder.id,
                'name': 'Jim Smith',
                'role': 'Father',
                'phone': "+13216540987",
                }
            ]


class TestBasePost(object):
    def test_extra_data(self):
        assert models.BasePost().extra_data() == {}



class TestProcessText(object):
    @mock.patch('portfoliyo.model.village.models.get_highlight_names')
    @mock.patch(
        'portfoliyo.model.village.models.replace_highlights',
        lambda text, student: (text, set()))
    def call_simple(self, text, mock_get_highlight_names):
        """Call process_text mocking out highlight handling."""
        html, _ = models.process_text(text, None)
        return html


    def test_escapes_html(self, monkeypatch):
        """Escapes any HTML in the original text."""
        assert self.call_simple('<b>') == '&lt;b&gt;'


    def test_replaces_newlines(self):
        """Replaces newlines with <br>."""
        assert self.call_simple('foo\nbar') == 'foo<br>bar'


    def test_full(self, db):
        """End-to-end test with highlights, newlines, HTML."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__user__email="john@example.com",
            from_profile__phone=None,
            description="Math Teacher")
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__name="Max Dad",
            from_profile__user__email=None,
            from_profile__phone="+13216540987",
            description="Father")

        html, highlights = models.process_text(
            "<b>Hi</b> there @johndoe, @father\nHow's it?",
            contextualized_elders(rel1.to_profile.elder_relationships))

        assert html == (
            '&lt;b&gt;Hi&lt;/b&gt; there '
            '<b class="nametag" data-user-id="%s">@johndoe</b>, '
            '<b class="nametag" data-user-id="%s">@father</b><br>'
            "How&#39;s it?" % (rel1.elder.id, rel2.elder.id)
            )

        assert highlights == {rel1.elder: ['johndoe'], rel2.elder: ['father']}



class TestReplaceHighlights(object):
    class MockElder(object):
        """A mock elder."""
        def __init__(self, id):
            self.id = id


    elder1 = MockElder(1)
    elder2 = MockElder(2)
    elder3 = MockElder(3)
    name_map = {
        'one': set([elder1]),
        'two': set([elder2]),
        'foo@example.com': set([elder3]),
        'all': set([elder1, elder2]),
        }


    def call(self, text):
        """Shortcut to call replace_highlights with self.name_map."""
        return models.replace_highlights(text, self.name_map)


    def test_wrap(self):
        """Wraps highlights with b.nametag and returns in set."""
        html, highlights = self.call("Hello @one")

        assert html == 'Hello <b class="nametag" data-user-id="1">@one</b>'
        assert highlights == {self.elder1: ["one"]}


    def test_all(self):
        """Can highlight all users with @all."""
        html, highlights = self.call("Hello @all")

        assert re.match(
            'Hello <b class="nametag all me" data-user-id="(1,2|2,1)">@all</b>',
            html)
        assert highlights == {self.elder1: ["all"], self.elder2: ["all"]}


    def test_email(self):
        """Can highlight a user by email address."""
        _, highlights = self.call("Hello @foo@example.com")

        assert highlights == {self.elder3: ["foo@example.com"]}


    def test_false_alarm(self):
        """If it looks like a highlight but isn't in the map, ignore it."""
        html, highlights = self.call("Hello @foo")

        assert html == 'Hello @foo'
        assert not highlights


    def test_no_embedded(self):
        """Highlights have to be delimited by whitespace or punctuation."""
        _, highlights = self.call("example@one.com")

        assert len(highlights) == 0


    def test_multiple_highlights(self):
        """Can find multiple highlights in a text."""
        _, highlights = self.call("Hello @one and @two")

        assert len(highlights) == 2


    def test_multiple_adjacent_highlights(self):
        """Can find multiple adjacent highlights in a text."""
        _, highlights = self.call("Hello @one @two")

        assert len(highlights) == 2


    def test_multiple_highlights_same_name(self):
        """If multiple highlights of same name, no double-replace."""
        html, highlights = self.call("Hello @one and @one")

        assert len(highlights) == 1
        assert html.count('data-user-id') == 2


    def assert_finds(self, text):
        """Assert that 'one' is found as highlight in text."""
        _, highlights = self.call(text)

        assert self.elder1 in highlights


    @pytest.mark.parametrize(
        'symbol', ['.', '?', ',', ';', ':', ')', ']', ' ', '', '...'])
    def test_followed_by(self, symbol):
        """Can detect a highlight immediately followed by some punctuation."""
        self.assert_finds("Hey @one%s" % symbol)


    @pytest.mark.parametrize(
        'symbol', ['(', '[', ' ', ''])
    def test_preceded_by(self, symbol):
        """Can detect a highlight immediately preceded by some punctuation."""
        self.assert_finds("%s@one" % symbol)




def test_get_highlight_names(db):
    """Returns dict mapping highlightable names to elders-in-context."""
    rel1 = factories.RelationshipFactory.create(
        from_profile__name="John Doe",
        from_profile__user__email="john@example.com",
        from_profile__phone=None,
        description="Math Teacher")
    rel2 = factories.RelationshipFactory.create(
        to_profile=rel1.to_profile,
        from_profile__name="Max Dad",
        from_profile__user__email=None,
        from_profile__phone="+13216540987",
        description="Father")
    rel3 = factories.RelationshipFactory.create(
        to_profile=rel1.to_profile,
        from_profile__name="",
        from_profile__user__email=None,
        from_profile__phone="+15671234567",
        description="Father")

    name_map = models.get_highlight_names(
        contextualized_elders(rel1.to_profile.elder_relationships))

    assert len(name_map) == 10
    assert name_map['johndoe'] == set([rel1.elder])
    assert name_map['john@example.com'] == set([rel1.elder])
    assert name_map['mathteacher'] == set([rel1.elder])
    assert name_map['maxdad'] == set([rel2.elder])
    assert name_map['+13216540987'] == set([rel2.elder])
    assert name_map['3216540987'] == set([rel2.elder])
    assert name_map['father'] == set([rel2.elder, rel3.elder])
    assert name_map['+15671234567'] == set([rel3.elder])
    assert name_map['5671234567'] == set([rel3.elder])
    assert name_map['all'] == set([rel1.elder, rel2.elder, rel3.elder])



def test_notification_suffix():
    """Text notification suffix is name_or_role preceded by ' --'."""
    rel = mock.Mock()
    rel.name_or_role = "Foo"
    assert models.notification_suffix(rel) == " --Foo"



@mock.patch('portfoliyo.model.village.models.notification_suffix')
def test_post_char_limit(mock_notification_suffix):
    """Char limit for a post is 160 - length of suffix."""
    mock_notification_suffix.return_value = "a" * 10
    rel = mock.Mock()

    assert models.post_char_limit(rel) == 150
