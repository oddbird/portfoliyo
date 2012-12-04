"""Tests for announcement models."""
from portfoliyo.announce import models as announce
from portfoliyo.tests import factories



def test_unicode():
    """Unicode rep of announcement is the text itself."""
    a = factories.AnnouncementFactory.build(text="foobar")

    assert unicode(a) == u"foobar"


def test_read_unread(db):
    """Test announce_to_all, get_unread_announcements, mark_read_by."""
    p1 = factories.ProfileFactory.create(user__email='one@example.com')
    p2 = factories.ProfileFactory.create(user__email='two@example.com')
    p3 = factories.ProfileFactory.create(user__email=None)

    a1 = announce.to_all("Something is happening!")
    a2 = announce.to_all("Something else is happening!")

    assert list(announce.get_unread(p1)) == [a1, a2]
    assert list(announce.get_unread(p2)) == [a1, a2]
    assert list(announce.get_unread(p3)) == []

    announce.mark_read(p1, a1.id)

    assert list(announce.get_unread(p1)) == [a2]
    assert list(announce.get_unread(p2)) == [a1, a2]
