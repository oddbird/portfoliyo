"""
Account-related URLs.

"""
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template



urlpatterns = patterns(
    "portfoliyo.users.views",

    # auth -------------------------------------------------------------------

    url(r"^login/", "login", name="login"),
    url(r"^logout/", "logout", name="logout"),
    url(r"^password/change/$", "password_change", name="password_change"),
    url(r"^password/reset/$", "password_reset", name="password_reset"),
    url(r"^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        "password_reset_confirm",
        name="password_reset_confirm"),

    # registration -----------------------------------------------------------

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r"^activate/(?P<activation_key>\w+)/$",
        "activate",
        name="activate"),
    url(r"^register/$",
        "register",
        name="register"),
    url(r"^register/closed/$",
        direct_to_template,
        {"template": "users/registration_closed.html"},
        name="registration_disallowed"),
    )
