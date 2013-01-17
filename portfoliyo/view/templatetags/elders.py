"""Template tags for the list of village elders."""
from django import template

from portfoliyo import model


register = template.Library()


@register.filter
def elder_status(elder, current):
    """Return short CSS class describing this elder's status."""
    status = 'online'
    if elder.declined:
        status = 'declined'
    elif not elder.user.is_active:
        status = 'inactive'
    elif not elder.school_staff:
        status = 'mobile'
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
        desc = '%s is not yet active.' % elder
    elif elder.phone:
        desc = '%s receives SMS notifications.' % elder
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
            'school_staff': False,
            'elders': non,
            },
        {
            'school_staff': True,
            'elders': staff,
            },
        ]
