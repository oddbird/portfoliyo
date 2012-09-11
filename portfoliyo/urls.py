from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from . import admin

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    "",
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
    url(
        r"^student/add/$",
        login_required(direct_to_template),
        {"template": "student/add_student.html"},
        name="add_student",
        ),
    url(
        r"^student/id/invite/$",
        login_required(direct_to_template),
        {"template": "student/invite_elder.html"},
        name="invite_elder",
        ),
    url(
        "^student/id/$",
        login_required(direct_to_template),
        {"template": "student/chat.html"},
        name="village_detail",
        ),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^", include("portfoliyo.users.urls")),
)
