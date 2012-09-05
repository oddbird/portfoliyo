"""
Account-related forms.

"""
import operator
import random

from django.contrib.auth import forms as auth_forms, models as auth_models

import floppyforms as forms



class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the email address is not already in use, and
    requires the password to be entered twice to catch typos.

    """
    name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        label="confirm password",
        widget=forms.PasswordInput(render_value=False))
    role = forms.CharField(max_length=200)


    def clean(self):
        """Verify that the password fields match."""
        password = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("password_confirm")
        if password != confirm:
            raise forms.ValidationError("The passwords didn't match.")
        return self.cleaned_data


    def clean_email(self):
        """Validate that the supplied email address is unique."""
        if auth_models.User.objects.filter(
                email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                "This email address is already in use. "
                "Please supply a different email address."
                )
        return self.cleaned_data['email']



class PasswordResetForm(auth_forms.PasswordResetForm):
    """A password reset form that doesn't reveal valid users."""
    def clean_email(self):
        """No validation that the email address exists."""
        return self.cleaned_data["email"]


    def save(self, *args, **kwargs):
        """Fetch the affected users here before sending reset emails."""
        email = self.cleaned_data["email"]
        # super's save expects self.users_cache to be set.
        self.users_cache = auth_models.User.objects.filter(
            email__iexact=email, is_active=True)

        return super(PasswordResetForm, self).save(*args, **kwargs)



OPERATORS = {
    "plus": operator.add,
    "minus": operator.sub,
    "times": operator.mul,
    }

CAPTCHA_SESSION_KEY = "auth_captcha_answer"



class CaptchaAuthenticationForm(auth_forms.AuthenticationForm):
    """
    Login form with a simple math captcha.

    For use when there have been too many failed login attempts from a
    particular IP address or for a particular username. Simply locking users
    out in this case creates a potential Denial of Service vulnerability; a
    captcha allows a human to still log in but makes life more difficult for
    the brute-force attacker.

    Expected answer to captcha is stored in the session; this avoids replay
    attacks and the need to trust client input, at the cost of somewhat higher
    likelihood of spurious failure, e.g. if the user opens up captcha login
    forms in two tabs and then tries to use the first one.

    """
    def __init__(self, *args, **kwargs):
        """Initialize form, including captcha question and expected answer."""
        super(CaptchaAuthenticationForm, self).__init__(*args, **kwargs)

        # get previous expected answer before generating new one
        self.captcha_answer = self.request.session.get(CAPTCHA_SESSION_KEY)

        # only add the captcha field if this request hit the rate limit
        if getattr(self.request, "limited", False):
            a, b = random.randint(1,9), random.randint(1, 9)
            # avoid negative answers
            if b > a:
                a, b = b, a
            opname, op = random.choice(OPERATORS.items())

            # store the expected answer in the session
            self.request.session[CAPTCHA_SESSION_KEY] = op(a, b)

            self.fields["captcha"] = forms.IntegerField(
                widget=forms.TextInput,
                label=u"What is {0} {1} {2}?".format(a, opname, b),
                )


    def clean_captcha(self):
        """
        Fail form validation if captcha answer is not the expected answer.

        If no expected captcha answer was previously generated (this is the
        request on which they hit the rate limit for the first time) and no
        captcha answer was provided in the POST data, we don't fail them -- if
        they've got the right username and password on the login attempt that
        first hits the rate limit, their login should succeed.

        """
        answer = self.cleaned_data.get("captcha")
        if answer != self.captcha_answer:
            raise forms.ValidationError(
                "Sorry, that's not the answer we were looking for.")
