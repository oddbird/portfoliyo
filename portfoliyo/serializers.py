"""Serialization."""
import datetime

from django.utils import dateformat, timezone



def post2dict(post, **extra):
    """Return given post rendered as dictionary, ready for JSONification."""
    if post.author:
        author_name = (
            post.author.name or post.author.user.email or post.author.phone
            )

        relationship = post.get_relationship()

        if relationship is None:
            role = post.author.role
        else:
            role = relationship.description or post.author.role
    else:
        author_name = ""
        role = "Portfoliyo"

    timestamp = timezone.localtime(post.timestamp)

    sms_recipients = [s['name'] or s['role'] for s in post.meta.get('sms', [])]

    data = {
        'post_id': post.id,
        'author_id': post.author_id if post.author else 0,
        'author': author_name,
        'role': role,
        'timestamp': timestamp.isoformat(),
        'date': dateformat.format(timestamp, 'F j, Y'),
        'naturaldate': naturaldate(timestamp),
        'time': dateformat.time_format(timestamp, 'P'),
        'text': post.html_text,
        'sms': post.sms,
        'to_sms': post.to_sms,
        'from_sms': post.from_sms,
        'sms_recipients': ', '.join(sms_recipients),
        'num_sms_recipients': len(sms_recipients),
        'plural_sms': 's' if len(sms_recipients) > 1 else '',
        }

    data.update(post.extra_data())
    data.update(extra)

    return data



def now(tzinfo=None):
    """Get the current datetime."""
    return datetime.datetime.now(tzinfo)



def naturaldate(value):
    """
    Return given past date/datetime formatted "naturally" as a day/date.

    If the given date is today or yesterday, return "today" or "yesterday". If
    the date is within the past week, return the full day of the week
    name. Otherwise, return e.g. "January 23, 2012", omitting the year if it is
    the current year.

    """
    tzinfo = getattr(value, 'tzinfo', None)
    value = datetime.date(value.year, value.month, value.day)
    today = now(tzinfo).date()
    delta = today - value
    if delta.days == 0:
        return u'today'
    elif delta.days == 1:
        return u'yesterday'
    elif 0 < delta.days < 7:
        return dateformat.format(value, 'l')

    if today.year == value.year:
        long_format = 'F j'
    else:
        long_format = 'F j, Y'

    return dateformat.format(value, long_format)
