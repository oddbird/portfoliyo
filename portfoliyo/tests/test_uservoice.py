"""Tests for UserVoice support code."""
from django.test.utils import override_settings

from portfoliyo import uservoice


def test_context_processor():
    with override_settings(USERVOICE_ID="foo"):
        expected = {"USERVOICE_ID": "foo"}
        assert uservoice.context_processor(None) == expected
