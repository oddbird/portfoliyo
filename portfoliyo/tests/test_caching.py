"""Tests for caching code."""
from django.test import RequestFactory
import mock

from portfoliyo import caching



class TestNeverCacheAjaxGetMiddleware(object):
    def test_no_cache_ajax_get(self):
        req = RequestFactory().get(
            '/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        middleware = caching.NeverCacheAjaxGetMiddleware()
        resp = mock.Mock()

        target = 'portfoliyo.caching.add_never_cache_headers'
        with mock.patch(target) as mock_add_never_cache_headers:
            retval = middleware.process_response(req, resp)

        assert retval is resp
        mock_add_never_cache_headers.assert_called_with(resp)
