"""Tests for admin."""
import mock

from portfoliyo.model.users import admin



def test_denormalized_email():
    email = 'foo@example.com'
    profile = mock.Mock()
    profile.user.email = email

    assert admin.email(profile) == email
