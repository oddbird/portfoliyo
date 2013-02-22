"""Template tags for format conversions."""
from django import template

from portfoliyo import formats


register = template.Library()



@register.filter
def display_phone(number):
    if number is not None:
        number = formats.display_phone(number)
    return number
