"""
Student/elder (village) views.

"""
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ..users.decorators import school_staff_required
from ..users import models as user_models
from ..view.ajax import ajax
from . import forms, models



@login_required
@ajax('village/_dashboard_content.html')
def dashboard(request):
    """Dashboard view for users with multiple students."""
    return TemplateResponse(
        request,
        'village/dashboard.html',
        {'elders_formset': forms.InviteEldersFormSet(prefix='elders')},
        )



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
        request,
        'village/add_student.html',
        {
            'form': form,
            'elders_formset': form.elders_formset,
            },
        )



def get_related_student_or_404(student_id, profile):
    """Get student with ID student_id who is student of profile, or 404."""
    return get_object_or_404(
        user_models.Profile.objects.filter(
            relationships_to__from_profile=profile
            ).select_related('user'),
        id=student_id,
        )



@school_staff_required
@ajax('village/_invite_elders_content.html')
def invite_elders(request, student_id):
    """Invite new elder(s) to a student's village."""
    student = get_related_student_or_404(student_id, request.user.profile)

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
        {'elders_formset': formset, 'student': student},
        )



@login_required
@ajax('village/_village_content.html')
def village(request, student_id):
    """The main chat view for a student/village."""
    student = get_related_student_or_404(student_id, request.user.profile)

    return TemplateResponse(
        request,
        'village/village.html',
        {
            'student': student,
            'elders_formset': forms.InviteEldersFormSet(prefix='elders'),
            },
        )



@login_required
def json_posts(request, student_id):
    """Get backlog of up to 100 latest posts from this village."""
    student = get_related_student_or_404(student_id, request.user.profile)

    data = json.dumps(
        [
            post.json_data() for post in
            student.posts_in_village.order_by('-timestamp')[:100]
            ]
        )

    return HttpResponse(data, content_type='application/json')



@login_required
@require_POST
def create_post(request, student_id):
    """Create a post in given student's village."""
    student = get_related_student_or_404(student_id, request.user.profile)
    text = request.POST['text']
    models.Post.create(request.user.profile, student, text)
