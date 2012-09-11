from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(
        r"^add/$", views.add_student, name="add_student"),
    url(
        r"^(?P<student_id>\d+)/invite/$",
        views.invite_elder,
        name="invite_elder",
        ),
    url(
        "^(?P<student_id>\d+)/$", views.chat, name="chat"),
    )
