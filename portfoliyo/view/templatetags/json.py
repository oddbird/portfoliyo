"""JSON template filter."""
from __future__ import absolute_import

from django import template
import json

register = template.Library()


@register.filter
def jsonify(obj):
    """Return JSON serialization of given object."""
    return json.dumps(obj)
