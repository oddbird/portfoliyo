from base64 import b64encode
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from hashlib import sha1

from registration.backends.default import DefaultBackend
from registration.models import RegistrationProfile

from .models import Profile
from .forms import RegistrationForm



class RegistrationBackend(DefaultBackend):
    """Custom registration backend that doesn't require username."""
    def register(self, request, name, email, password, role, **kwargs):
        """
        Create inactive user and profile with given data.

        Generates a username via SHA hash of email address (which
        registration form ensures is unique) to satisfy Django's
        requirement of a <30-character unique username.

        Also create RegistrationProfile with activation key for later
        activation.

        """
        username = b64encode(sha1(email).digest())

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        Profile.objects.create(user=new_user, name=name, role=role)

        reg_profile = RegistrationProfile.objects.create_profile(new_user)
        reg_profile.send_activation_email(RequestSite(request))

        return new_user


    def get_form_class(self, request):
        """Return the default form class used for user registration."""
        return RegistrationForm
