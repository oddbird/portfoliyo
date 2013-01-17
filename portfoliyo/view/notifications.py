from django.http import HttpResponse

from portfoliyo.notifications import render



def send_email(request):
    """
    Debug view to force sending of notification email.

    By default doesn't erase the pending notifications, so you can get the same
    email repeatedly after updating the templates/styles. Pass the querystring
    parameter ?clear=1 to erase notifications.

    Most likely useful in conjunction with ``PORTFOLIYO_NOTIFICATION_EMAILS =
    False`` in settings, to suppress the normal sending of notification emails
    immediately upon receipt of a triggering notification.

    """
    clear = request.GET.get('clear', False) == '1'
    sent = render.send(request.user.profile.id, clear=clear)
    if sent:
        response = "Email sent to %s." % request.user.email
    else:
        if not request.user.is_active:
            reason = "User inactive"
        elif not request.user.email:
            reason = "User has no email address"
        else:
            reason = "No notifications found"
        response = "%s; no email sent." % reason

    return HttpResponse(response)
