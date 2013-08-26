"""Tests for base NotificationTypeCollector."""
import mock

from portfoliyo.notifications.render.collectors import base


def test_default_context_empty():
    """Default template context for a notification collector is empty."""
    ntc = base.NotificationTypeCollector(mock.Mock())

    assert ntc.get_context() == {}
