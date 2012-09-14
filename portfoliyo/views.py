"""Core/home views."""
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from session_csrf import anonymous_csrf

from .landing.views import landing




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
            return reverse('add_student')
        return reverse('no_students')
    elif len(students) == 1:
        return reverse('chat', kwargs=dict(student_id=students[0].id))
    return reverse('home')



@anonymous_csrf
def home(request):
    """Home view. Redirects or displays a get-started page."""
    if request.user.is_authenticated():
        dest = redirect_home(request.user)

        if dest != request.path:
            return redirect(dest)

        return TemplateResponse(request, 'village/dashboard.html')
    else:
        return landing(request)
