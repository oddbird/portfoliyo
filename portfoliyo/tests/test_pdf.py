"""Tests for PDF generation."""
import io

from portfoliyo import pdf

from portfoliyo.tests import factories



def test_generate_instructions_pdf():
    """Smoke test - writes to the stream and doesn't blow up."""
    stream = io.BytesIO()
    pdf.generate_instructions_pdf(
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        group=factories.GroupFactory.build(name='Group'),
        )
    stream.close()



def test_generate_instructions_pdf_no_group():
    """Can omit group argument."""
    stream = io.BytesIO()
    pdf.generate_instructions_pdf(
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        )
    stream.close()



def test_generate_instructions_pdf_unicode_group():
    """Group can have unicode name."""
    stream = io.BytesIO()
    pdf.generate_instructions_pdf(
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        group=factories.GroupFactory.build(name=u'Grúpo'),
        )
    stream.close()
