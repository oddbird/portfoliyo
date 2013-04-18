"""Rendering of handlebars templates."""
from django import template
from django.utils.safestring import mark_safe

from portfoliyo.handlebars import render


register = template.Library()


@register.filter
def handlebars(data, template_name):
    return mark_safe(unicode(render(template_name, data)))
