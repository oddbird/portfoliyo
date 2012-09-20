"""Tests for PDF generation."""
import io

from portfoliyo import pdf



def test_generate_instructions_pdf():
    """Smoke test - writes to the stream and doesn't blow up."""
    stream = io.BytesIO()
    pdf.generate_instructions_pdf(stream, code='ABCDEF', phone='+3214567890')
    stream.close()
