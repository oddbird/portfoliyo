"""Tests for handlebars helpers."""
from portfoliyo import handlebars


def render(tpl, context):
    return unicode(tpl(context, helpers=handlebars.helpers))


def test_join():
    tpl = handlebars.compiler.compile(u'{{{join ary ", "}}}')
    assert render(tpl, {'ary': ['a', 'b']}) == u'a, b'



def test_plural():
    tpl = handlebars.compiler.compile(u'{{#plural ary}}s{{/plural}}')
    assert render(tpl, {'ary': ['a', 'b']}) == u's'


def test_not_plural():
    tpl = handlebars.compiler.compile(u'{{#plural ary}}s{{/plural}}')
    assert render(tpl, {'ary': ['a']}) == u''


def test_zero_is_plural():
    tpl = handlebars.compiler.compile(u'{{#plural ary}}s{{/plural}}')
    assert render(tpl, {'ary': []}) == u's'
