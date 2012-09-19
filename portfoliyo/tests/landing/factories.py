"""Factories for landing-page models."""
import factory

from portfoliyo.landing import models



class LeadFactory(factory.Factory):
    FACTORY_FOR = models.Lead

    email = "foo@example.com"

