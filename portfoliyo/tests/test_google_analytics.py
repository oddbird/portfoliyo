"""Tests for GA support code."""
from django.test.utils import override_settings

from portfoliyo import google_analytics


def test_context_processor():
    with override_settings(GOOGLE_ANALYTICS_ID="foo"):
        expected = {"GOOGLE_ANALYTICS_ID": "foo"}
        assert google_analytics.context_processor(None) == expected
