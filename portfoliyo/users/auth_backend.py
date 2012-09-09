from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User



class EmailBackend(ModelBackend):
    """
    Requires login with email instead of username.

    """
    def authenticate(self, username=None, password=None):
        """
        Authenticate user by email address. Pre-select profile.

        Credential argument is still named ``username`` to be compatible with
        default ``AuthenticationForm`` (we could override its ``clean`` method
        to fix this, but not worth it, especially since we may add username
        authentication back in later).

        """
        try:
            user = User.objects.select_related("profile").get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        """Get user by ID. Pre-select profile."""
        try:
            return User.objects.select_related("profile").get(pk=user_id)
        except User.DoesNotExist:
            return None
