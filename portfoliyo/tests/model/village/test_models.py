"""Tests for village models and related functions."""
import datetime

from django.core.urlresolvers import reverse
from django.utils.timezone import utc
import mock
import pytest

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
        assert post.relationship == rel
        assert post.timestamp == mock_now.return_value
        assert post.original_text == 'Foo\n'
        assert post.html_text == 'Foo<br>'
        assert post.from_sms == False
        assert post.to_sms == False
        assert post.meta == {'sms': []}
        assert utils.refresh(rel.elder).has_posted


    def test_new_post_unread_for_all_web_users_in_village(self, db, redis):
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


    def test_triggers_pusher_event(self, db):
        """Triggers a pusher event for each teacher."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        target = 'portfoliyo.pusher.events.trigger'
        with mock.patch(target) as mock_trigger:
            post = models.Post.create(
                rel.elder, rel.student, 'Foo\n', sequence_id='33')

        args = mock_trigger.call_args[0]
        post_data = args[2]['objects'][0]

        assert args[0] == 'user_%s' % rel.from_profile_id
        assert args[1] == 'message_posted'
        assert post_data['author_sequence_id'] == '33'
        assert post_data['author_id'] == rel.from_profile_id
        assert post_data['student_id'] == rel.to_profile_id
        assert post_data['mark_read_url'] == reverse(
            'mark_post_read', kwargs={'post_id': post.id})


    def test_texts_selected_mobile_users(self, db):
        """Sends text to selected active mobile users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__source_phone='+13336660000',
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
            "+13216540987", "+13336660000", "Hey dad --John Doe")
        assert post.to_sms == True
        assert post.meta['sms'] == [
            {
                'id': rel2.elder.id,
                'role': "Father",
                'name': "Jim Smith",
                'phone': "+13216540987",
                }
            ]


    def test_no_texts_by_default(self, db):
        """Sends no texts by default."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__source_phone='+13336660000',
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
                )

        assert not mock_send_sms.call_count
        assert post.to_sms == False
        assert post.meta['sms'] == []


    def test_text_all_mobile_users(self, db):
        """Sends text to all active mobile users if 'all' given."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__source_phone='+13336660000',
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
                sms_profile_ids='all',
                )

        mock_send_sms.assert_called_with(
            "+13216540987", "+13336660000", "Hey dad --John Doe")
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
            from_profile__source_phone="+1333666000",
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
            "+13216540987", "+1333666000", "Hey dad --John Doe")
        assert utils.refresh(signup).state == 'done'


    def test_only_texts_active_mobile_users(self, db):
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


    def test_only_texts_mobile_users(self, db):
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
        """Auto-reply sends no SMS to that phone."""
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


    def test_records_notifications(self, db):
        """Records notification for users in village."""
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.student)

        target = 'portfoliyo.notifications.record.post'
        with mock.patch(target) as mock_notify_post:
            post = models.Post.create(rel1.elder, rel1.student, "Hello")

        mock_notify_post.assert_called_with(rel2.elder, post)


    def test_can_prevent_notification(self, db):
        """No notification if pass notifications=False."""
        rel1 = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            to_profile=rel1.student)

        target = 'portfoliyo.notifications.record.post'
        with mock.patch(target) as mock_notify_post:
            models.Post.create(
                rel1.elder, rel1.student, "Hello", notifications=False)

        assert mock_notify_post.call_count == 0


    def test_no_notification_for_system_posts(self, db):
        """No notification for system posts."""
        rel = factories.RelationshipFactory.create()

        target = 'portfoliyo.notifications.record.post'
        with mock.patch(target) as mock_notify_post:
            models.Post.create(None, rel.student, "Hello")

        assert mock_notify_post.call_count == 0


    def test_no_notification_for_author(self, db):
        """No notification recorded for author."""
        rel = factories.RelationshipFactory.create()

        target = 'portfoliyo.notifications.record.post'
        with mock.patch(target) as mock_notify_post:
            models.Post.create(rel.elder, rel.student, "Hello")

        assert mock_notify_post.call_count == 0



class TestBulkPost(object):
    def test_create(self, db):
        """Creates a bulk post and posts in individual villages."""
        rel = factories.RelationshipFactory()
        rel2 = factories.RelationshipFactory(from_profile=rel.elder)
        factories.RelationshipFactory(from_profile=rel.elder)
        g = factories.GroupFactory()
        g.students.add(rel.student, rel2.student)
        post = models.BulkPost.create(rel.elder, g, "Hallo")

        subs = models.Post.objects.filter(from_bulk=post)
        exp = set([p.student for p in subs])
        assert set([rel.student, rel2.student]) == exp
        assert {rel, rel2} == set([p.relationship for p in subs])
        assert utils.refresh(rel.elder).has_posted


    def test_create_no_author(self, db):
        """Can create an authorless (system) bulk post."""
        g = factories.GroupFactory()
        post = models.BulkPost.create(None, g, "Hallo")

        assert post.author is None


    def test_triggers_pusher_event(self, db):
        """Triggers pusher events for both self and sub-posts."""
        rel = factories.RelationshipFactory.create(
            from_profile__school_staff=True)

        target = 'portfoliyo.pusher.events.trigger'
        with mock.patch(target) as mock_trigger:
            models.BulkPost.create(rel.elder, None, 'Foo\n', sequence_id='33')

        student_args = mock_trigger.call_args_list[0][0]
        student_post_data = student_args[2]['objects'][0]
        group_args = mock_trigger.call_args_list[1][0]
        group_post_data = group_args[2]['objects'][0]

        assert student_args[0] == 'user_%s' % rel.from_profile_id
        assert group_args[0] == 'user_%s' % rel.from_profile_id
        assert student_args[1] == group_args[1] == 'message_posted'
        assert student_post_data['author_sequence_id'] == '33'
        assert student_post_data['author_id'] == rel.from_profile_id
        assert group_post_data['author_sequence_id'] == '33'
        assert group_post_data['author_id'] == rel.from_profile_id
        assert student_post_data['student_id'] == rel.to_profile_id
        assert group_post_data['group_id'] == 'all%s' % rel.from_profile_id


    def test_new_post_unread_for_all_web_users_but_author(self, db, redis):
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


    def test_texts_selected_mobile_users(self, db):
        """Sends text to selected active mobile users."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__source_phone="+13336660000",
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
            "+13216540987", "+13336660000", "Hey dad --John Doe")
        assert post.to_sms == True
        assert post.meta['sms'] == [
            {
                'id': rel2.elder.id,
                'name': 'Jim Smith',
                'role': 'Father',
                'phone': "+13216540987",
                }
            ]


    def test_text_all_mobile_users(self, db):
        """Sends text to all active mobile users if 'all' given."""
        rel1 = factories.RelationshipFactory.create(
            from_profile__name="John Doe",
            from_profile__phone=None,
            )
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.to_profile,
            from_profile__phone="+13216540987",
            from_profile__source_phone="+13336660000",
            from_profile__user__is_active=True,
            from_profile__role="Father",
            from_profile__name="Jim Smith",
            )
        group = factories.GroupFactory.create()
        group.students.add(rel1.student)

        target = 'portfoliyo.model.village.models.tasks.send_sms.delay'
        with mock.patch(target) as mock_send_sms:
            post = models.BulkPost.create(
                rel1.elder, group, 'Hey dad', sms_profile_ids='all')

        mock_send_sms.assert_called_with(
            "+13216540987", "+13336660000", "Hey dad --John Doe")
        assert post.to_sms == True
        assert post.meta['sms'] == [
            {
                'id': rel2.elder.id,
                'name': 'Jim Smith',
                'role': 'Father',
                'phone': "+13216540987",
                }
            ]


    def test_records_notifications(self, db):
        """Records notification for users in group."""
        group = factories.GroupFactory.create()
        rel = factories.RelationshipFactory.create(
            from_profile=group.owner)
        other = factories.ProfileFactory.create()
        group.elders.add(other)
        group.students.add(rel.student)

        target = 'portfoliyo.notifications.record.bulk_post'
        with mock.patch(target) as mock_notify_bulk_post:
            bulk_post = models.BulkPost.create(
                rel.elder, group, "Hello")

        mock_notify_bulk_post.assert_called_with(other, bulk_post)


class TestBasePost(object):
    def test_extra_data(self):
        assert models.BasePost().extra_data() == {}


class TestPost(object):
    def test_relationship_deleted(self, db):
        """Deleting a relationship does not delete posts in that village."""
        rel = factories.RelationshipFactory.create()
        post = factories.PostFactory.create(
            student=rel.student, relationship=rel)

        rel.delete()

        assert not utils.deleted(post)



class TestText2Html(object):
    def test_escapes_html(self, monkeypatch):
        """Escapes any HTML in the original text."""
        assert models.text2html('<b>') == '&lt;b&gt;'


    def test_replaces_newlines(self):
        """Replaces newlines with <br>."""
        assert models.text2html('foo\nbar') == 'foo<br>bar'



def test_sms_suffix():
    """SMS suffix is name_or_role preceded by ' --'."""
    rel = mock.Mock()
    rel.name_or_role = "Foo"
    assert models.sms_suffix(rel) == " --Foo"



@mock.patch('portfoliyo.model.village.models.sms_suffix')
def test_post_char_limit(mock_sms_suffix):
    """Char limit for a post is 160 - length of suffix."""
    mock_sms_suffix.return_value = "a" * 10
    rel = mock.Mock()

    assert models.post_char_limit(rel) == 150
