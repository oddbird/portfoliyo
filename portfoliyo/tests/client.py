"""
Webapp integration test client.

"""
import django_webtest



class TestClient(django_webtest.DjangoTestApp):
    """
    A WebTest-based test client for webapp integration tests.

    """
    def get(self, *a, **kw):
        """Add easier support for making simulated ajax requests."""
        ajax = kw.pop('ajax', False)
        if ajax:
            headers = kw.setdefault('headers', {})
            headers['X-Requested-With'] = 'XMLHttpRequest'
        return super(TestClient, self).get(*a, **kw)


    def post(self, *a, **kw):
        """Add easier support for making simulated ajax requests."""
        ajax = kw.pop('ajax', False)
        if ajax:
            headers = kw.setdefault('headers', {})
            headers['X-Requested-With'] = 'XMLHttpRequest'
        return super(TestClient, self).post(*a, **kw)
