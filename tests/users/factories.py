"""Factories for user models."""
from django.contrib.auth import models as auth_models
import factory

from portfoliyo.users import models


class UserFactory(factory.Factory):
    FACTORY_FOR = auth_models.User

    username = factory.Sequence(lambda n: "test{0}".format(n))
    email = factory.Sequence(lambda n: "test{0}@example.com".format(n))


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for ``set_password`` method."""
        password = kwargs.pop("password", None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ProfileFactory(factory.Factory):
    FACTORY_FOR = models.Profile

    user = factory.SubFactory(UserFactory)
    name = "Test User"
    phone = factory.Sequence(lambda n: "999-999-{0:04}".format(n))
    role = "Some Role"
