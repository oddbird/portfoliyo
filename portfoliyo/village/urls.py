from django.conf.urls.defaults import patterns, url, include

from . import views

per_student_patterns = patterns(
    '',
    url(r'^invite/$', views.invite_elders, name='invite_elders'),
    url(r'^$', views.village, name='village'),
    url(r'^_posts/$', views.json_posts, name='json_posts'),
    )


urlpatterns = patterns(
    '',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^add/$', views.add_student, name='add_student'),
    url(r'^(?P<student_id>\d+)/', include(per_student_patterns)),
    )
