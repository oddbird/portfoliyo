"""
Models and related functions all imported here to provide unified import point.

Code elsewhere can simply do::

    from portfoliyo import model

and then reference any model class as e.g. model.User, model.Profile...

"""
from django.contrib.auth.models import User
from .users.models import Profile, Relationship
from .village.models import Post, post_char_limit
