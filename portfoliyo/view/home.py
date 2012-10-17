"""Core/home views."""
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from session_csrf import anonymous_csrf

from portfoliyo.landing.views import landing




def redirect_home(user):
    """
    Return the 'home' URL for a user.

    Since our home view often redirects users elsewhere, this function can be
    used by other views that want to redirect to home to avoid needless
    double-redirects.

    """
    if not user.is_authenticated():
        return reverse('login')
    students = user.profile.students
    if not students:
        if user.profile.school_staff:
            return reverse('add_group')
        return reverse('no_students')
    return reverse('dashboard')


@anonymous_csrf
def home(request):
    """Home view. Redirects appropriately or displays landing page."""
    if request.user.is_authenticated():
        return redirect(redirect_home(request.user))
    else:
        return landing(request)
