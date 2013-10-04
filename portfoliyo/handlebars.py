"""Compiled handlebars templates."""
import os

from django.conf import settings
import pybars


JSTEMPLATES_PATH = os.path.join(settings.BASE_PATH, 'jstemplates')


# helpers

def join(this, ary, joiner):
    return joiner.join(ary)


def plural(this, options, ary):
    if len(ary) == 1:
        return options['inverse'](this)
    return options['fn'](this)


helpers = {
    u'join': join,
    u'plural': plural,
    }


compiler = pybars.Compiler()


def _compile(template_name):
    template_path = os.path.join(
        JSTEMPLATES_PATH, '%s.hbs' % template_name)
    with open(template_path) as fh:
        return compiler.compile(fh.read().decode('utf-8'))


templates = {
    'posts': _compile('posts'),
    }


def render(template_name, context):
    return templates[template_name](context, helpers=helpers)
