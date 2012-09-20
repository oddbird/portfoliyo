"""
Student/elder (village) views.

"""
import io
import json
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
import pyPdf
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.pdfgen import canvas

from portfoliyo import model, formats
from ..decorators import school_staff_required
from ..ajax import ajax
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


def get_relationship_or_404(student_id, profile):
    """Get relationship between student_id and profile, or 404."""
    try:
        return model.Relationship.objects.select_related().get(
            from_profile=profile,
            to_profile_id=student_id,
            kind=model.Relationship.KIND.elder,
            )
    except model.Relationship.DoesNotExist:
        raise Http404



@school_staff_required
@ajax('village/_invite_elders_content.html')
def invite_elders(request, student_id):
    """Invite new elder(s) to a student's village."""
    rel = get_relationship_or_404(student_id, request.user.profile)

    if request.method == 'POST':
        formset = forms.InviteEldersFormSet(request.POST, prefix='elders')
        if formset.is_valid():
            formset.save(request, rel)
            return redirect('village', student_id=rel.student.id)
    else:
        formset = forms.InviteEldersFormSet(prefix='elders')

    return TemplateResponse(
        request,
        'village/invite_elders.html',
        {'elders_formset': formset, 'student': rel.student},
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
            'relationship': rel,
            'post_char_limit': model.post_char_limit(rel),
            'elders_formset': forms.InviteEldersFormSet(prefix='elders'),
            },
        )



@login_required
def json_posts(request, student_id):
    """Get backlog of up to 100 latest posts, or POST a post."""
    rel = get_relationship_or_404(student_id, request.user.profile)

    if request.method == 'POST' and 'text' in request.POST:
        text = request.POST['text']
        sequence_id = request.POST.get('author_sequence_id')
        limit = model.post_char_limit(rel)
        if len(text) > limit:
            return HttpResponseBadRequest(
                json.dumps(
                    {
                        'error': 'Posts are limited to %s characters.' % limit,
                        'success': False,
                        }
                    ),
                content_type='application/json',
                )
        post = model.Post.create(
            request.user.profile, rel.student, text, sequence_id)

        data = {
            'success': True,
            'posts': [post.json_data(author_sequence_id=sequence_id)],
            }

        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {
        'posts':
            [
            post.json_data() for post in
            reversed(
                rel.student.posts_in_village.order_by(
                    '-timestamp')[:BACKLOG_POSTS]
                )
            ],
        }

    return HttpResponse(json.dumps(data), content_type='application/json')



@school_staff_required
def pdf_parent_instructions(request):
    """Render a PDF for sending home with parents."""
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=instructions.pdf'

    template_path = os.path.join(
        os.path.dirname(__file__), 'parent-instructions-template.pdf')
    template_page = pyPdf.PdfFileReader(open(template_path, 'rb')).getPage(0)

    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=landscape(LETTER))

    p.setFont('Helvetica-Bold', 16)

    p.drawString(390, 372, request.user.profile.code)
    p.drawString(
        380, 347, formats.display_phone(settings.PORTFOLIYO_SMS_DEFAULT_FROM))
    p.drawString(438, 300, request.user.profile.code)

    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    additions_page = pyPdf.PdfFileReader(buffer).getPage(0)
    template_page.mergePage(additions_page)

    output = pyPdf.PdfFileWriter()
    output.addPage(template_page)
    output.write(response)

    buffer.close()

    return response
