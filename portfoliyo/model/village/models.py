"""Village models."""
from __future__ import absolute_import

import re

from django.db import models
from django.utils import dateformat, html, timezone

from portfoliyo.pusher import get_pusher
from portfoliyo import sms
from ..users import models as user_models


def now():
    """Return current datetime as tz-aware UTC."""
    return timezone.now()


class Post(models.Model):
    author = models.ForeignKey(
        user_models.Profile, related_name='authored_posts')
    timestamp = models.DateTimeField(default=now)
    # the student in whose village this was posted
    student = models.ForeignKey(
        user_models.Profile, related_name='posts_in_village')
    # the original text as entered by a user
    original_text = models.TextField()
    # the parsed text as HTML, with highlights wrapped in <b>
    html_text = models.TextField()
    # message was received via SMS
    from_sms = models.BooleanField(default=False)
    # message was sent to at least one SMS
    to_sms = models.BooleanField(default=False)


    def __unicode__(self):
        return self.original_text


    @property
    def sms(self):
        """Post was either received from or sent by SMS."""
        return self.from_sms or self.to_sms


    @classmethod
    def create(cls, author, student, text, sequence_id=None, from_sms=False):
        """Create and return a Post."""
        html_text, highlights = process_text(text, student)

        post = cls(
            author=author,
            student=student,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            to_sms=False,
            )

        # notify highlighted text-only users
        for rel in highlights:
            if (rel.elder.user.is_active and rel.elder.phone):
                sender_rel = post.get_relationship()
                prefix = text_notification_prefix(sender_rel)
                sms_body = prefix + post.original_text
                sms.send(rel.elder.phone, sms_body)
                post.to_sms = True

        post.save()

        # trigger Pusher event, if configured
        pusher = get_pusher()
        if pusher is not None:
            channel = 'student_%s' % student.id
            pusher[channel].trigger(
                'message_posted',
                {'posts': [post_dict(post, author_sequence_id=sequence_id)]},
                )

        return post


    def get_relationship(self):
        """The Relationship object between the author and the student."""
        try:
            return user_models.Relationship.objects.select_related().get(
                kind=user_models.Relationship.KIND.elder,
                from_profile=self.author,
                to_profile=self.student,
                )
        except user_models.Relationship.DoesNotExist:
            return None



def process_text(text, student):
    """
    Process given post text in given student's village.

    Escapes HTML, replaces newlines with <br>, replaces highlights.

    Returns tuple of (rendered-text, set-of-highlighted-relationships).

    """
    name_map = get_highlight_names(student)
    html_text, highlights = replace_highlights(html.escape(text), name_map)
    html_text = html_text.replace('\n', '<br>')
    return html_text, highlights



highlight_re = re.compile(r'(\A|[\s[(])(@(\S+?))(\Z|[\s,.;:)\]?])')



def replace_highlights(text, name_map):
    """
    Detect highlights and wrap with HTML element.

    Returns a tuple of (rendered-text, set-of-highlighted-relationships).

    ``name_map`` should be a mapping of highlightable names to the Relationship
    with the elder who has that name (such as the map returned by
    ``get_highlight_names``).

    """
    highlighted = set()
    offset = 0 # how much we've increased the length of ``text``
    for match in highlight_re.finditer(text):
        full_highlight = match.group(2)
        highlight_name = match.group(3)
        highlight_rel = name_map.get(normalize_name(highlight_name))
        if highlight_rel:
            replace_with = u'<b class="nametag" data-user-id="%s">%s</b>' % (
                highlight_rel.elder.id, full_highlight)
            start, end = match.span(2)
            text = text[:start+offset] + replace_with + text[end+offset:]
            offset += len(replace_with) - (end - start)
            highlighted.add(highlight_rel)
    return text, highlighted



def get_highlight_names(student):
    """
    Get highlightable names in given student's village.

    Returns dictionary mapping names to relationships.

    """
    name_map = {}
    collisions = set()
    for elder_rel in student.elder_relationships:
        elder = elder_rel.elder
        possible_names = []
        if elder.name:
            possible_names.append(normalize_name(elder.name))
        if elder.phone:
            possible_names.append(normalize_name(elder.phone))
            possible_names.append(
                normalize_name(elder.phone.lstrip('+').lstrip('1')))
        if elder.user.email:
            possible_names.append(normalize_name(elder.user.email))
        possible_names.append(normalize_name(elder_rel.description_or_role))
        for name in possible_names:
            if name in name_map:
                # if there's a collision, nobody gets to use that name
                # @@@ when we have autocomplete, maybe add disambiguators?
                collisions.add(name)
            name_map[name] = elder_rel
    for collision in collisions:
        del name_map[collision]
    return name_map



def normalize_name(name):
    """Normalize a name for highlight detection (lower-case, strip spaces)."""
    return name.lower().replace(' ', '')


def text_notification_prefix(relationship):
    """The prefix for texts sent out from this elder/student relationship."""
    return u'%s: ' % (
        relationship.elder.name or relationship.description_or_role,)


def post_char_limit(relationship):
    """Max length for posts from this profile/student relationship."""
    return 160 - len(text_notification_prefix(relationship))



def post_dict(post, **extra):
    """Return given post rendered as dictionary, ready for JSONification."""
    author_name = (
        post.author.name or post.author.user.email or post.author.phone)

    relationship = post.get_relationship()

    if relationship is None:
        role = post.author.role
    else:
        role = relationship.description or post.author.role

    timestamp = timezone.localtime(post.timestamp)

    data = {
        'author_id': post.author_id,
        'student_id': post.student_id,
        'author': author_name,
        'role': role,
        'timestamp': timestamp.isoformat(),
        'date': dateformat.format(timestamp, 'n/j/Y'),
        'time': dateformat.time_format(timestamp, 'P'),
        'text': post.html_text,
        'sms': post.sms,
        }

    data.update(extra)

    return data
