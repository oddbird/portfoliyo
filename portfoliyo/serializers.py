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
        author_name = "Portfoliyo"
        role = ""

    timestamp = timezone.localtime(post.timestamp)

    sms_recipients = [s['name'] or s['role'] for s in post.meta.get('sms', [])]

    data = {
        'post_id': post.id,
        'author_id': post.author_id if post.author else 0,
        'author': author_name,
        'role': role,
        'school_staff': post.author.school_staff if post.author else True,
        'timestamp': timestamp.isoformat(),
        'timestamp_display': naturaldatetime(timestamp),
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



def now():
    """Get the current (timezone-aware) datetime."""
    return datetime.datetime.utcnow().replace(tzinfo=timezone.utc)



def naturaldatetime(value):
    """
    Return given past datetime formatted "naturally", omitting unnecessary data.

    If the given date is today, display only the time. If the date is within
    the past week, prepend the three-letter day of the week name to the
    time. Otherwise, return e.g. "January 23, 2012", omitting the year if it is
    the current year.

    A given timezone-naive datetime is assumed to be in the current timezone.

    """
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    else:
        value = timezone.localtime(value)
    nowdt = timezone.localtime(now())
    delta = nowdt - value
    if delta.days <= 0:
        return dateformat.format(value, 'P')
    elif 0 < delta.days < 7:
        return dateformat.format(value, 'D P')

    if nowdt.year == value.year:
        long_format = 'j-M P'
    else:
        long_format = 'j-M Y P'

    return dateformat.format(value, long_format)
