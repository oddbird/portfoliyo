"""Tests for API resources."""
import mock

from portfoliyo.api import resources



def test_dehydrate_email():
    email = 'foo@example.com'
    bundle = mock.Mock()
    bundle.obj.user.email = email

    assert resources.ProfileResource().dehydrate_email(bundle) == email
