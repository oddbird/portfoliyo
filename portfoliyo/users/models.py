"""
Portfoliyo network models.

"""
from django.contrib.auth import models as auth_models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models


class Profile(models.Model):
    """A Portfoliyo user profile."""
    user = models.OneToOneField(auth_models.User)
    # fields from User we use: username, password, email
    name = models.CharField(max_length=200)
    phone = PhoneNumberField(blank=True)
    # @@@ later this should maybe be per-student?
    # e.g. "Math Teacher", "Father", "Principal", etc
    role = models.CharField(max_length=200)


    def __unicode__(self):
        return self.name


# monkeypatch Django's User.email to be sufficiently long and unique/nullable
email_field = auth_models.User._meta.get_field("email")
email_field._unique = True
email_field.null = True
email_field.max_length = 255
