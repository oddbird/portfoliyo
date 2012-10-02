"""Tests for village models and related functions."""
import datetime
from django.utils.timezone import utc
import mock
import pytest
import re


from portfoliyo.model.village import models

from portfoliyo.tests import factories




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



def test_post_dict():
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
        'meta': {},
        }



def test_post_dict_no_author():
    """Special handling for author-less (automated) posts."""
    student = factories.ProfileFactory.create()
    post = factories.PostFactory.create(author=None, student=student)

    d = models.post_dict(post)

    assert d['author_id'] == 0
    assert d['author'] == ""
    assert d['role'] == "Portfoliyo"



def test_post_dict_no_relationship():
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



class TestPostCreate(object):
    @mock.patch('portfoliyo.model.village.models.timezone.now')
    def test_creates_post(self, mock_now):
        """Actually creates and returns a Post object."""
        mock_now.return_value = datetime.datetime(
            2012, 9, 17, 6, 25, tzinfo=utc)
        rel = factories.RelationshipFactory.create()

        post = models.Post.create(rel.elder, rel.student, 'Foo\n')

        assert post.author == rel.elder
        assert post.student == rel.student
        assert post.timestamp == mock_now.return_value
        assert post.original_text == 'Foo\n'
        assert post.html_text == 'Foo<br>'
        assert post.from_sms == False
        assert post.to_sms == False
        assert post.meta == {'highlights': []}


    def test_creates_post_from_sms(self):
        """Post object can have from_sms set to True."""
        rel = factories.RelationshipFactory.create()

        post = models.Post.create(
            rel.elder, rel.student, 'Foo\n', from_sms=True)

        assert post.from_sms == True
        assert post.to_sms == False


    @mock.patch('portfoliyo.model.village.models.get_pusher')
    def test_triggers_pusher_event(self, mock_get_pusher):
        """Triggers a pusher event if get_pusher doesn't return None."""
        rel = factories.RelationshipFactory.create()

        models.Post.create(rel.elder, rel.student, 'Foo\n', '33')

        channel = mock_get_pusher.return_value['student_%s' % rel.student.id]
        args = channel.trigger.call_args[0]
        post_data = args[1]['posts'][0]

        assert args[0] == 'message_posted'
        assert post_data['author_sequence_id'] == '33'
        assert post_data['author_id'] == rel.elder.id
        assert post_data['student_id'] == rel.student.id


    @mock.patch('portfoliyo.model.village.models.sms.send')
    def test_notifies_highlighted_mobile_users(self, mock_send_sms):
        """Sends text to highlighted active mobile users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            description="Father",
            )

        post = models.Post.create(rel1.elder, rel1.student, 'Hey @father')

        mock_send_sms.assert_called_with(
            "+13216540987", "Hey @father --John Doe")
        assert post.to_sms == True
        assert post.meta['highlights'] == [
            {
                'id': rel2.elder.id,
                'mentioned_as': ['father'],
                'role': 'Father',
                'name': '',
                'phone': "+13216540987",
                'email': None,
                'is_active': True,
                'declined': False,
                'sms_sent': True,
                }
            ]


    @mock.patch('portfoliyo.model.village.models.sms.send')
    def test_only_notifies_active_mobile_users(self, mock_send_sms):
        """Sends text only to active users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__phone=None,
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=False,
            description="Father",
            )

        post = models.Post.create(rel1.elder, rel1.student, 'Hey @father')

        assert mock_send_sms.call_count == 0
        assert post.to_sms == False
        assert post.meta['highlights'][0]['sms_sent'] == False


    @mock.patch('portfoliyo.model.village.models.sms.send')
    def test_only_notifies_mobile_users(self, mock_send_sms):
        """Sends text only to users with phone numbers."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__phone=None)
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone=None,
            from_profile__user__is_active=True,
            description="Father",
            )

        post = models.Post.create(rel1.elder, rel1.student, 'Hey @father')

        assert mock_send_sms.call_count == 0
        assert post.to_sms == False
        assert post.meta['highlights'][0]['sms_sent'] == False


    @mock.patch('portfoliyo.model.village.models.sms.send')
    def test_elides_initial_mention(self, mock_send_sms):
        """Initial mention of user elided in text notification to that user."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            description="Father",
            )

        post = models.Post.create(
            rel1.elder, rel1.student, '@father are you there?')

        mock_send_sms.assert_called_with(
            "+13216540987", "are you there? --John Doe")
        assert post.to_sms == True
        assert post.meta['highlights'] == [
            {
                'id': rel2.elder.id,
                'mentioned_as': ['father'],
                'role': 'Father',
                'name': '',
                'phone': "+13216540987",
                'email': None,
                'is_active': True,
                'declined': False,
                'sms_sent': True,
                }
            ]


    @mock.patch('portfoliyo.model.village.models.sms.send')
    def test_can_create_autoreply_post(self, mock_send_sms):
        """Auto-reply prepends phone mention, sends no text to that phone."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__user__is_active=True,
            description="Father",
            )

        post = models.Post.create(
            rel1.elder, rel1.student, 'Thank you!', in_reply_to="+13216540987")

        assert mock_send_sms.call_count == 0
        assert post.original_text == "@+13216540987 Thank you!"
        # With in_reply_to we assume that an SMS was sent by the caller
        assert post.meta['highlights'][0]['id'] == rel2.elder.id
        assert post.meta['highlights'][0]['sms_sent'] == True
        assert post.to_sms == True


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


    def test_full(self):
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
            "<b>Hi</b> there @johndoe, @father\nHow's it?", rel1.to_profile)

        assert html == (
            '&lt;b&gt;Hi&lt;/b&gt; there '
            '<b class="nametag" data-user-id="%s">@johndoe</b>, '
            '<b class="nametag" data-user-id="%s">@father</b><br>'
            "How&#39;s it?" % (rel1.elder.id, rel2.elder.id)
            )

        assert highlights == {rel1: ['johndoe'], rel2: ['father']}



class TestReplaceHighlights(object):
    class MockRel(object):
        """A mock Relationship."""
        def __init__(self, elder_id):
            self.elder = mock.Mock()
            self.elder.id = elder_id


    rel1 = MockRel(1)
    rel2 = MockRel(2)
    rel3 = MockRel(3)
    name_map = {
        'one': set([rel1]),
        'two': set([rel2]),
        'foo@example.com': set([rel3]),
        'all': set([rel1, rel2]),
        }


    def call(self, text):
        """Shortcut to call replace_highlights with self.name_map."""
        return models.replace_highlights(text, self.name_map)


    def test_wrap(self):
        """Wraps highlights with b.nametag and returns in set."""
        html, highlights = self.call("Hello @one")

        assert html == 'Hello <b class="nametag" data-user-id="1">@one</b>'
        assert highlights == {self.rel1: ["one"]}


    def test_all(self):
        """Can highlight all users with @all."""
        html, highlights = self.call("Hello @all")

        assert re.match(
            'Hello <b class="nametag all me" data-user-id="(1,2|2,1)">@all</b>',
            html)
        assert highlights == {self.rel1: ["all"], self.rel2: ["all"]}


    def test_email(self):
        """Can highlight a user by email address."""
        _, highlights = self.call("Hello @foo@example.com")

        assert highlights == {self.rel3: ["foo@example.com"]}


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

        assert self.rel1 in highlights


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




def test_get_highlight_names():
    """Returns dict mapping highlightable names to relationship."""
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

    name_map = models.get_highlight_names(rel1.to_profile)

    assert len(name_map) == 10
    assert name_map['johndoe'] == set([rel1])
    assert name_map['john@example.com'] == set([rel1])
    assert name_map['mathteacher'] == set([rel1])
    assert name_map['maxdad'] == set([rel2])
    assert name_map['+13216540987'] == set([rel2])
    assert name_map['3216540987'] == set([rel2])
    assert name_map['father'] == set([rel2, rel3])
    assert name_map['+15671234567'] == set([rel3])
    assert name_map['5671234567'] == set([rel3])
    assert name_map['all'] == set([rel1, rel2, rel3])



def test_text_notification_suffix_elder_has_name():
    """Text notification suffix is elder name preceded by ' --'."""
    rel = mock.Mock()
    rel.elder.name = "Foo"
    assert models.text_notification_suffix(rel) == " --Foo"



def test_text_notification_suffix_no_name():
    """If elder has no name, text suffix uses relationship role."""
    rel = mock.Mock()
    rel.elder.name = ""
    rel.description_or_role = "Math Teacher"
    assert models.text_notification_suffix(rel) == " --Math Teacher"



@mock.patch('portfoliyo.model.village.models.text_notification_suffix')
def test_post_char_limit(mock_text_notification_suffix):
    """Char limit for a post is 160 - length of suffix."""
    mock_text_notification_suffix.return_value = "a" * 10
    rel = mock.Mock()

    assert models.post_char_limit(rel) == 150


def test_strip_initial_mention_case():
    """strip_initial_mention is case-insensitive."""
    assert models.strip_initial_mention('@Father foo', ['father']) == 'foo'


def test_strip_initial_mention_only_initial():
    """strip_initial_mention only strips initial mentions."""
    assert models.strip_initial_mention('hi @dad', ['dad']) == 'hi @dad'


def test_strip_initial_mention_only_given():
    """strip_initial_mention only strips given names."""
    assert models.strip_initial_mention('@dad hey', ['mom']) == '@dad hey'
