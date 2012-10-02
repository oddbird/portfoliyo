"""Tests for SnapEngage support code."""
from django.test.utils import override_settings

from portfoliyo import snapengage


def test_context_processor():
    with override_settings(SNAPENGAGE_ID="foo"):
        expected = {"SNAPENGAGE_ID": "foo"}
        assert snapengage.context_processor(None) == expected
