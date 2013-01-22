import debug_toolbar.middleware
import debug_toolbar.urls
from django.http import HttpResponse
from django.test.client import RequestFactory

from portfoliyo.api import versions



def api(request):
    """
    Allows viewing API SQL queries in Debug Toolbar.

    Requires _resource querystring parameter naming the API resource to query;
    all other querystring parameters are passed along to the resource.

    """
    params = request.GET.copy()
    resource_name = params.pop('_resource')[0]

    resource = versions.api_v1.canonical_resource_for(resource_name)

    req = RequestFactory().get('/api/v1/%s' % resource_name, params)
    req.user = request.user

    resource.get_list(req)

    return HttpResponse('<html><body>API Debugger</body></html>')



class DebugToolbarMiddleware(debug_toolbar.middleware.DebugToolbarMiddleware):
    """Avoid conflict with AjaxMessagesMiddleware."""
    def process_response(self, request, response):
        response = super(DebugToolbarMiddleware, self).process_response(
            request, response)
        if request.path.startswith(debug_toolbar.urls._PREFIX):
            response.no_messages = True
        return response
