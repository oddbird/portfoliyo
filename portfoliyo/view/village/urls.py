from django.conf.urls.defaults import patterns, url, include

from . import views

per_student_patterns = patterns(
    '',
    url(r'^invite/$', views.invite_elder, name='invite_elder'),
    url(r'^edit/$', views.edit_student, name='edit_student'),
    url(r'^elder/(?P<elder_id>\d+)/$', views.edit_elder, name='edit_elder'),
    url(r'^$', views.village, name='village'),
    url(r'^_posts/$', views.json_posts, name='json_posts'),
    )


per_group_patterns = patterns(
    '',
    url(r'^$', views.group, name='group'),
    url(r'^invite/$', views.invite_elder, name='invite_elder_to_group'),
    url(r'^edit/$', views.edit_group, name='edit_group'),
    url(r'^add/$', views.add_student, name='add_student_in_group'),
    url(r'^instructions-(?P<lang>en|es).pdf$',
        views.pdf_parent_instructions,
        name='pdf_parent_instructions_group',
        ),
    )


urlpatterns = patterns(
    '',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^add/$', views.add_student, name='add_student'),
    url(r'^(?P<student_id>\d+)/', include(per_student_patterns)),
    url(r'^all/$', views.all_students, name='all_students'),
    url(r'^group/add/$', views.add_group, name='add_group'),
    url(r'^group/(?P<group_id>\d+)/', include(per_group_patterns)),
    url(r'^instructions-(?P<lang>en|es).pdf$',
        views.pdf_parent_instructions,
        name='pdf_parent_instructions',
        ),
    )
