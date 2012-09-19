"""Tests for SMS backend base class."""
import pytest

from portfoliyo.sms.backends import base


def test_send_not_implemented():
    """send() method raises NotImplementedError."""
    sms = base.SMSBackend()
    with pytest.raises(NotImplementedError):
        sms.send('1', '2', 'body')
