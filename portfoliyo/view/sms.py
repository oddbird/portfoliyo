"""SMS-related views."""
from __future__ import absolute_import
from functools import wraps
from posixpath import join

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators import http, csrf
from twilio import twiml
from twilio.util import RequestValidator

from portfoliyo import xact
from portfoliyo.sms import hook
from portfoliyo.sms.base import split_sms


def twilio(viewfunc):
    """
    Wrap a Twilio-request-handling view.

    Validates the request, and expects the view func to return a TwiML
    response.

    """
    @wraps(viewfunc)
    def decorator(request, *args, **kw):
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

        twiml = viewfunc(request, *args, **kw)

        return HttpResponse(str(twiml), content_type='application/xml')

    return decorator


@csrf.csrf_exempt
@http.require_POST
@twilio
def twilio_receive(request):
    """Receive an SMS via Twilio."""
    source = request.POST['From']
    to = request.POST['To']
    body = request.POST['Body']

    with xact.xact():
        reply = hook.receive_sms(source, to, body)

    response = twiml.Response()

    if reply:
        for chunk in split_sms(reply):
            response.sms(chunk)

    return response


@csrf.csrf_exempt
@http.require_POST
@twilio
def twilio_voice(request):
    """Receive a voice call via Twilio."""
    response = twiml.Response()

    response.play(join(settings.STATIC_URL, 'audio/phone-message.wav'))

    return response
