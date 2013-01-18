"""Pusher authentication."""
from __future__ import absolute_import

import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .base import get_pusher



def allow(profile, channel):
    """Return True if ``profile`` should be allowed in pusher ``channel``."""
    channel_type, channel_id = channel.rsplit('_', 1)

    if channel_type.startswith('private-'):
        channel_type = channel_type[len('private-'):]
    else:
        # if channel isn't private, any access is allowed
        return True

    if channel_type == 'user' and channel_id == str(profile.id):
        return True

    return False



@require_POST
@csrf_exempt
def pusher_auth(request):
    channel = request.POST["channel_name"]
    socket_id = request.POST["socket_id"]

    pusher = get_pusher()

    if (pusher and
            request.user.is_authenticated() and
            allow(request.user.profile, channel)
            ):
        r = pusher[channel].authenticate(socket_id)
        return HttpResponse(json.dumps(r), mimetype="application/json")

    return HttpResponseForbidden("Not Authorized")
