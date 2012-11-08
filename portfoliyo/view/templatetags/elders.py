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
def elder_types(qs):
    """
    Group a queryset of elders by type (school_staff/non).

    Return list of two dictionaries, one with school_staff: True and one_with
    school_staff: False, and each with a list of elders under the ``elders``
    key.

    Similar to the regroup tag, but always returns both groups, even if their
    list is empty.

    """
    staff = []
    non = []
    for elder in model.contextualized_elders(qs).order_by('school_staff', 'name'):
        if elder.school_staff:
            staff.append(elder)
        else:
            non.append(elder)
    return [
        {
            'school_staff': True,
            'elders': staff,
            },
        {
            'school_staff': False,
            'elders': non,
            },
        ]
