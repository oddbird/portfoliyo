"""
Account-related URLs.

"""
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from . import views



urlpatterns = patterns(
    '',
    # profile ----------------------------------------------------------------

    url(r'^profile/$', views.edit_profile, name='edit_profile'),

    # auth -------------------------------------------------------------------

    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^password/change/$', views.password_change, name='password_change'),
    url(r'^password/reset/$', views.password_reset, name='password_reset'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^accept/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.accept_email_invite,
        name='accept_email_invite'),
    url(r'^confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.confirm_email,
        name='confirm_email'),

    # registration -----------------------------------------------------------

    url(r'^register/$',
        views.register,
        name='register'),
    url(r'^register/closed/$',
        direct_to_template,
        {'template': 'users/registration_closed.html'},
        name='registration_disallowed'),
    url(r'^donate/$', views.donate, name='donate'),
)