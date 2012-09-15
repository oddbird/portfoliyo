"""
Tests for format-normalization functions.

"""
import pytest

from portfoliyo.users import formats


@pytest.mark.parametrize(
    'raw',
    [
        '(321)456-7890',
        '3214567890',
        '321-456-7890',
        '321.456.7890',
        '+13214567890',
        ],
    )
def test_valid_phone_numbers(raw):
    """Returns valid phone numbers re-formatted to E.164 format."""
    assert formats.normalize_phone(raw) == '+13214567890'


@pytest.mark.parametrize(
    'raw',
    ['foo', '', 'bar@example.com'],
    )
def test_invalid_phone_numbers(raw):
    """Returns None for unparseable phone numbers."""
    assert formats.normalize_phone(raw) is None


@pytest.mark.parametrize(
    ('raw', 'output'),
    [
        ('foo@EXAMPLE.COM', 'foo@example.com')
        ],
    )
def test_valid_emails(raw, output):
    """Returns valid phone numbers with domain part lower-cased."""
    assert formats.normalize_email(raw) == output


@pytest.mark.parametrize(
    'raw',
    ['foo'],
    )
def test_invalid_emails(raw):
    """Returns None for unparseable emails."""
    assert formats.normalize_email(raw) is None
