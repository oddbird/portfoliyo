from django.http import HttpResponse

from portfoliyo.notifications import render
from portfoliyo.view.decorators import login_required



@login_required
def send_email(request):
    """
    Debug view to force sending of notification email.

    By default doesn't erase the pending notifications, so you can get the same
    email repeatedly after updating the templates/styles. Pass the querystring
    parameter ?clear=1 to erase notifications.

    Most likely useful in conjunction with ``NOTIFICATION_EMAILS = False`` in
    settings, to suppress the normal sending of notification emails immediately
    upon receipt of a triggering notification.

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



@login_required
def show_email(request):
    """
    Debug view to show notification email in browser.

    By default doesn't erase the pending notifications, so you can get the same
    email repeatedly after updating the templates/styles. Pass the querystring
    parameter ?clear=1 to erase notifications.

    Can also pass querystring parameter ?text=1 to see the plain-text rather
    than HTML email.

    Most likely useful in conjunction with ``NOTIFICATION_EMAILS = False`` in
    settings, to suppress the normal sending of notification emails immediately
    upon receipt of a triggering notification.

    """
    clear = request.GET.get('clear', False) == '1'
    show_text = request.GET.get('text', False) == '1'
    try:
        subject, text, html = render.render(request.user.profile, clear=clear)
    except render.NothingToDo:
        response = "No notifications found."
        content_type = "text/plain"
    else:
        if show_text:
            response = text
            content_type = "text/plain"
        else:
            response = html
            content_type = "text/html"

    return HttpResponse(response, content_type=content_type)
