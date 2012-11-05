"""Tests for PDF generation."""
import io
import os

from portfoliyo import pdf

from portfoliyo.tests import factories



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
        group=factories.GroupFactory.build(name='Group'),
        )
    stream.close()



def test_generate_instructions_pdf_no_group():
    """Can omit group argument."""
    stream = io.BytesIO()
    template_path = os.path.join(
        os.path.dirname(pdf.__file__), 'parent-instructions-template-es.pdf')
    pdf.generate_instructions_pdf(
        template_path,
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        )
    stream.close()



def test_generate_instructions_pdf_unicode_group():
    """Group can have unicode name."""
    stream = io.BytesIO()
    template_path = os.path.join(
        os.path.dirname(pdf.__file__), 'parent-instructions-template-en.pdf')
    pdf.generate_instructions_pdf(
        template_path,
        stream,
        name='John Doe',
        code='ABCDEF',
        phone='+3214567890',
        group=factories.GroupFactory.build(name=u'Grúpo'),
        )
    stream.close()
