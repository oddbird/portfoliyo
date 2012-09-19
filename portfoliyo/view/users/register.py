"""
Custom Portfoliyo registration code.

"""
from django.contrib.sites.models import RequestSite

from registration.backends.default import DefaultBackend
from registration.models import RegistrationProfile

from portfoliyo import model
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
        profile = model.Profile.create_with_user(
            name=name,
            email=email,
            password=password,
            role=role,
            school_staff=True,
            )

        reg_profile = RegistrationProfile.objects.create_profile(profile.user)
        reg_profile.send_activation_email(RequestSite(request))

        return profile.user


    def get_form_class(self, request):
        """Return the default form class used for user registration."""
        return RegistrationForm
