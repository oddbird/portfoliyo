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
        name="user_edit",
        ),
)
