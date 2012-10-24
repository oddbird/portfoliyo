"""Template tags and filters for announcements."""
from django import template

from portfoliyo.announce import models as announce


register = template.Library()



@register.filter
def unread_announcements(profile):
    return announce.get_unread(profile)
