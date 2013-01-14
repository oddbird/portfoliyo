"""Tracking mixpanel events from Python code."""
import base64
import json
import logging
import urllib2

from django.conf import settings


logger = logging.getLogger(__name__)


MIXPANEL_BASE_URL = 'http://api.mixpanel.com/track/?data=%(data)s'


def track(event, properties=None):
    """
    Track ``event`` with given dict of ``properties``.

    This is a simple synchronous implementation; it should not be called
    directly from code in the request cycle, but only via the Celery task.

    Logs a warning if the response from Mixpanel does not have status code 200
    and content "1" (which is what Mixpanel's API returns for success).

    """
    mixpanel_id = getattr(settings, 'MIXPANEL_ID', None)
    if mixpanel_id is None:
        return

    properties = properties or {}
    properties['token'] = mixpanel_id

    params = {'event': event, 'properties': properties}
    data = base64.b64encode(json.dumps(params))

    url = MIXPANEL_BASE_URL % {'data': data}

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
