from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User



class EmailBackend(ModelBackend):
    """
    Requires login with email instead of username.

    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
