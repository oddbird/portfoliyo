from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    "",
    url(
        r"^$",
        direct_to_template,
        {"template": "village_landing.html"},
        name="village_landing",
        ),

    url(r"^admin/", include(admin.site.urls)),
)
