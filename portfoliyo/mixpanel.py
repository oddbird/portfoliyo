"""Tracking mixpanel events from Python code."""
import base64
import json
import urllib2

from django.conf import settings


MIXPANEL_BASE_URL = 'http://api.mixpanel.com/track/?data=%(data)s'


def track(event, properties=None):
    """
    Track ``event`` with given dict of ``properties``.

    This is a simple synchronous implementation; it should not be called
    directly from code in the request cycle, but only via the Celery task.

    """
    mixpanel_id = getattr(settings, 'MIXPANEL_ID', None)
    if mixpanel_id is None:
        return

    properties = properties or {}
    properties['token'] = mixpanel_id

    params = {'event': event, 'properties': properties}
    data = base64.b64encode(json.dumps(params))

    url = MIXPANEL_BASE_URL % {'data': data}

    urllib2.urlopen(url)
