"""PDF code."""
import io
import os

import pyPdf
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.pdfgen import canvas

from portfoliyo import formats



def generate_instructions_pdf(stream, code, phone):
    """Generate a parent signup instructions PDF and write it to stream."""
    template_path = os.path.join(
        os.path.dirname(__file__), 'parent-instructions-template.pdf')
    template_page = pyPdf.PdfFileReader(open(template_path, 'rb')).getPage(0)

    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=landscape(LETTER))

    p.setFont('Helvetica-Bold', 16)

    p.drawString(390, 372, code)
    p.drawString(
        380, 347, formats.display_phone(phone))
    p.drawString(438, 300, code)

    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    additions_page = pyPdf.PdfFileReader(buffer).getPage(0)
    template_page.mergePage(additions_page)

    output = pyPdf.PdfFileWriter()
    output.addPage(template_page)
    output.write(stream)

    buffer.close()
