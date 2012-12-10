from django.test.utils import override_settings

from portfoliyo.view import context_processors


def test_google_analytics():
    with override_settings(GOOGLE_ANALYTICS_ID='foo'):
        d = context_processors.services(None)
        assert d['GOOGLE_ANALYTICS_ID'] == 'foo'


def test_snapengage():
    with override_settings(SNAPENGAGE_ID='foo'):
        d = context_processors.services(None)
        assert d['SNAPENGAGE_ID'] == 'foo'


def test_uservoice():
    with override_settings(USERVOICE_ID='foo'):
        d = context_processors.services(None)
        assert d['USERVOICE_ID'] == 'foo'


def test_mixpanel():
    with override_settings(MIXPANEL_ID='foo'):
        d = context_processors.services(None)
        assert d['MIXPANEL_ID'] == 'foo'


def test_pusher():
    with override_settings(PUSHER_KEY='foo'):
        d = context_processors.services(None)
        assert d['PUSHER_KEY'] == 'foo'
