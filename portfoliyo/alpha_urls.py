from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    "",
    url(
        "^$",
        direct_to_template,
        {"template": "signup.html"},
        name="landing",
        ),

)
