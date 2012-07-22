"""Landing page models."""
from django.db import models


class Lead(models.Model):
    """Someone who signs up for more info at the landing page."""
    email = models.EmailField()
    signed_up = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        """Unicode representation is the email address."""
        return self.email
