"""Tests for unread-counts management."""
from portfoliyo.model import unread

from portfoliyo.tests import factories



def test_read(db, redis):
    """By default, a post is read."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()

    assert not unread.is_unread(post, profile)



def test_unread(db, redis):
    """After marking a post unread, it shows up as unread."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()

    unread.mark_unread(post, profile)

    assert unread.is_unread(post, profile)



def test_all_unread(db, redis):
    """After marking a post unread, it shows up in all_unread set."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()

    unread.mark_unread(post, profile)

    assert unread.all_unread(post.student, profile) == {str(post.id)}



def test_mark_read(db, redis):
    """Can mark a post as read."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post, profile)

    unread.mark_read(post, profile)

    assert not unread.is_unread(post, profile)



def test_mark_village_read(db, redis):
    """Marks posts only in given village read."""
    post1 = factories.PostFactory.create()
    post2 = factories.PostFactory.create(student=post1.student)
    other_village_post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post1, profile)
    unread.mark_unread(post2, profile)
    unread.mark_unread(other_village_post, profile)

    unread.mark_village_read(post1.student, profile)

    assert not unread.is_unread(post1, profile)
    assert not unread.is_unread(post2, profile)
    assert unread.is_unread(other_village_post, profile)



def test_unread_count(db, redis):
    post1 = factories.PostFactory.create()
    factories.PostFactory.create(student=post1.student)
    other_village_post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post1, profile)
    unread.mark_unread(other_village_post, profile)

    # Only post1; the second is read, and other is wrong village
    assert unread.unread_count(post1.student, profile) == 1



def test_group_unread_count(db, redis):
    post1 = factories.PostFactory.create()
    factories.PostFactory.create(student=post1.student)
    post2 = factories.PostFactory.create()
    group = factories.GroupFactory.create()
    group.students.add(post1.student, post2.student)
    other_village_post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post1, profile)
    unread.mark_unread(post2, profile)
    unread.mark_unread(other_village_post, profile)

    assert unread.group_unread_count(group, profile) == 2
