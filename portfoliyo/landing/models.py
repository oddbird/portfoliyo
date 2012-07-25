"""Landing page models."""
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Lead(models.Model):
    """Someone who signs up for more info at the landing page."""
    email = models.EmailField()
    following_up = models.ForeignKey(User, blank=True, null=True)
    notes = models.TextField(blank=True)
    signed_up = models.DateTimeField(default=now)


    def __unicode__(self):
        """Unicode representation is the email address."""
        return self.email
