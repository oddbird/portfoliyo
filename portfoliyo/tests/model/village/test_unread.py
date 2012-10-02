"""Tests for unread-counts management."""
from portfoliyo.model import unread

from portfoliyo.tests import factories



def test_read():
    """By default, a post is read."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()

    assert unread.is_read(post, profile)



def test_unread():
    """After marking a post unread, it shows up as unread."""
    post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()

    unread.mark_unread(post, profile)

    assert not unread.is_read(post, profile)



def test_mark_village_read():
    """Marks posts only in given village read."""
    post1 = factories.PostFactory.create()
    post2 = factories.PostFactory.create(student=post1.student)
    other_village_post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post1, profile)
    unread.mark_unread(post2, profile)
    unread.mark_unread(other_village_post, profile)

    unread.mark_village_read(post1.student, profile)

    assert unread.is_read(post1, profile)
    assert unread.is_read(post2, profile)
    assert not unread.is_read(other_village_post, profile)



def test_unread_count():
    post1 = factories.PostFactory.create()
    factories.PostFactory.create(student=post1.student)
    other_village_post = factories.PostFactory.create()
    profile = factories.ProfileFactory.create()
    unread.mark_unread(post1, profile)
    unread.mark_unread(other_village_post, profile)

    # Only post1; the second is read, and other is wrong village
    assert unread.unread_count(post1.student, profile) == 1
