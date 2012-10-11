"""
Account-related views.

"""
from functools import partial

from django.contrib.auth import views as auth_views, forms as auth_forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.views.decorators.http import require_POST

from ratelimit.decorators import ratelimit
from registration import views as registration_views
from session_csrf import anonymous_csrf

from portfoliyo import model
from ..home import redirect_home
from . import forms



@anonymous_csrf
@ratelimit(field='username', method='POST', rate='5/m')
def login(request):
    kwargs = {
        'template_name': 'users/login.html',
        'authentication_form': forms.CaptchaAuthenticationForm,
        }
    # the contrib.auth login view doesn't pass request into the bound form,
    # but CaptchaAuthenticationForm needs it, so we ensure it's passed in
    if request.method == 'POST':
        kwargs['authentication_form'] = partial(
            kwargs['authentication_form'], request)
    return auth_views.login(request, **kwargs)



@require_POST
def logout(request):
    return auth_views.logout(request, next_page=reverse('home'))



@login_required
def password_change(request):
    response = auth_views.password_change(
        request,
        template_name='users/password_change.html',
        password_change_form=auth_forms.PasswordChangeForm,
        post_change_redirect=redirect_home(request.user),
        )

    if response.status_code == 302:
        messages.success(request, "Password changed.")

    return response



@anonymous_csrf
def password_reset(request):
    response = auth_views.password_reset(
        request,
        password_reset_form=forms.PasswordResetForm,
        template_name='users/password_reset.html',
        email_template_name='registration/password_reset_email.txt',
        subject_template_name='registration/password_reset_subject.txt',
        post_reset_redirect=redirect_home(request.user),
        )

    if response.status_code == 302:
        messages.success(
            request,
            u"Password reset email sent; check your email. "
            u"If you don't receive an email, verify that you are entering the "
            u"email address you signed up with, and try again."
            )

    return response



@anonymous_csrf
def password_reset_confirm(request, uidb36, token):
    response = auth_views.password_reset_confirm(
        request,
        uidb36=uidb36,
        token=token,
        template_name='users/password_reset_confirm.html',
        set_password_form=auth_forms.SetPasswordForm,
        post_reset_redirect=redirect_home(request.user),
        )

    if response.status_code == 302:
        messages.success(request, "Password changed.")

    return response



def activate(request, activation_key):
    response = registration_views.activate(
        request,
        activation_key=activation_key,
        backend='portfoliyo.view.users.register.RegistrationBackend',
        template_name='users/activate.html',
        success_url=reverse('login'),
        )

    if response.status_code == 302:
        messages.success(request, "Account activated; now you can login.")

    return response



@anonymous_csrf
def register(request):
    return registration_views.register(
        request,
        backend='portfoliyo.view.users.register.RegistrationBackend',
        template_name='users/register.html',
        success_url=reverse('awaiting_activation'),
        )



@anonymous_csrf
def accept_email_invite(request, uidb36, token):
    response = auth_views.password_reset_confirm(
        request,
        uidb36=uidb36,
        token=token,
        template_name='users/accept_email_invite.html',
        set_password_form=auth_forms.SetPasswordForm,
        post_reset_redirect=reverse('edit_profile'),
        )

    if response.status_code == 302:
        uid_int = base36_to_int(uidb36)
        model.User.objects.filter(id=uid_int).update(is_active=True)
        messages.success(
            request,
            u"Great, you've chosen a password! "
            u"Now log in using your email address and password "
            u"to see messages about your student.",
            )

    return response


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = forms.EditProfileForm(
            request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, u"Profile changes saved!")
            return redirect(redirect_home(request.user))
    else:
        form = forms.EditProfileForm(instance=request.user.profile)

    return TemplateResponse(request, 'users/edit_profile.html', {'form': form})
