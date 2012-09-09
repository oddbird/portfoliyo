"""Landing page views."""
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from session_csrf import anonymous_csrf

from ..users.forms import CaptchaAuthenticationForm
from ..view.ajax import ajax

from .forms import LeadForm



@anonymous_csrf
@ajax("landing/_form.html")
def landing(request):
    """A landing page with an email address signup."""
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thanks for your interest; we'll be in touch soon!")
            return redirect("landing")
    else:
        form = LeadForm()

    request.session.set_test_cookie()

    return TemplateResponse(
        request,
        "landing.html",
        {
            "form": form,
            "login_form": CaptchaAuthenticationForm(request),
            },
        )
