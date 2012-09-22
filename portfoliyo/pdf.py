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
        'code': (358, 225),
        'phone': (342, 207),
        'example': (386, 171),
        },
    'parent-instructions-template-es.pdf': {
        'code': (370, 189),
        'phone': (345, 171),
        'example': (386, 135),
        },
    }


COLOR = (7, 54, 66)



def generate_instructions_pdf(template_path, stream, code, phone):
    """Generate a parent signup instructions PDF and write it to stream."""
    template_page = pyPdf.PdfFileReader(open(template_path, 'rb')).getPage(0)

    # font_path = os.path.join(
    #     os.path.dirname(os.path.abspath(__file__)),
    #     'cambridge_round_bold.ttf',
    #     )

    # pdfmetrics.registerFont(TTFont('Cambridge-Round-Bold', font_path))
    # addMapping('Cambridge-Round-Bold', 0, 0, 'Cambridge-Round-Bold')

    locations = LOCATIONS[os.path.basename(template_path)]
    code_loc = locations['code']
    phone_loc = locations['phone']
    example_loc = locations['example']

    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=landscape(LETTER))

    p.setFont('Helvetica-Bold', 11)
    p.setFillColorRGB(*[c/255.0 for c in COLOR])

    p.drawString(code_loc[0], code_loc[1], code)
    p.drawString(
        phone_loc[0], phone_loc[1], formats.display_phone(phone))
    p.drawString(example_loc[0], example_loc[1], '%s Jane Doe' % code)

    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    additions_page = pyPdf.PdfFileReader(buffer).getPage(0)
    template_page.mergePage(additions_page)

    output = pyPdf.PdfFileWriter()
    output.addPage(template_page)
    output.write(stream)

    buffer.close()
