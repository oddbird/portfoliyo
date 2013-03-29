"""
Account-related forms.

"""
import operator
import random
import time

from django.contrib.auth import forms as auth_forms

import floppyforms as forms

from portfoliyo import model
from .. import forms as pyoforms


class SchoolRadioSelect(forms.RadioSelect):
    """A RadioSelect with a custom display template."""
    template_name = 'users/school_radio.html'



class SchoolForm(forms.ModelForm):
    class Meta:
        model = model.School
        fields = ['name', 'postcode']



class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the email address is not already in use, and requires the
    password to be entered twice to catch typos. Also allows user to either
    pick from an existing list of schools or enter a new one.

    """
    name = pyoforms.StripCharField(max_length=200)
    role = pyoforms.StripCharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        label="confirm password",
        widget=forms.PasswordInput(render_value=False))
    email = forms.EmailField(max_length=255)
    country_code = forms.TypedChoiceField(
        choices=model.Profile._meta.get_field('country_code').choices,
        widget=forms.RadioSelect(),
        )
    school = pyoforms.ModelChoiceField(
        queryset=model.School.objects.filter(auto=False).order_by('name'),
        empty_label=u"I'm not affiliated with a school or program",
        required=False,
        widget=SchoolRadioSelect,
        initial=u'',
        )
    addschool = forms.BooleanField(
        initial=False, required=False, widget=forms.HiddenInput)


    def __init__(self, *args, **kwargs):
        """Also instantiate a nested SchoolForm."""
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.addschool_form = SchoolForm(self.data or None, prefix='addschool')


    def clean(self):
        """
        Verify password fields match and school is provided.

        If addschool is True, build a new School based on data in nested
        SchoolForm.

        If not, and no school was selected, auto-construct one.

        """
        data = self.cleaned_data
        password = data.get('password')
        confirm = data.get('password_confirm')
        if password != confirm:
            raise forms.ValidationError("The passwords didn't match.")
        if data.get('addschool'):
            if self.addschool_form.is_valid():
                data['school'] = self.addschool_form.save(commit=False)
            else:
                raise forms.ValidationError(
                    "Could not add a school.")
        else:
            # reinstantiate unbound addschool_form to avoid spurious errors
            self.addschool_form = SchoolForm(prefix='addschool')
            if data.get('email') and not data.get('school'):
                data['school'] = model.School(
                    name=(u"%f-%s" % (time.time(), data['email']))[:200],
                    postcode="",
                    auto=True,
                    )
        return data


    def clean_email(self):
        """Validate that the supplied email address is unique."""
        if model.User.objects.filter(
                email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                "This email address is already in use. "
                "Please supply a different email address."
                )
        return self.cleaned_data['email']


    def save(self):
        """Save and return new user profile."""
        school = self.cleaned_data['school']
        if school.id is None:
            # this could just set country_code and then school.save(), but that
            # creates a race condition for two users creating same school at
            # same time, resulting in IntegrityError
            school, created = model.School.objects.get_or_create(
                name=school.name,
                postcode=school.postcode,
                defaults={
                    'country_code': self.cleaned_data['country_code'],
                    'auto': school.auto,
                    },
                )

        profile = model.Profile.create_with_user(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
            country_code=self.cleaned_data['country_code'],
            school=school,
            school_staff=True,
            email_confirmed=False,
            is_active=True,
            email_notifications=True,
            )

        return profile




class PasswordResetForm(auth_forms.PasswordResetForm):
    """A password reset form that doesn't reveal valid users."""
    def clean_email(self):
        """No validation that the email address exists."""
        return self.cleaned_data["email"]


    def save(self, *args, **kwargs):
        """Fetch the affected users here before sending reset emails."""
        email = self.cleaned_data["email"]
        # super's save expects self.users_cache to be set.
        self.users_cache = model.User.objects.filter(email__iexact=email)

        return super(PasswordResetForm, self).save(*args, **kwargs)


class SetPasswordForm(auth_forms.SetPasswordForm):
    """A set-password form that activates inactive users."""
    def save(self, *args, **kwargs):
        self.user.is_active = True
        return super(SetPasswordForm, self).save(*args, **kwargs)



OPERATORS = {
    "plus": operator.add,
    "minus": operator.sub,
    "times": operator.mul,
    }

CAPTCHA_SESSION_KEY = "auth_captcha_answer"


class NoRequiredValidationIntegerField(forms.IntegerField):
    """
    Disables the built-in "required" validation.

    We want the captcha field to be marked as required, but we want to control
    the validation of that ourselves in the form's clean_captcha method, so
    that the first time the captcha field appears it doesn't appear with a
    "This field is required." error.

    """
    def validate(self, value):
        pass



class CaptchaAuthenticationForm(auth_forms.AuthenticationForm):
    """
    Login form with a simple math captcha.

    For use when there have been too many failed login attempts from a
    particular IP address or for a particular username. Simply locking users
    out in this case creates a potential Denial of Service vulnerability; a
    captcha allows a human to still log in but makes life more difficult for
    the brute-force attacker. Obviously a dedicated attacker could write a bot
    to circumvent this captcha, so it's really just a roadblock to casual
    attacks.

    Expected answer to captcha is stored in the session; this avoids replay
    attacks and the need to trust client input, at the cost of somewhat higher
    likelihood of spurious failure, e.g. if the user opens up captcha login
    forms in two tabs and then tries to use the first one.

    """
    username = forms.CharField(label="Username", max_length=255)


    def __init__(self, *args, **kwargs):
        """Initialize form, including captcha question and expected answer."""
        super(CaptchaAuthenticationForm, self).__init__(*args, **kwargs)

        # get previous expected answer before generating new one
        self.captcha_answer = self.request.session.get(CAPTCHA_SESSION_KEY)

        # only add the captcha field if this request hit the rate limit
        if getattr(self.request, "limited", False):
            a, b = random.randint(1,9), random.randint(1, 9)
            # avoid negative answers
            if b > a: # pragma: no cover
                a, b = b, a
            opname, op = random.choice(OPERATORS.items())

            # store the expected answer in the session
            self.request.session[CAPTCHA_SESSION_KEY] = op(a, b)

            self.fields["captcha"] = NoRequiredValidationIntegerField(
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


    def clean(self):
        """
        No username/password validation if captcha validation failed.

        Otherwise, the captcha would do nothing to prevent brute-forcing a
        username/password combo, since a brute-forcing bot could keep trying
        usernames and passwords and look for the presence or absence of the
        "Please supply a valid username/password" error.

        """
        if not self._errors:
            return super(CaptchaAuthenticationForm, self).clean()



class EditProfileForm(forms.ModelForm):
    """Form for editing a users profile."""
    name = pyoforms.StripCharField(max_length=200)
    role = pyoforms.StripCharField(max_length=200)


    class Meta:
        fields = ['name', 'role'] + model.Profile.NOTIFICATION_PREFS
        model = model.Profile


    def __init__(self, *args, **kw):
        super(EditProfileForm, self).__init__(*args, **kw)
        self.old_role = self.instance.role


    def save(self):
        """Save edits and return updated profile."""
        profile = super(EditProfileForm, self).save()
        profile.relationships_from.filter(description=self.old_role).update(
            description='')

        return profile
