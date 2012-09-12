"""
Student/elder (village) views.

"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from ..users import models as user_models
from . import forms


@user_passes_test(lambda u: u.profile.school_staff)
def add_student(request):
    """Add a student and elders."""
    if request.method == 'POST':
        form = forms.AddStudentAndInviteEldersForm(request.POST)
        if form.is_valid():
            student, _ = form.save(added_by=request.user.profile)
            return redirect(reverse('chat', kwargs={'student_id': student.id}))
    else:
        form = forms.AddStudentAndInviteEldersForm()

    return TemplateResponse(
        request, 'village/add_student.html', {'form': form})



@user_passes_test(lambda u: u.profile.school_staff)
def invite_elder(request, student_id):
    """Invite new elder(s) to a student's village."""
    student = get_object_or_404(
        user_models.Profile.objects.select_related('user'), id=student_id)

    # @@@ check that user is part of this student's village

    if request.method == 'POST':
        form = forms.InviteElderForm(request.POST)
        if form.is_valid():
            form.save(student)
            return redirect(reverse('chat', kwargs={'student_id': student.id}))
    else:
        form = forms.InviteElderForm()

    return TemplateResponse(
        request,
        'village/invite_elder.html',
        {'form': form, 'student': student},
        )



@login_required
def chat(request, student_id):
    """The main chat view for a student/village."""
    student = get_object_or_404(
        user_models.Profile.objects.select_related('user'), id=student_id)

    # @@@ check that user is part of this student's village

    return TemplateResponse(request, 'village/chat.html', {'student': student})
