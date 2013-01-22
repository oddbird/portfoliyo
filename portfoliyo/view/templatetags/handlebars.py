"""Rendering of handlebars templates."""
from django import template
from django.utils.safestring import mark_safe

from portfoliyo.handlebars import templates


register = template.Library()


@register.filter
def handlebars(data, template_name):
    template = templates[template_name]
    return mark_safe(unicode(template(data)))
