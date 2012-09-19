"""Tests for root urlconf."""
from django.conf.urls import patterns, url
from django.core.signals import got_request_exception
from django.core.urlresolvers import clear_url_caches
from django.test.utils import override_settings
from django.test.signals import setting_changed

# imported so it will be present in this URLconf as 500 handler
from portfoliyo.view.urls import handler500



def raises_500(request):
    """A view that causes a 500 server error."""
    raise ValueError("something busted.")


urlpatterns = patterns(
    '',
    url('^500/$', raises_500),
    )


def _clear_url_caches(setting, value, **kwargs):
    if setting == 'ROOT_URLCONF':
        clear_url_caches()


def fake_sentry_handler(request=None, **kwargs):
    if request:
        request.sentry = {'id': 'the-sentry-id'}


setting_changed.connect(_clear_url_caches)
got_request_exception.connect(fake_sentry_handler)


def test_sentry_500_handler(client):
    """500 handler puts request in template context."""
    with override_settings(
            ROOT_URLCONF='portfoliyo.tests.view.test_urls',
            DEBUG_PROPAGATE_EXCEPTIONS=False,
            ):
        response = client.get('/500/', status=500)

    response.mustcontain('the-sentry-id')
