"""Tags and filters for displaying summaries of object collections."""
from django import template
from django.contrib.humanize.templatetags.humanize import apnumber


register = template.Library()



@register.filter
def summary(objects, options_string):
    """
    Display a summary of a list of objects.

    Assumes individual objects have sane unicode representations.

    Accepts the following options (in the form "option=val:option2=val2":

    ``max`` - the maximum size of the summary list (default 1). Any objects
    above this amount will be summarized as a number of objects; this summary
    also counts as one towards the maximum.

    ``named`` - the suffix to append to one or more named objects.

    ``unnamed`` - the suffix to append to a number of unnamed objects.

    ``apnumber`` - if 'no' or 'false', don't convert single-digit numbers to
    text (which is the default behavior.

    For instance, if the list of items given are ["Student X", "Student Y",
    "Student Z"] and ``named`` is "'s village" while ``unnamed`` is " student
    village", then with ``max==1`` the output would be "three student villages"
    (unless ``apnumber=="no"``, in which case it would be "3 student
    villages"), while with ``max==1`` the output would be "Student X two other
    student villages".

    """
    if not objects:
        return 'nobody'

    options = {}
    for option_string in options_string.split(':'):
        if option_string:
            k, v = option_string.split('=')
            options[k] = v

    max_show = int(options.get('max', 1))
    named = options.get('named', '')
    unnamed = options.get('unnamed', objects[0].__class__.__name__.lower())
    use_apnumber = not (
        options.get('apnumber', 'true').lower() in {'no', 'false', '0'})
    apply_apnumber = apnumber if use_apnumber else lambda x: x

    length = len(objects)
    some_unnamed = length > max_show

    if some_unnamed:
        num_unnamed = length - max_show + 1
        objects[max_show-1:] = [
            u"%s%s %s%s" % (
                apply_apnumber(num_unnamed),
                u" other" if max_show > 1 else u"",
                unnamed,
                u"s" if num_unnamed > 1 else u"",
                )
            ]

    objects = [unicode(o) for o in objects]

    return u'%s%s%s%s' % (
        u', '.join(objects[:-1]),
        u" and " if max_show > 1 else u"",
        objects[-1],
        named if not some_unnamed else u"",
        )
