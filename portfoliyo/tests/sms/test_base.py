import mock
from django.conf import settings

from portfoliyo import sms


def test_split_sms():
    """An overly-long SMS is split."""
    phone = '+132165437890'
    longtext = 'a' * 161
    with mock.patch('portfoliyo.sms.base.backend') as mock_backend:
        sms.send(phone, longtext)

    mock_send = mock_backend.send
    mock_send.assert_any_call(
        phone, settings.DEFAULT_NUMBER, ('a' * 157) + '...')
    mock_send.assert_any_call(
        phone, settings.DEFAULT_NUMBER, '...' + ('a' * 4))
