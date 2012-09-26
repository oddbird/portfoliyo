"""Tests for elder-related template tags."""
from portfoliyo.view.templatetags import elders

from portfoliyo.tests import factories


class TestElderStatus(object):
    """Tests for elder_status template filter."""
    def test_declined(self):
        p = factories.ProfileFactory(declined=True)
        assert elders.elder_status(p, None) == 'declined'


    def test_inactive(self):
        p = factories.ProfileFactory(user__is_active=False)
        assert elders.elder_status(p, None) == 'inactive'


    def test_mobile(self):
        p = factories.ProfileFactory(phone='+13216540987')
        assert elders.elder_status(p, None) == 'mobile'


    def test_offline(self):
        p = factories.ProfileFactory()
        assert elders.elder_status(p, None) == 'offline'


    def test_current(self):
        p = factories.ProfileFactory()
        assert elders.elder_status(p, p) == ''



class TestElderStatusDescription(object):
    """Tests for elder_status_description filter."""
    def test_current(self):
        p = factories.ProfileFactory()
        assert elders.elder_status_description(p, p) == 'This is you!'


    def test_declined(self):
        p = factories.ProfileFactory(name='Foo', declined=True)
        assert elders.elder_status_description(p, None) == (
            'Foo has declined to receive SMS notifications.')


    def test_no_phone(self):
        p = factories.ProfileFactory(name='Foo', phone=None)
        assert elders.elder_status_description(p, None) == (
            'Foo has no phone number on their account.')


    def test_inactive(self):
        p = factories.ProfileFactory(
            name='Foo', phone='+13216540987', user__is_active=False)
        assert elders.elder_status_description(p, None) == (
            'Foo is inactive and will not receive SMS notifications.')


    def test_active(self):
        p = factories.ProfileFactory(name='Foo', phone='+13216540987')
        assert elders.elder_status_description(p, None) == (
            'Foo will receive SMS notifications if mentioned in a post.')
