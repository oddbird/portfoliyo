"""SMS-related views."""
from __future__ import absolute_import

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators import http, csrf
from twilio import twiml
from twilio.util import RequestValidator

from ..village.sms import receive_sms


@csrf.csrf_exempt
@http.require_POST
def twilio_receive(request):
    """Receive an SMS via Twilio."""
    # Validate the request
    try:
        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        url = request.build_absolute_uri()
        signature = request.META['HTTP_X_TWILIO_SIGNATURE']
    except (AttributeError, KeyError):
        return HttpResponseForbidden()

    # Now that we have all the required information to perform forgery
    # checks, we'll actually do the forgery check.
    if not validator.validate(url, request.POST, signature):
        return HttpResponseForbidden()

    source = request.POST['From']
    body = request.POST['Body']

    receive_sms(source, body)

    return HttpResponse(str(twiml.Response()), content_type='application/xml')
