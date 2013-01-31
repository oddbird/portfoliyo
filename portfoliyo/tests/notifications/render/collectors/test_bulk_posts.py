"""Tests for BulkPostCollector and related classes."""
import pytest

from portfoliyo.notifications.render.collectors import bulk_posts
from portfoliyo.tests import factories



def test_not_visible(db):
    """A bulkpost that doesn't show up in any of my villages fails hydration."""
    p = factories.ProfileFactory.create()
    bpc = bulk_posts.BulkPostCollector(p)
    bp = factories.BulkPostFactory.create()

    with pytest.raises(bulk_posts.base.RehydrationFailed):
        bpc.hydrate({'bulk-post-id': bp.id})
