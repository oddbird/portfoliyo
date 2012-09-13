from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from . import admin, views

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    '',
    url("^$", views.home, name="home"),
    url(
        "^no_students/$",
        login_required(direct_to_template),
        {"template": "no_students.html"},
        name="no_students",
        ),
    url(r"^signup/$", "portfoliyo.landing.views.landing", name="landing"),
    url(r"^student/", include("portfoliyo.village.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^", include("portfoliyo.users.urls")),
    )
