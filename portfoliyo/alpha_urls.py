from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    "",
    url(
        r"^signup/",
        direct_to_template,
        {"template": "signup.html"},
        name="landing",
        ),
    url(
        r"^username/edit/",
        direct_to_template,
        {"template": "users/user_edit.html"},
        name="edit_profile",
        ),
    url(
        r"^username/network/",
        direct_to_template,
        {"template": "users/network.html"},
        name="network",
        ),
    url(
        r"^username/join_network/",
        direct_to_template,
        {"template": "users/join_network.html"},
        name="join_network",
        ),
    url(
        r"^username/",
        direct_to_template,
        {"template": "users/user_feed.html"},
        name="profile",
        ),
)
