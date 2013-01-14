"""
Tracking mixpanel events from Python code.

This is a simple synchronous implementation; it should not be called directly
from code in the request cycle, but only via the Celery task.

"""
import base64
import json
import logging
import posixpath
import urllib
import urllib2

from django.conf import settings


logger = logging.getLogger(__name__)


MIXPANEL_API_BASE = 'http://api.mixpanel.com/'


def track(event, properties=None):
    """Track ``event`` with given dict of ``properties``."""
    _send('track/', {'event': event, 'properties': properties or {}})



def people_set(user_id, data):
    """Set given mixpanel ``data`` (dict) for given ``user_id``."""
    _send('engage/', {'$set': data, '$distinct_id': user_id, '$ip': 0})



def people_increment(user_id, data):
    """Increment given mixpanel ``data`` (dict) for given ``user_id``."""
    _send('engage/', {'$add': data, '$distinct_id': user_id, '$ip': 0})



def _send(path, params):
    """
    Send ``params`` dict to ``path`` endpoint in Mixpanel API.

    Logs a warning if the response from Mixpanel does not have status code 200
    and content "1" (which is what Mixpanel's API returns for success).


    """
    mixpanel_id = getattr(settings, 'MIXPANEL_ID', None)
    if mixpanel_id is None:
        return

    # Mixpanel API is not consistent about where token goes
    if 'track' in path:
        params['properties']['token'] = mixpanel_id
    else: # engage/
        params['$token'] = mixpanel_id

    data = base64.b64encode(json.dumps(params))

    url = "%s?%s" % (
        posixpath.join(MIXPANEL_API_BASE, path),
        urllib.urlencode({'data': data}),
        )

    resp = urllib2.urlopen(url)

    code = resp.getcode()
    body = resp.read()

    if code != 200:
        logger.warning(
            "Mixpanel returned bad status code %s",
            code,
            extra={
                'stack': True,
                'body': body,
                'params': params,
                },
            )
    elif body != '1':
        logger.warning(
            "Mixpanel returned bad response %s",
            body,
            extra={
                'stack': True,
                'params': params,
                },
            )
