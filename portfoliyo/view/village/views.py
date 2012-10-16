"""
Student/elder (village) views.

"""
import json
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django import http
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse

from portfoliyo import model, pdf
from ..ajax import ajax
from ..decorators import school_staff_required
from . import forms


# number of posts to show in backlog
BACKLOG_POSTS = 100


@login_required
@ajax('village/_dashboard_content.html')
def dashboard(request):
    """Dashboard view for users with multiple students."""
    return TemplateResponse(
        request,
        'village/dashboard.html',
        {},
        )


def redirect_to_village(student, group=None):
    """Redirect to a student village, optionally in group context."""
    target = reverse('village', kwargs=dict(student_id=student.id))
    if group:
        target = '%s?group=%s' % (target, group.id)
    return http.HttpResponseRedirect(target)



def get_relationship_or_404(student_id, profile):
    """Get relationship between student_id and profile, or 404."""
    try:
        return model.Relationship.objects.select_related().get(
            from_profile=profile,
            to_profile_id=student_id,
            to_profile__deleted=False,
            kind=model.Relationship.KIND.elder,
            )
    except model.Relationship.DoesNotExist:
        raise http.Http404


def get_querystring_group(request, student):
    """Get optional group from querystring."""
    try:
        group_id = int(request.GET.get('group'))
        group = model.Group.objects.get(
            students=student, owner=request.user.profile, pk=group_id)
    except (ValueError, TypeError, model.Group.DoesNotExist):
        group = None
    return group



@school_staff_required
@ajax('village/_add_student_content.html')
def add_student(request, group_id=None):
    """Add a student."""
    group = get_object_or_404(model.Group, id=group_id) if group_id else None

    if request.method == 'POST':
        form = forms.AddStudentForm(
            request.POST, elder=request.user.profile, group=group)
        if form.is_valid():
            student = form.save()
            return redirect_to_village(student, group)
    else:
        form = forms.AddStudentForm(elder=request.user.profile, group=group)

    return TemplateResponse(
        request,
        'village/add_student.html',
        {
            'form': form,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/_edit_student_content.html')
def edit_student(request, student_id):
    """Edit a student."""
    rel = get_relationship_or_404(student_id, request.user.profile)
    group = get_querystring_group(request, rel.student)

    if request.method == 'POST':
        form = forms.StudentForm(
            request.POST, instance=rel.student, elder=rel.elder)
        if form.is_valid():
            student = form.save()
            return redirect_to_village(student, group)
    else:
        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

    return TemplateResponse(
        request,
        'village/edit_student.html',
        {
            'form': form,
            'student': rel.student,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/_add_group_content.html')
def add_group(request):
    """Add a group."""
    if request.method == 'POST':
        form = forms.AddGroupForm(request.POST, owner=request.user.profile)
        if form.is_valid():
            group = form.save()
            if not group.students.exists():
                return redirect('add_student_in_group', group_id=group.id)
            return redirect('group', group_id=group.id)
    else:
        form = forms.AddGroupForm(owner=request.user.profile)

    return TemplateResponse(
        request,
        'village/add_group.html',
        {
            'form': form,
            },
        )



@school_staff_required
@ajax('village/_edit_group_content.html')
def edit_group(request, group_id):
    """Edit a group."""
    group = get_object_or_404(
        model.Group.objects.select_related('owner'), pk=group_id)
    if group.owner != request.user.profile:
        raise http.Http404

    if request.method == 'POST':
        form = forms.GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            return redirect('group', group_id=group.id)
    else:
        form = forms.GroupForm(instance=group)

    return TemplateResponse(
        request,
        'village/edit_group.html',
        {
            'form': form,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/_invite_elder_content.html')
def invite_elder(request, student_id=None, group_id=None):
    """Invite new elder to a student's village or to a group."""
    if student_id:
        rel = get_relationship_or_404(student_id, request.user.profile)
        group = None
        form_kwargs = {'rel': rel}
        template_context = {
            'student': rel.student,
            'group': get_querystring_group(request, rel.student),
            }
    elif group_id:
        group = get_object_or_404(
            model.Group.objects.filter(owner=request.user.profile), id=group_id)
        rel = None
        form_kwargs = {'group': group}
        template_context = {'group': group}
    else:
        raise http.Http404

    if request.method == 'POST':
        form = forms.InviteElderForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save(request)
            if rel:
                return redirect_to_village(
                    rel.student, template_context.get('group'))
            return redirect('group', group_id=group.id)
    else:
        form = forms.InviteElderForm(**form_kwargs)

    template_context['form'] = form

    return TemplateResponse(
        request,
        'village/invite_elder.html',
        template_context,
        )



@login_required
@ajax('village/_village_content.html')
def village(request, student_id):
    """The main chat view for a student/village."""
    rel = get_relationship_or_404(student_id, request.user.profile)
    group = get_querystring_group(request, rel.student)

    return TemplateResponse(
        request,
        'village/village.html',
        {
            'student': rel.student,
            'group': group,
            'relationship': rel,
            'post_char_limit': model.post_char_limit(rel),
            },
        )



@login_required
@ajax('village/_group_content.html')
def group(request, group_id):
    """The main chat view for a group."""
    group = get_object_or_404(
        model.Group.objects.filter(
            owner=request.user.profile,
            deleted=False,
            ),
        id=group_id)

    return TemplateResponse(
        request,
        'village/group.html',
        {
            'group': group,
            'post_char_limit': model.post_char_limit(request.user.profile),
            },
        )



@login_required
@ajax('village/_group_content.html')
def all_students(request):
    """Main chat view for all-students 'group'."""
    group = model.AllStudentsGroup(request.user.profile)

    return TemplateResponse(
        request,
        'village/group.html',
        {
            'group': group,
            'post_char_limit': model.post_char_limit(request.user.profile),
            }
        )



@login_required
def json_posts(request, student_id=None, group_id=None):
    """Get backlog of up to 100 latest posts, or POST a post."""
    group = None
    rel = None
    post_model = model.BulkPost
    if student_id is not None:
        rel = get_relationship_or_404(student_id, request.user.profile)
        post_model = model.Post
        target = rel.student
        manager = rel.student.posts_in_village
    elif group_id is not None:
        group = get_object_or_404(
            model.Group.objects.filter(owner=request.user.profile), pk=group_id)
        target = group
        manager = group.bulk_posts
    else:
        target = None
        manager = request.user.profile.authored_bulkposts

    if request.method == 'POST' and 'text' in request.POST:
        text = request.POST['text']
        sequence_id = request.POST.get('author_sequence_id')
        limit = model.post_char_limit(rel or request.user.profile)
        if len(text) > limit:
            return http.HttpResponseBadRequest(
                json.dumps(
                    {
                        'error': 'Posts are limited to %s characters.' % limit,
                        'success': False,
                        }
                    ),
                content_type='application/json',
                )
        post = post_model.create(
            request.user.profile, target, text, sequence_id)

        data = {
            'success': True,
            'posts': [model.post_dict(post, author_sequence_id=sequence_id)],
            }

        return http.HttpResponse(json.dumps(data), content_type='application/json')

    data = {
        'posts':
            [
            model.post_dict(post) for post in
            reversed(
                manager.order_by('-timestamp')[:BACKLOG_POSTS])
            ],
        }

    return http.HttpResponse(json.dumps(data), content_type='application/json')


@school_staff_required
@ajax('village/_edit_elder_content.html')
def edit_elder(request, elder_id, student_id=None, group_id=None):
    """Edit a village elder."""
    elder = get_object_or_404(
        model.Profile.objects.select_related('user'), id=elder_id)
    # can't edit the profile of another school staff
    if elder.school_staff:
        raise http.Http404
    if student_id is not None:
        get_relationship_or_404(student_id, request.user.profile)
        elder_rel = get_relationship_or_404(student_id, elder)
        group = get_querystring_group(request, elder_rel.student)
    else:
        elder_rel = None
        if group_id is not None:
            group = get_object_or_404(model.Group.objects.filter(
                    owner=request.user.profile, deleted=False), pk=group_id)
        else:
            group = model.AllStudentsGroup(request.user.profile)

    if request.method == 'POST':
        form = forms.EditElderForm(
            request.POST, instance=elder, editor=request.user.profile)
        if form.is_valid():
            form.save(elder_rel)
            messages.success(request, u"Changes saved!")
            if elder_rel:
                return redirect('village', student_id=student_id)
            elif group and not group.is_all:
                return redirect('group', group_id=group.id)
            return redirect('all_students')
    else:
        form = forms.EditElderForm(instance=elder, editor=request.user.profile)

    return TemplateResponse(
        request,
        'village/edit_elder.html',
        {
            'form': form,
            'group': group,
            'student': elder_rel.student if elder_rel else None,
            'elder': elder,
            },
        )



@school_staff_required
def pdf_parent_instructions(request, lang, group_id=None):
    """Render a PDF for sending home with parents."""
    group = get_object_or_404(
        model.Group.objects.filter(
            owner=request.user.profile, id=group_id)) if group_id else None

    template_dir = os.path.dirname(os.path.abspath(pdf.__file__))
    template_path = os.path.join(
        template_dir,
        'parent-instructions-template-%s.pdf' % lang,
        )

    if not os.path.isfile(template_path):
        raise http.Http404

    response = http.HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename=instructions-%s.pdf' % lang)

    pdf.generate_instructions_pdf(
        template_path=template_path,
        stream=response,
        name=request.user.profile.name or "Your Child's Teacher",
        code=group.code if group else request.user.profile.code or '',
        phone=settings.PORTFOLIYO_SMS_DEFAULT_FROM,
        )

    return response
