import json

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
    response = resource.get_list(req)

    data = json.loads(response.content)

    return HttpResponse(
        '<html><body><h1>API Debugger</h1><pre>%s</pre></body></html>'
        % json.dumps(data, sort_keys=True, indent=2)
        )
