"""
Account-related URLs.

"""
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from portfoliyo.users import views



urlpatterns = patterns(
    '',

    # auth -------------------------------------------------------------------

    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^password/change/$', views.password_change, name='password_change'),
    url(r'^password/reset/$', views.password_reset, name='password_reset'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^accept/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.accept_email_invite,
        name='accept_email_invite'),

    # registration -----------------------------------------------------------

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible 'invalid key' message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        views.activate,
        name='activate'),
    url(r'^register/$',
        views.register,
        name='register'),
    url(r'^register/closed/$',
        direct_to_template,
        {'template': 'users/registration_closed.html'},
        name='registration_disallowed'),
    )
