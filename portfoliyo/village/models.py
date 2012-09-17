"""Village models."""
from __future__ import absolute_import

import re

from django.db import models
from django.utils import timezone, dateformat, html

from portfoliyo.pusher import get_pusher
from ..users import invites, models as user_models



class Post(models.Model):
    author = models.ForeignKey(
        user_models.Profile, related_name='authored_posts')
    timestamp = models.DateTimeField(default=timezone.now)
    # the student in whose village this was posted
    student = models.ForeignKey(
        user_models.Profile, related_name='posts_in_village')
    # the original text as entered by a user
    original_text = models.TextField()
    # the parsed text as HTML, with highlights wrapped in <b>
    html_text = models.TextField()


    def __unicode__(self):
        return self.original_text


    @classmethod
    def create(cls, author, student, text, sequence_id=None):
        """Create and return a Post."""
        html_text, highlights = replace_highlights(html.escape(text), student)
        html_text = html_text.replace('\n', '<br>')

        post = cls.objects.create(
            author=author,
            student=student,
            original_text=text,
            html_text=html_text,
            )

        # notify highlighted text-only users
        for rel in highlights:
            if (rel.elder.user.is_active and
                    rel.elder.phone and
                    not rel.elder.user.email):
                sender_rel = post.get_relationship()
                prefix = text_notification_prefix(sender_rel)
                sms_body = prefix + post.original_text
                invites.send_sms(rel.elder.phone, sms_body)

        # trigger Pusher event, if Pusher is configured
        pusher = get_pusher()
        if pusher is not None:
            channel = 'student_%s' % student.id
            pusher[channel].trigger(
                'message_posted',
                {'posts': [post.json_data(author_sequence_id=sequence_id)]},
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


    def json_data(self, **extra):
        """Return this post rendered as dictionary, ready for JSONification."""
        author_name = (
            self.author.name or self.author.user.email or self.author.phone)

        relationship = self.get_relationship()

        if relationship is None:
            role = self.author.role
        else:
            role = relationship.description or self.author.role

        data = {
            'author_id': self.author_id,
            'student_id': self.student_id,
            'author': author_name,
            'role': role,
            'timestamp': self.timestamp.isoformat(),
            'date': dateformat.format(self.timestamp, 'n/j/Y'),
            'time': dateformat.time_format(self.timestamp, 'P'),
            'text': self.html_text,
            }

        data.update(extra)

        return data



highlight_re = re.compile(r'(\A|[\s[(])@(\S+?)(\Z|[\s,.;:)\]?])')



def replace_highlights(text, student):
    """
    Detect highlights and wrap with HTML element.

    Returns a tuple of (rendered-text, set-of-highlighted-relationships).

    """
    name_map = get_highlight_names(student)
    highlighted = set()
    for _, highlight_name, _ in highlight_re.findall(text):
        highlight_rel = name_map.get(normalize_name(highlight_name))
        if highlight_rel:
            full_highlight = '@%s' % highlight_name
            replace_with = '<b class="nametag" data-user-id="%s">%s</b>' % (
                highlight_rel.elder.id, full_highlight)
            text = text.replace(full_highlight, replace_with)
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
        del name_map[name]
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
