from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from .. import admin
from ..api.versions import api_v1
from . import home as home_views
from . import sms as sms_views

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    '',
    url(r'^_twilio_hook/$', sms_views.twilio_receive),
    url(r'^$', home_views.home, name='home'),
    url(r'^no_students/$',
        login_required(direct_to_template),
        {'template': 'no_students.html'},
        name='no_students',
        ),
    url(r'^student/', include('portfoliyo.view.village.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_v1.urls)),
    url(r'^', include('portfoliyo.view.users.urls')),
    )


if settings.DEBUG: # pragma: no cover
    urlpatterns += patterns( # pragma: no cover
        '',
        url(r'^_debug/403/$', direct_to_template, {'template': '403.html'}),
        url(r'^_debug/404/$', direct_to_template, {'template': '404.html'}),
        url(r'^_debug/500/$', direct_to_template, {'template': '500.html'}),
        )


def handler500(request):
    """500 error handler which includes ``request`` in the context."""
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(Context({'request': request})))
