"""
Student/elder (village) views.

"""
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

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


def get_relationship_or_404(student_id, profile):
    """Get relationship between student_id and profile, or 404."""
    try:
        return user_models.Relationship.objects.select_related().get(
            from_profile=profile,
            to_profile_id=student_id,
            kind=user_models.Relationship.KIND.elder,
            )
    except user_models.Relationship.DoesNotExist:
        raise Http404



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
    rel = get_relationship_or_404(student_id, request.user.profile)

    return TemplateResponse(
        request,
        'village/village.html',
        {
            'student': rel.student,
            'post_char_limit': models.post_char_limit(rel),
            'elders_formset': forms.InviteEldersFormSet(prefix='elders'),
            },
        )



@login_required
def json_posts(request, student_id):
    """Get backlog of up to 100 latest posts, or POST a post."""
    rel = get_relationship_or_404(student_id, request.user.profile)

    if request.method == 'POST' and 'text' in request.POST:
        text = request.POST['text']
        limit = models.post_char_limit(rel)
        if len(text) > limit:
            return HttpResponseBadRequest(
                json.dumps(
                    {
                        'error': 'Posts are limited to %s characters.' % limit,
                        'success': False,
                        }
                    )
                )
        post = models.Post.create(request.user.profile, rel.student, text)

        data = {
            'success': True,
            'posts': [post.json_data()],
            }

        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {
        'posts':
            [
            post.json_data() for post in
            reversed(rel.student.posts_in_village.order_by('-timestamp')[:100])
            ],
        }

    return HttpResponse(json.dumps(data), content_type='application/json')
