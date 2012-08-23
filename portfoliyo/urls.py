from django.conf.urls.defaults import patterns, url, include

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    "",
    url("^$", "portfoliyo.landing.views.landing", name="landing"),

    url(r"^admin/", include(admin.site.urls)),

    url(r"^alpha/", include("portfoliyo.alpha_urls")),
)
