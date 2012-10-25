import mock

from portfoliyo.api import authorization


class TestPortfoliyoAuthorization(object):
    def test_only_get_authorized(self):
        """Non-GET requests are forbidden by default."""
        a = authorization.PortfoliyoAuthorization()
        request = mock.Mock()
        request.method = 'POST'
        response = a.is_authorized(request)

        assert response.status_code == 403
