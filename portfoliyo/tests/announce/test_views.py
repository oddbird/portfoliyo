"""Tests for announcement views."""
from django.core.urlresolvers import reverse

from portfoliyo.announce import models as announce
from portfoliyo.tests import factories


def test_mark_announcement_read(no_csrf_client):
    p = factories.ProfileFactory.create(user__email='foo@example.com')
    a = announce.to_all('something')

    assert list(announce.get_unread(p)) == [a]

    no_csrf_client.post(
        reverse('mark_announcement_read', kwargs={'annc_id': a.id}),
        user=p.user,
        )

    assert list(announce.get_unread(p)) == []
