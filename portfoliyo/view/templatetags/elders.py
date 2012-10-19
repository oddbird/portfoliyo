"""Template tags for the list of village elders."""
from django import template

from portfoliyo import model


register = template.Library()


@register.filter
def elder_status(elder, current):
    """Return short CSS class describing this elder's status."""
    status = ''
    if elder.declined:
        status = 'declined'
    elif not elder.user.is_active:
        status = 'inactive'
    elif elder.phone:
        status = 'mobile'
    elif elder != current:
        status = 'offline' # @@@ this should use Pusher presence-detection
    return status


@register.filter
def elder_status_description(elder, current):
    """Return human-readable tooltip description of this elder's status."""
    desc = ''
    if elder == current:
        desc = 'This is you!'
    elif elder.declined:
        desc = '%s has declined to receive SMS notifications.' % elder
    elif not elder.user.is_active:
        desc = '%s is inactive and will not receive SMS notifications.' % elder
    elif not elder.phone:
        desc = '%s has no phone number on their account.' % elder
    else:
        desc = '%s will receive SMS notifications if mentioned in a post.' % elder
    return desc


@register.filter
def contextualized_elders(queryset):
    return model.contextualized_elders(queryset)
