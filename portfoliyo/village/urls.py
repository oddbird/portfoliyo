from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^add/$', views.add_student, name='add_student'),
    url(r'^(?P<student_id>\d+)/invite/$',
        views.invite_elders,
        name='invite_elders',
        ),
    url('^(?P<student_id>\d+)/$', views.village, name='village'),
    )
