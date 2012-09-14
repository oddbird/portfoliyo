"""
Student/elder (village) views.

"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from ..users.decorators import school_staff_required
from ..users import models as user_models
from ..view.ajax import ajax
from . import forms



@login_required
@ajax('village/_dashboard_content.html')
def dashboard(request):
    """Dashboard view for users with multiple students."""
    return TemplateResponse(request, 'village/dashboard.html')



@school_staff_required
@ajax('village/_add_student_content.html')
def add_student(request):
    """Add a student and elders."""
    if request.method == 'POST':
        form = forms.AddStudentAndInviteEldersForm(request.POST)
        if form.is_valid():
            student, _ = form.save(request, added_by=request.user.profile)
            return redirect('village', student_id=student.id)
    else:
        form = forms.AddStudentAndInviteEldersForm()

    return TemplateResponse(
        request, 'village/add_student.html', {'form': form})



@school_staff_required
@ajax('village/_invite_elders_content.html')
def invite_elders(request, student_id):
    """Invite new elder(s) to a student's village."""
    student = get_object_or_404(
        user_models.Profile.objects.filter(
            relationships_to__from_profile=request.user.profile
            ).select_related('user'),
        id=student_id,
        )

    if request.method == 'POST':
        formset = forms.InviteEldersFormSet(request.POST, prefix='elders')
        if formset.is_valid():
            formset.save(request, student)
            return redirect('village', student_id=student.id)
    else:
        formset = forms.InviteEldersFormSet(prefix='elders')

    return TemplateResponse(
        request,
        'village/invite_elders.html',
        {'formset': formset, 'student': student},
        )



@login_required
@ajax('village/_village_content.html')
def village(request, student_id):
    """The main chat view for a student/village."""
    student = get_object_or_404(
        user_models.Profile.objects.filter(
            relationships_to__from_profile=request.user.profile
            ).select_related('user'),
        id=student_id,
        )

    return TemplateResponse(
        request, 'village/village.html', {'student': student})
