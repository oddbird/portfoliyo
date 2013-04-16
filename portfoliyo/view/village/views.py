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
from unidecode import unidecode

from portfoliyo import formats, model, pdf, serializers, xact
from portfoliyo.view import tracking
from .. import home
from ..ajax import ajax
from ..decorators import school_staff_required, login_required
from . import forms


# number of posts to show in backlog
BACKLOG_POSTS = 15


@login_required
@ajax('village/_dashboard.html')
def dashboard(request, group_id=None):
    """Group dashboard."""
    if group_id is None:
        group = model.AllStudentsGroup(request.user.profile)
    else:
        group = get_object_or_404(
            model.Group.objects.filter(owner=request.user.profile),
            id=group_id,
            )

    return TemplateResponse(
        request,
        'village/dashboard.html',
        {
            'group': group,
            'elders': model.contextualized_elders(
                group.all_elders).order_by('school_staff', 'name'),
            'student_count': group.students.count(),
            'teacher_count': group.all_elders.filter(school_staff=True).count(),
            'family_count': group.all_elders.filter(school_staff=False).count(),
            },
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
            with xact.xact():
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
            'code': group.code if group else request.user.profile.code,
            'default_lang_code': settings.LANGUAGE_CODE,
            'pyo_phone': formats.display_phone(
                request.user.profile.source_phone),
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
        if request.POST.get('remove', False):
            with xact.xact():
                rel.delete()
            messages.success(request, "Student '%s' removed." % rel.student)
            if group:
                return redirect('group', group_id=group.id)
            else:
                return redirect('all_students')
        form = forms.StudentForm(
            request.POST, instance=rel.student, elder=rel.elder)
        if form.is_valid():
            with xact.xact():
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
            with xact.xact():
                group = form.save()
            tracking.track(request, 'added group')
            if not group.students.exists():
                return redirect(
                    reverse('add_student', kwargs={'group_id': group.id})
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
        if request.POST.get('remove', False):
            with xact.xact():
                group.delete()
            messages.success(request, "Group '%s' removed." % group)
            return redirect(home.redirect_home(request.user))
        form = forms.GroupForm(request.POST, instance=group)
        if form.is_valid():
            with xact.xact():
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
            with xact.xact():
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
            'elders': model.contextualized_elders(
                rel.student.elder_relationships).order_by(
                'school_staff', 'name'),
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
            with xact.xact():
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
        {
            'group': group,
            'student': rel.student,
            'form': form,
            'elders': model.contextualized_elders(
                rel.student.elder_relationships).order_by(
                'school_staff', 'name'),
            },
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
            with xact.xact():
                teacher = form.save()
            tracking.track(
                request,
                'invited teacher',
                invitedEmail=teacher.user.email,
                groupId=group_id,
                )
            return redirect('group', group_id=group.id)
    else:
        form = forms.InviteTeacherForm(group=group)

    return TemplateResponse(
        request,
        'village/invite_elder/teacher_to_group.html',
        {
            'group': group,
            'form': form,
            'elders': model.contextualized_elders(
                group.all_elders).order_by('school_staff', 'name'),
            },
        )


def _get_posts(profile, student=None, group=None):
    """
    Return post data for handlebars posts.html template render.

    Get all posts for given student/group; list them as read/unread by given
    ``profile``.

    """
    all_unread = set()
    if student:
        all_unread = model.unread.all_unread(student, profile)
        queryset = student.posts_in_village.select_related(
            'author__user', 'student', 'relationship').prefetch_related(
            'attachments')
    elif group:
        if group.is_all:
            queryset = profile.authored_bulkposts.filter(
                group=None).select_related('author__user')
        else:
            queryset = group.bulk_posts.select_related('author__user')
    else:
        queryset = None

    post_data = []
    count = 0
    if queryset is not None:
        count = queryset.count()
        post_data = [
            serializers.post2dict(
                post,
                unread=str(post.id) in all_unread,
                mine=post.author == profile,
                )
            for post in reversed(
                queryset.order_by(
                    '-timestamp')[:BACKLOG_POSTS])
            ]

    return {
        'objects': post_data,
        'meta': {
            'total_count': count,
            'limit': BACKLOG_POSTS,
            'more': count > BACKLOG_POSTS,
            },
        }



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

    posts = _get_posts(request.user.profile, student=student)

    if rel and not request.impersonating:
        model.unread.mark_village_read(rel.student, rel.elder)

    return TemplateResponse(
        request,
        'village/post_list/village.html',
        {
            'student': student,
            'group': group,
            'relationship': rel,
            'elders': model.contextualized_elders(
                student.elder_relationships).order_by('school_staff', 'name'),
            'read_only': rel is None,
            'posts': posts,
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
            'elders': model.contextualized_elders(
                group.all_elders).order_by('school_staff', 'name'),
            'posts': _get_posts(request.user.profile, group=group),
            'post_char_limit': model.post_char_limit(request.user.profile),
            },
        )



# @@@ This should be integrated into the API
@login_required
@require_POST
def create_post(request, student_id=None, group_id=None):
    """
    Create a post.

    If ``student_id`` is provided in the URL, the post will be a single-village
    post. If ``group_id`` is provided, it will be a group bulk post. If neither
    is provided, it will be an all-students bulk post.

    POST parameters accepted:

    ``text``

        The text of the post to create. Must be few enough characters that,
        when the user's auto-signature is appended, the resulting full SMS
        message is <160 characters.

    ``type``

        The type of post to create: "message", "note", "call", or
        "meeting". This parameter is ignored for bulk posts; all bulk posts are
        of type "message".

    ``elder``

        A list of elder IDs connected with this post. For a "message" type
        post, these users will receive the post via SMS. For a "meeting" or
        "call" type post, these are the users who were present on the call or
        at the meeting.

    ``extra_name``

       A list of additional names connected with this post. (For instance, for
       a "meeting" or "call" type post, these are names of additional people
       present at the meeting or on the call, who are not actually elders in
       the village.)

    ``author_sequence_id``

       An increasing numeric ID for posts authored by this user in this browser
       session. This value is opaque to the server and not stored anywhere, but
       is round-tripped through Pusher back to the client, to simplify
       matching up post data and avoid creating duplicates on the client.

    For non-bulk posts, an ``attachment`` file-upload parameter is also
    optionally accepted.

    Returns JSON object with boolean key ``success``. If ``success`` is
    ``False``, a human-readable message will be provided in the ``error``
    key. If ``success`` is ``True``, the ``objects`` key will be a list
    containing one JSON-serialized post object. (Even though this view will
    only ever return one post, it still returns a list for better compatibility
    with other client-side JSON-handling code.)

    """
    if 'text' not in request.POST:
        return http.HttpResponseBadRequest(
            json.dumps(
                {
                    'error': "Must provide a 'text' querystring parameter.",
                    'success': False,
                    }
                ),
            content_type='application/json',
            )

    extra_kwargs = {}
    group = None
    rel = None
    post_model = model.BulkPost
    profile_ids = 'all'
    if student_id is not None:
        rel = get_relationship_or_404(student_id, request.user.profile)
        post_model = model.Post
        target = rel.student
        profile_ids = request.POST.getlist('elder')
        extra_kwargs['extra_names'] = request.POST.getlist('extra_name')
        extra_kwargs['post_type'] = request.POST.get('type')
        if 'attachment' in request.FILES:
            extra_kwargs['attachments'] = request.FILES.getlist('attachment')
        redirect_url = reverse('village', kwargs={'student_id': student_id})
    elif group_id is not None:
        group = get_object_or_404(
            model.Group.objects.filter(owner=request.user.profile), pk=group_id)
        target = group
        redirect_url = reverse('group', kwargs={'group_id': group_id})
    else:
        target = None
        redirect_url = reverse('all_students')

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

    with xact.xact():
        post = post_model.create(
            request.user.profile,
            target,
            text,
            profile_ids=profile_ids,
            sequence_id=sequence_id,
            **extra_kwargs)

    if request.is_ajax():
        data = {
            'success': True,
            'objects': [
                serializers.post2dict(
                    post, author_sequence_id=sequence_id, unread=False, mine=True)
                ],
            }

        return http.HttpResponse(
            json.dumps(data), content_type='application/json')
    else:
        return http.HttpResponseRedirect(redirect_url)



@login_required
@require_POST
def mark_post_read(request, post_id):
    if not request.impersonating:
        post = get_object_or_404(model.Post, pk=post_id)
        model.unread.mark_read(post, request.user.profile)
    return http.HttpResponse(
        json.dumps({'success': True}), content_type='application/json')



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
        all_elders = elder_rel.student.elder_relationships
        group = get_querystring_group(request, elder_rel.student)
    else:
        elder_rel = None
        editor = request.user.profile
        if group_id is not None:
            group = get_object_or_404(model.Group.objects.filter(
                    owner=request.user.profile), pk=group_id)
        else:
            group = model.AllStudentsGroup(request.user.profile)
        all_elders = group.all_elders

    if request.method == 'POST':
        form = forms.EditFamilyForm(request.POST, instance=elder, rel=elder_rel)
        success = False
        if elder_rel and request.POST.get('remove', False):
            with xact.xact():
                elder_rel.delete()
            success = True
        elif form.is_valid():
            with xact.xact():
                form.save(editor=editor)
            messages.success(request, u"Changes saved!")
            success = True
        if success:
            if elder_rel:
                return redirect('village', student_id=student_id)
            elif group and not group.is_all:
                return redirect('group', group_id=group.id)
            return redirect('all_students')
    else:
        form = forms.EditFamilyForm(instance=elder, rel=elder_rel)

    return TemplateResponse(
        request,
        'village/elder_form/edit_elder.html',
        {
            'form': form,
            'group': group,
            'student': elder_rel.student if elder_rel else None,
            'inviter': editor,
            'elder': elder,
            'elders': model.contextualized_elders(
                all_elders).order_by('school_staff', 'name'),
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
            " - {0}".format(unidecode(group.name)) if group else u"",
            )

    response = http.HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="%s"' % filename.encode('utf-8'))

    pdf.generate_instructions_pdf(
        stream=response,
        lang=lang,
        name=request.user.profile.name or "Your Child's Teacher",
        code=group.code if group else request.user.profile.code or '',
        phone=request.user.profile.source_phone,
        group=group,
        )

    tracking.track(request, 'downloaded signup pdf', language=lang)

    return response
