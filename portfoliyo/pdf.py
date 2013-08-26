"""PDF code."""
import io
import os

from django.conf import settings
from django.template.loader import render_to_string
import pyPdf
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from portfoliyo import formats


# Each tuple consists of ((x, y), font, font-size, wrap-width)
# If wrap-width is None, do not wrap.
SECTIONS = {
    'header': ((350, 510), 'Helvetica-Bold', 30, 350),
    'phone_label': ((370, 450), 'Helvetica', 20, None),
    'phone': ((370, 405), 'Helvetica-Bold', 36, None),
    'code_label': ((370, 320), 'Helvetica', 20, None),
    'code': ((370, 275), 'Helvetica-Bold', 36, None),
    'sample_to_label': ((120, 450), 'Helvetica', 20, None),
    'sample_to': ((135, 405), 'Helvetica-Bold', 20, None),
    'sample_message_label': ((120, 350), 'Helvetica', 20, None),
    'sample_message': ((135, 305), 'Helvetica-Bold', 20, None),
    'note': ((350, 160), 'Helvetica', 12, 350),
    'signature': ((350, 125), 'Helvetica', 12, None),
    'date': ((350, 105), 'Helvetica', 12, None),
    'footer': ((350, 65), 'Helvetica-Oblique', 10, 350),
    'group': ((75, 50), 'Helvetica', 10, None),
    }


COLOR = (7, 54, 66)


TEXT_TEMPLATES_BASE = 'village/student_form/bulksheet/'



def get_text(lang, name):
    """Get text for a given named section of PDF in given language."""
    path = '%s%s/%s.txt' % (TEXT_TEMPLATES_BASE, lang, name)
    return render_to_string(path).replace('\n', ' ').strip()



def generate_instructions_pdf(stream, lang, name, code, phone, group=None):
    """Generate a parent signup instructions PDF and write it to stream."""
    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(
        template_dir,
        'parent-instructions-template.pdf',
        )

    display_phone = formats.display_phone(phone)

    if lang != settings.LANGUAGE_CODE:
        code += " " + lang

    code = code.lower()

    sections = {
        'header': '%s %s' % (get_text(lang, 'action'), name),
        'phone_label': get_text(lang, 'phone_label'),
        'phone': display_phone,
        'code_label': get_text(lang, 'code_label'),
        'code': code,
        'sample_to_label': 'To: ',
        'sample_to': display_phone,
        'sample_message_label': 'Message: ',
        'sample_message': code,
        'note': get_text(lang, 'note'),
        'signature': get_text(lang, 'signature'),
        'date': get_text(lang, 'date'),
        'footer': get_text(lang, 'footer'),
        }

    if group:
        sections['group'] = unicode(group)

    template_page = pyPdf.PdfFileReader(open(template_path, 'rb')).getPage(0)

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=landscape(LETTER))
    text_color = Color(*[color/255.0 for color in COLOR])

    for name, text in sections.items():
        coords, fontname, fontsize, wrap = SECTIONS[name]
        style = ParagraphStyle(
            name=name,
            fontName=fontname,
            fontSize=fontsize,
            textColor=text_color,
            leading=fontsize + 4,
            )
        p = Paragraph(text, style=style)
        p.wrapOn(c, wrap or 600, 600)
        p.drawOn(c, coords[0], coords[1])

    c.showPage()
    c.save()

    # Get the value of the BytesIO buffer and write it to the response.
    additions_page = pyPdf.PdfFileReader(buffer).getPage(0)
    template_page.mergePage(additions_page)

    output = pyPdf.PdfFileWriter()
    output.addPage(template_page)
    output.write(stream)

    buffer.close()
