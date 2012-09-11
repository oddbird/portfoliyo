from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from . import admin

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    '',
    url(
        "^$",
        login_required(direct_to_template),
        {"template": "home.html"},
        name="home",
        ),
    url(r"^signup/$", "portfoliyo.landing.views.landing", name="landing"),
    url(
        r"^username/edit/$",
        login_required(direct_to_template),
        {"template": "users/user_edit.html"},
        name="edit_profile",
        ),
    url(r"^student/", include("portfoliyo.village.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^", include("portfoliyo.users.urls")),
    )
