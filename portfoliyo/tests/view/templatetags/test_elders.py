"""Tests for elder-related template tags."""
from portfoliyo.view.templatetags import elders

from portfoliyo.tests import factories


class TestElderStatus(object):
    """Tests for elder_status template filter."""
    def test_declined(self):
        p = factories.ProfileFactory.build(declined=True)
        assert elders.elder_status(p, None) == 'declined'


    def test_inactive(self):
        p = factories.ProfileFactory.build(user__is_active=False)
        assert elders.elder_status(p, None) == 'inactive'


    def test_mobile(self):
        p = factories.ProfileFactory.build(phone='+13216540987')
        assert elders.elder_status(p, None) == 'mobile'


    def test_online(self):
        p = factories.ProfileFactory.build(school_staff=True)
        assert elders.elder_status(p, None) == 'online'



class TestElderStatusDescription(object):
    """Tests for elder_status_description filter."""
    def test_current(self):
        p = factories.ProfileFactory.build()
        assert elders.elder_status_description(p, p) == 'This is you!'


    def test_declined(self):
        p = factories.ProfileFactory.build(name='Foo', declined=True)
        assert elders.elder_status_description(p, None) == (
            'Foo has declined to receive SMS notifications.')


    def test_inactive(self):
        p = factories.ProfileFactory.build(
            name='Foo', phone='+13216540987', user__is_active=False)
        assert elders.elder_status_description(p, None) == (
            'Foo is not yet active.')


    def test_active(self):
        p = factories.ProfileFactory.build(name='Foo', phone='+13216540987')
        assert elders.elder_status_description(p, None) == (
            'Foo receives SMS notifications.')
