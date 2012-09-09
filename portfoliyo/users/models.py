"""
Portfoliyo network models.

"""
from django.contrib.auth import models as auth_models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models

from model_utils import Choices


# monkeypatch Django's User.email to be sufficiently long and unique/nullable
email_field = auth_models.User._meta.get_field("email")
email_field._unique = True
email_field.null = True
email_field.max_length = 255

# monkeypatch User's __unicode__ method to be friendlier for no-username
auth_models.User.__unicode__ = lambda self: self.email or self.profile.name


class Profile(models.Model):
    """A Portfoliyo user profile."""
    user = models.OneToOneField(auth_models.User)
    # fields from User we use: username, password, email
    name = models.CharField(max_length=200)
    phone = PhoneNumberField(blank=True, null=True, unique=True)
    # e.g. "Math Teacher", "Father", "Principal", etc
    # serves as default fall-back for the relationship-description field
    role = models.CharField(max_length=200)
    school_staff = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name


# monkeypatch Django's User.email to be sufficiently long and unique/nullable
email_field = auth_models.User._meta.get_field("email")
email_field._unique = True
email_field.null = True
email_field.max_length = 255
