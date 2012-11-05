"""PDF code."""
import io
import os

import pyPdf
# from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import LETTER, landscape
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from portfoliyo import formats



LOCATIONS = {
    'parent-instructions-template-en.pdf': {
        'name': (408, 505),
        'code': (356, 224),
        'phone': (456, 224),
        'sample_to': (145, 470),
        'sample_message_label': (145, 440),
        'sample_message': (145, 420),
        'group': (620, 80),
        },
    'parent-instructions-template-es.pdf': {
        'name': (424, 505),
        'code': (370, 170),
        'phone': (470, 170),
        'sample_to': (145, 470),
        'sample_message_label': (145, 440),
        'sample_message': (145, 420),
        'group': (620, 80),
        },
    }


COLOR = (7, 54, 66)



def draw(canvas, location, text):
    """Draw ``text`` on ``canvas`` at ``location`` (x, y) tuple."""
    canvas.drawString(location[0], location[1], text)



def generate_instructions_pdf(template_path, stream, name, code, phone,
                              group=None):
    """Generate a parent signup instructions PDF and write it to stream."""
    template_page = pyPdf.PdfFileReader(open(template_path, 'rb')).getPage(0)

    # font_path = os.path.join(
    #     os.path.dirname(os.path.abspath(__file__)),
    #     'cambridge_round_bold.ttf',
    #     )

    # pdfmetrics.registerFont(TTFont('Cambridge-Round-Bold', font_path))
    # addMapping('Cambridge-Round-Bold', 0, 0, 'Cambridge-Round-Bold')

    locations = LOCATIONS[os.path.basename(template_path)]
    display_phone = formats.display_phone(phone)

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=landscape(LETTER))
    c.setFillColorRGB(*[color/255.0 for color in COLOR])

    c.setFont('Helvetica-Bold', 36)
    draw(c, locations['name'], name)

    if group:
        c.setFont('Helvetica-Bold', 9)
        draw(c, locations['group'], unicode(group))

    c.setFont('Helvetica-Bold', 9)

    draw(c, locations['sample_to'], 'To: %s' % display_phone)
    draw(c, locations['sample_message_label'], 'Message:')
    draw(c, locations['sample_message'], code)

    c.setFont('Helvetica-Bold', 12)

    draw(c, locations['code'], code)
    draw(c, locations['phone'], display_phone)

    c.showPage()
    c.save()

    # Get the value of the BytesIO buffer and write it to the response.
    additions_page = pyPdf.PdfFileReader(buffer).getPage(0)
    template_page.mergePage(additions_page)

    output = pyPdf.PdfFileWriter()
    output.addPage(template_page)
    output.write(stream)

    buffer.close()
