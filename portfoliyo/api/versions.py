"""Api versions."""

from tastypie import api

from . import resources



class PortfoliyoApi(api.Api):
    """
    Override a deprecated method in order to avoid a deprecation warning!

    See https://github.com/toastdriven/django-tastypie/issues/692

    """
    def override_urls(self):
        return []


api_v1 = PortfoliyoApi(api_name='v1')
api_v1.register(resources.GroupResource())
api_v1.register(resources.ProfileResource())
api_v1.register(resources.PostResource())
api_v1.register(resources.BulkPostResource())
api_v1.register(resources.ElderRelationshipResource())
