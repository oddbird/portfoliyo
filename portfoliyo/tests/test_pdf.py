"""Tests for PDF generation."""
import io
import os

from portfoliyo import pdf



def test_generate_instructions_pdf():
    """Smoke test - writes to the stream and doesn't blow up."""
    stream = io.BytesIO()
    template_path = os.path.join(
        os.path.dirname(pdf.__file__), 'parent-instructions-template-en.pdf')
    pdf.generate_instructions_pdf(
        template_path,
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        )
    stream.close()
