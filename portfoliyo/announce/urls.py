from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^_mark_read/(?P<annc_id>\d+)/$',
        views.mark_announcement_read,
        name='mark_announcement_read',
        ),
    )
