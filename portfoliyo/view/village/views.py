"""
Student/elder (village) views.

"""
import json

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django import http
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from portfoliyo import formats, model, pdf
from portfoliyo.view import tracking
from ..ajax import ajax
from ..decorators import school_staff_required, login_required
from . import forms


# number of posts to show in backlog
BACKLOG_POSTS = 100


@login_required
@ajax('village/_dashboard.html')
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
@ajax('village/student_form/_add_student.html')
def add_student(request, group_id=None):
    """Add a student."""
    group = get_object_or_404(model.Group, id=group_id) if group_id else None

    if request.method == 'POST':
        form = forms.AddStudentForm(
            request.POST, elder=request.user.profile, group=group)
        if form.is_valid():
            student = form.save()
            tracking.track(request, 'added student')
            return redirect_to_village(student, group)
    else:
        form = forms.AddStudentForm(elder=request.user.profile, group=group)

    return TemplateResponse(
        request,
        'village/student_form/add_student.html',
        {
            'form': form,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/bulksignup/_bulk.html')
def add_students_bulk(request, group_id=None):
    """Add students by sending home a PDF to parents."""
    group = get_object_or_404(model.Group, id=group_id) if group_id else None

    return TemplateResponse(
        request,
        'village/bulksignup/bulk.html',
        {
            'group': group,
            'code': group.code if group else request.user.profile.code,
            'pyo_phone': formats.display_phone(
                settings.PORTFOLIYO_SMS_DEFAULT_FROM),
            'group_just_created': group and request.GET.get('created', None),
            },
        )



@school_staff_required
@ajax('village/student_form/_edit_student.html')
def edit_student(request, student_id):
    """Edit a student."""
    rel = get_relationship_or_404(student_id, request.user.profile)
    group = get_querystring_group(request, rel.student)

    if request.method == 'POST':
        form = forms.StudentForm(
            request.POST, instance=rel.student, elder=rel.elder)
        if form.is_valid():
            student = form.save()
            tracking.track(request, 'edited student')
            return redirect_to_village(student, group)
    else:
        form = forms.StudentForm(instance=rel.student, elder=rel.elder)

    return TemplateResponse(
        request,
        'village/student_form/edit_student.html',
        {
            'form': form,
            'student': rel.student,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/group_form/_add_group.html')
def add_group(request):
    """Add a group."""
    if request.method == 'POST':
        form = forms.AddGroupForm(request.POST, owner=request.user.profile)
        if form.is_valid():
            group = form.save()
            tracking.track(request, 'added group')
            if not group.students.exists():
                return redirect(
                    reverse('add_students_bulk', kwargs={'group_id': group.id})
                    + '?created=1')
            return redirect('group', group_id=group.id)
    else:
        form = forms.AddGroupForm(owner=request.user.profile)

    return TemplateResponse(
        request,
        'village/group_form/add_group.html',
        {
            'form': form,
            },
        )



@school_staff_required
@ajax('village/group_form/_edit_group.html')
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
            tracking.track(request, 'edited group')
            return redirect('group', group_id=group.id)
    else:
        form = forms.GroupForm(instance=group)

    return TemplateResponse(
        request,
        'village/group_form/edit_group.html',
        {
            'form': form,
            'group': group,
            },
        )



@school_staff_required
@ajax('village/invite_elder/_family.html')
def invite_family(request, student_id):
    """Invite family member to a student's village."""
    rel = get_relationship_or_404(student_id, request.user.profile)
    group = get_querystring_group(request, rel.student)

    if request.method == 'POST':
        form = forms.InviteFamilyForm(request.POST, rel=rel)
        if form.is_valid():
            form.save()
            tracking.track(request, 'invited family')
            return redirect_to_village(rel.student, group)
    else:
        phone = request.GET.get('phone', None)
        initial = {}
        if phone is not None:
            initial['phone'] = phone
        form = forms.InviteFamilyForm(initial=initial, rel=rel)

    return TemplateResponse(
        request,
        'village/invite_elder/family.html',
        {
            'group': group,
            'student': rel.student,
            'inviter': model.elder_in_context(rel),
            'form': form,
            },
        )



@school_staff_required
@ajax('village/invite_elder/_teacher.html')
def invite_teacher(request, student_id):
    """Invite teacher to a student's village."""
    rel = get_relationship_or_404(student_id, request.user.profile)
    group = get_querystring_group(request, rel.student)

    if request.method == 'POST':
        form = forms.InviteTeacherForm(request.POST, rel=rel)
        if form.is_valid():
            teacher = form.save()
            tracking.track(
                request,
                'invited teacher',
                invitedEmail=teacher.user.email,
                studentId=student_id,
                )
            return redirect_to_village(rel.student, group)
    else:
        form = forms.InviteTeacherForm(rel=rel)

    return TemplateResponse(
        request,
        'village/invite_elder/teacher.html',
        {'group': group, 'student': rel.student, 'form': form},
        )



@school_staff_required
@ajax('village/invite_elder/_teacher_to_group.html')
def invite_teacher_to_group(request, group_id):
    """Invite teacher to a group."""
    group = get_object_or_404(
        model.Group.objects.filter(owner=request.user.profile), id=group_id)

    if request.method == 'POST':
        form = forms.InviteTeacherForm(request.POST, group=group)
        if form.is_valid():
            teacher = form.save()
            tracking.track(
                request,
                'invited teacher to group',
                invitedEmail=teacher.user.email,
                groupId=group_id,
                )
            return redirect('group', group_id=group.id)
    else:
        form = forms.InviteTeacherForm(group=group)

    return TemplateResponse(
        request,
        'village/invite_elder/teacher_to_group.html',
        {'group': group, 'form': form},
        )



@login_required
@ajax('village/post_list/_village.html')
def village(request, student_id):
    """The main chat view for a student/village."""
    try:
        rel = get_relationship_or_404(student_id, request.user.profile)
    except http.Http404:
        if not request.user.is_superuser:
            raise
        rel = None
        student = get_object_or_404(model.Profile, pk=student_id)
    else:
        student = rel.student

    group = get_querystring_group(request, student)

    return TemplateResponse(
        request,
        'village/post_list/village.html',
        {
            'student': student,
            'group': group,
            'relationship': rel,
            'sms_elders': model.sms_eligible(
                model.contextualized_elders(student.elder_relationships)),
            'read_only': rel is None,
            'post_char_limit': model.post_char_limit(rel) if rel else 0,
            },
        )



@login_required
@ajax('village/post_list/_group.html')
def group(request, group_id=None):
    """The main chat view for a group."""
    if group_id is None:
        group = model.AllStudentsGroup(request.user.profile)
    else:
        group = get_object_or_404(
            model.Group.objects.filter(owner=request.user.profile),
            id=group_id,
            )

    return TemplateResponse(
        request,
        'village/post_list/group.html',
        {
            'group': group,
            'sms_elders': model.sms_eligible(
                model.contextualized_elders(group.all_elders)),
            'post_char_limit': model.post_char_limit(request.user.profile),
            },
        )



@login_required
def json_posts(request, student_id=None, group_id=None):
    """Get backlog of up to 100 latest posts, or POST a post."""
    group = None
    rel = None
    post_model = model.BulkPost
    if student_id is not None:
        try:
            rel = get_relationship_or_404(student_id, request.user.profile)
        except http.Http404:
            if not request.user.is_superuser:
                raise
            student = get_object_or_404(model.Profile, pk=student_id)
        else:
            student = rel.student
        post_model = model.Post
        target = student
        manager = student.posts_in_village
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
        sms_profile_ids = request.POST.getlist('sms-target')
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
            request.user.profile,
            target,
            text,
            sms_profile_ids=sms_profile_ids,
            sequence_id=sequence_id,
            )

        data = {
            'success': True,
            'posts': [
                model.post_dict(
                    post, author_sequence_id=sequence_id, unread=False)
                ],
            }

        return http.HttpResponse(
            json.dumps(data), content_type='application/json')

    data = {
        'posts':
            [
            model.post_dict(
                post,
                unread=model.unread.is_unread(
                    post,
                    request.user.profile
                    ) if (post_model is model.Post) else False,
                )
            for post in reversed(
                manager.order_by('-timestamp')[:BACKLOG_POSTS])
            ],
        }

    if rel:
        model.unread.mark_village_read(rel.student, rel.elder)

    return http.HttpResponse(json.dumps(data), content_type='application/json')



@login_required
@require_POST
def mark_post_read(request, post_id):
    post = get_object_or_404(model.Post, pk=post_id)
    model.unread.mark_read(post, request.user.profile)
    return http.HttpResponse(status=202)



@school_staff_required
@ajax('village/elder_form/_edit_elder.html')
def edit_elder(request, elder_id, student_id=None, group_id=None):
    """Edit a village elder."""
    elder = get_object_or_404(
        model.Profile.objects.select_related('user'), id=elder_id)
    # can't edit the profile of another school staff
    if elder.school_staff:
        raise http.Http404
    if student_id is not None:
        teacher_rel = get_relationship_or_404(student_id, request.user.profile)
        editor = model.elder_in_context(teacher_rel)
        elder_rel = get_relationship_or_404(student_id, elder)
        elder = model.elder_in_context(elder_rel)
        group = get_querystring_group(request, elder_rel.student)
    else:
        elder_rel = None
        editor = request.user.profile
        if group_id is not None:
            group = get_object_or_404(model.Group.objects.filter(
                    owner=request.user.profile), pk=group_id)
        else:
            group = model.AllStudentsGroup(request.user.profile)

    if request.method == 'POST':
        form = forms.EditElderForm(request.POST, instance=elder, rel=elder_rel)
        if form.is_valid():
            form.save(editor=editor)
            messages.success(request, u"Changes saved!")
            if elder_rel:
                return redirect('village', student_id=student_id)
            elif group and not group.is_all:
                return redirect('group', group_id=group.id)
            return redirect('all_students')
    else:
        form = forms.EditElderForm(instance=elder, rel=elder_rel)

    return TemplateResponse(
        request,
        'village/elder_form/edit_elder.html',
        {
            'form': form,
            'group': group,
            'student': elder_rel.student if elder_rel else None,
            'inviter': editor,
            'elder': elder,
            },
        )



@school_staff_required
def pdf_parent_instructions(request, lang, group_id=None):
    """Render a PDF for sending home with parents."""
    group = get_object_or_404(
        model.Group.objects.filter(
            owner=request.user.profile, id=group_id)) if group_id else None

    lang_verbose = dict(settings.LANGUAGES).get(lang, lang)

    filename = "Portfoliyo {0}{1}.pdf".format(
            lang_verbose,
            " - {0}".format(group.name) if group else "",
            )

    response = http.HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    pdf.generate_instructions_pdf(
        stream=response,
        lang=lang,
        name=request.user.profile.name or "Your Child's Teacher",
        code=group.code if group else request.user.profile.code or '',
        phone=settings.PORTFOLIYO_SMS_DEFAULT_FROM,
        group=group,
        )

    tracking.track(request, 'downloaded signup pdf', language=lang)

    return response
