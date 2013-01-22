"""Compiled handlebars templates."""
import os

from django.conf import settings
import pybars


compiler = pybars.Compiler()


JSTEMPLATES_PATH = os.path.join(settings.BASE_PATH, 'jstemplates')


def _compile(template_name):
    template_path = os.path.join(
        JSTEMPLATES_PATH, '%s.handlebars' % template_name)
    with open(template_path) as fh:
        return compiler.compile(fh.read().decode('utf-8'))


templates = {
    'posts': _compile('posts'),
    }
