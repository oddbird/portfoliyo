from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    "",
    url(
        r"^$",
        direct_to_template,
        {"template": "home.html"},
        name="home",
        ),
    url(
        r"^signup/$",
        direct_to_template,
        {"template": "signup.html"},
        name="signup",
        ),
    url(
        r"^register/$",
        direct_to_template,
        {"template": "register.html"},
        name="register",
        ),
    url(
        r"^login/$",
        direct_to_template,
        {"template": "users/login.html"},
        name="login",
        ),
    url(
        r"^password_change/$",
        direct_to_template,
        {"template": "users/password_change.html"},
        name="password_change",
        ),
    url(
        r"^password_reset/$",
        direct_to_template,
        {"template": "users/password_reset.html"},
        name="password_reset",
        ),
    url(
        r"^password_reset_confirm/$",
        direct_to_template,
        {"template": "users/password_reset_confirm.html"},
        name="password_reset_confirm",
        ),
    url(
        r"^username/edit/$",
        direct_to_template,
        {"template": "users/user_edit.html"},
        name="edit_profile",
        ),
    url(
        r"^username/network/$",
        direct_to_template,
        {"template": "users/network.html"},
        name="network",
        ),
    url(
        r"^username/join_network/$",
        direct_to_template,
        {"template": "users/join_network.html"},
        name="join_network",
        ),
    url(
        r"^username/$",
        direct_to_template,
        {"template": "users/user_feed.html"},
        name="profile",
        ),
)
