"""Caching-related code."""
from django.utils.cache import add_never_cache_headers


class NeverCacheAjaxGetMiddleware(object):
    """Most browsers don't cache AJAX, but IE9 does. We don't want it cached."""
    def process_response(self, request, response):
        if request.is_ajax() and request.method == "GET":
            add_never_cache_headers(response)
        return response
