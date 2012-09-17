"""Factories for village models."""
import factory

from portfoliyo.village import models

from ..users import factories


class PostFactory(factory.Factory):
    FACTORY_FOR = models.Post

    author = factory.SubFactory(factories.ProfileFactory)
    student = factory.SubFactory(factories.ProfileFactory)
    original_text = 'foo'
    html_text = 'foo'
