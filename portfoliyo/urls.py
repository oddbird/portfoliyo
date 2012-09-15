from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.defaults import page_not_found, server_error
from django.views.generic.simple import direct_to_template

from . import admin, views
from .sms import views as sms_views

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    '',
    url(r'^_twilio_hook/$', sms_views.twilio_receive),
    url(r'^$', views.home, name='home'),
    url(r'^no_students/$',
        login_required(direct_to_template),
        {'template': 'no_students.html'},
        name='no_students',
        ),
    url(r'^student/', include('portfoliyo.village.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('portfoliyo.users.urls')),
    )


def handler500(request):
    """500 error handler which includes ``request`` in the context."""
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(Context({'request': request})))
