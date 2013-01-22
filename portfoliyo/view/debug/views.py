import json

from django.http import HttpResponse
from django.test.client import RequestFactory

from portfoliyo.api import versions
from portfoliyo.view.village import views



def api(request):
    """
    Allows viewing API SQL queries in Debug Toolbar.

    Requires _resource querystring parameter naming the API resource to query;
    all other querystring parameters are passed along to the resource.

    A resource name of 'json_posts' is special-cased to the ``json_posts``
    custom view rather than the API.

    """
    params = request.GET.copy()
    resource_name = params.pop('_resource')[0]

    if resource_name == 'json_posts':
        req = RequestFactory().get('/_posts/')
        req.user = request.user
        response = views.json_posts(req, **params)
    else:
        resource = versions.api_v1.canonical_resource_for(resource_name)
        req = RequestFactory().get('/api/v1/%s' % resource_name, params)
        req.user = request.user
        response = resource.get_list(req)

    data = json.loads(response.content)

    return HttpResponse(
        '<html><body><h1>API Debugger</h1><pre>%s</pre></body></html>'
        % json.dumps(data, sort_keys=True, indent=2)
        )
