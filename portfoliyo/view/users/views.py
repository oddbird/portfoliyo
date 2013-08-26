"""
Account-related views.

"""
from functools import partial

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import views as auth_views, forms as auth_forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.views.decorators.http import require_POST

from ratelimit.decorators import ratelimit
from session_csrf import anonymous_csrf

from portfoliyo import model, invites, xact
from portfoliyo.view import tracking
from ..decorators import login_required
from ..home import redirect_home
from . import forms, tokens



@anonymous_csrf
@ratelimit(field='username', method='POST', rate='5/m')
@xact.xact # auth_views.login sends user_logged_in signal, updates last_login
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
@xact.xact
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
        email_template_name='emails/password_reset.txt',
        subject_template_name='emails/password_reset.subject.txt',
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
@xact.xact
def password_reset_confirm(request, uidb36, token):
    response = auth_views.password_reset_confirm(
        request,
        uidb36=uidb36,
        token=token,
        template_name='users/password_reset_confirm.html',
        set_password_form=forms.SetPasswordForm,
        post_reset_redirect=redirect_home(request.user),
        )

    if response.status_code == 302:
        messages.success(request, "Password changed.")

    return response



@anonymous_csrf
def register(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            with xact.xact():
                profile = form.save()
                user = profile.user
                user.backend = settings.AUTHENTICATION_BACKENDS[0]
                auth.login(request, user)
                token_generator = tokens.EmailConfirmTokenGenerator()
                invites.send_invite_email(
                    profile,
                    'emails/welcome',
                    token_generator=token_generator,
                    )
                messages.success(
                    request,
                    "Welcome to Portfoliyo! "
                    "Grab your phone and add yourself as a parent "
                    "to see how it works!"
                    )
                tracking.track(
                    request,
                    'registered',
                    email_notifications=(
                        'yes'
                        if form.cleaned_data.get('email_notifications')
                        else 'no'
                        ),
                    user_id=user.id,
                    )
            return redirect(redirect_home(user))
    else:
        form = forms.RegistrationForm()

    return TemplateResponse(
        request,
        'users/register.html',
        {'form': form},
        )



def confirm_email(request, uidb36, token):
    """Confirm an email address."""
    try:
        uid_int = base36_to_int(uidb36)
        user = model.User.objects.get(id=uid_int)
    except (ValueError, model.User.DoesNotExist):
        user = None

    token_generator = tokens.EmailConfirmTokenGenerator()

    if user is not None and token_generator.check_token(user, token):
        with xact.xact():
            user.is_active = True
            user.save(force_update=True)
            profile = user.profile
            profile.email_confirmed = True
            profile.save(force_update=True)
            messages.success(request, "Email address %s confirmed!" % user.email)
            tracking.track(request, 'confirmed email')
        return redirect(redirect_home(user))

    return TemplateResponse(request, 'users/confirmation_failed.html')



@anonymous_csrf
@xact.xact
def accept_email_invite(request, uidb36, token):
    response = auth_views.password_reset_confirm(
        request,
        uidb36=uidb36,
        token=token,
        template_name='users/accept_email_invite.html',
        set_password_form=auth_forms.SetPasswordForm,
        post_reset_redirect=reverse('login'),
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
        tracking.track(request, 'accepted email invite')

    return response


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = forms.EditProfileForm(
            request.POST, instance=request.user.profile)
        if form.is_valid():
            with xact.xact():
                form.save()
            messages.success(request, u"Profile changes saved!")
            return redirect(redirect_home(request.user))
    else:
        form = forms.EditProfileForm(instance=request.user.profile)

    return TemplateResponse(request, 'users/edit_profile.html', {'form': form})
