"""Compiled handlebars templates."""
import os
import re

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


operators = {
    re.compile(r'^==$'): lambda l, r: l == r,
    re.compile(r'^!=$'): lambda l, r: l != r,
    re.compile(r'^IS$|^===$'): lambda l, r: l == r,
    re.compile(r'^NOT$|^IS NOT$|^!==$|^!$'): lambda l, r: l != r,
    re.compile(r'^OR$|^\|\|$'): lambda l, r: l or r,
    re.compile(r'^AND$|^&&$'): lambda l, r: l and r,
    re.compile(r'^MOD$|^%$'): lambda l, r: l % r,
    re.compile(r'^<$'): lambda l, r: l < r,
    re.compile(r'^>$'): lambda l, r: l > r,
    re.compile(r'^<=$'): lambda l, r: l <= r,
    re.compile(r'^>=$'): lambda l, r: l >= r,
    re.compile(r'^IN$|^E$'): lambda l, r: l in r,
}


def iff(this, options, *args, **kwargs):
    left = args[0]
    operator = '==='

    if len(args) == 1:
        right = True
    elif len(args) == 2:
        right = args[1]
    elif len(args) == 3:
        operator = args[1]
        right = args[2]

    if not kwargs.get('case', True):
        left = unicode(left).lower()
        right = unicode(right).lower()

    for op_re, func in operators.items():
        if op_re.match(operator):
            if func(left, right):
                return options['fn'](this)
            else:
                return options['inverse'](this)

    raise ValueError(
        "Handlebars helper 'iff' doesn't know the operator %s" % operator)



helpers = {
    u'join': join,
    u'plural': plural,
    u'iff': iff,
    }


compiler = pybars.Compiler()


def _compile(template_name):
    template_path = os.path.join(
        JSTEMPLATES_PATH, '%s.handlebars' % template_name)
    with open(template_path) as fh:
        return compiler.compile(fh.read().decode('utf-8'))


templates = {
    'posts': _compile('posts'),
    }


def render(template_name, context):
    return templates[template_name](context, helpers=helpers)
