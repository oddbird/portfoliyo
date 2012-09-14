"""Village models."""
from __future__ import absolute_import

import re

from django.conf import settings
from django.db import models
from django.utils import timezone, dateformat
import pusher as pusherlib

from ..users import models as user_models



pusher = pusherlib.Pusher(
    app_id=settings.PUSHER_APPID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    )



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
    def create(cls, author, student, text):
        """Create and return a Post."""
        html, highlights = replace_highlights(text, student)

        # @@@ notify highlighted users

        post = cls.objects.create(
            author=author,
            student=student,
            original_text=text,
            html_text=html,
            )

        # trigger Pusher event
        channel = 'student_%s' % student.id
        pusher[channel].trigger('message_posted', {'posts': [post.json_data()]})

        return post


    def get_relationship(self):
        """The Relationship object between the author and the student."""
        try:
            return user_models.Relationship.objects.get(
                kind=user_models.Relationship.KIND.elder,
                from_profile=self.author,
                to_profile=self.student,
                )
        except user_models.Relationship.DoesNotExist:
            return None


    def json_data(self):
        """Return this post rendered as dictionary, ready for JSONification."""
        author_name = (
            self.author.name or self.author.user.email or self.author.phone)

        relationship = self.get_relationship()

        if relationship is None:
            role = self.author.role
        else:
            role = relationship.description

        return {
            'author_id': self.author_id,
            'student_id': self.student_id,
            'author': author_name,
            'role': role,
            'date': dateformat.format(self.timestamp, 'n/j/Y'),
            'time': dateformat.time_format(self.timestamp, 'P'),
            'text': self.html_text,
            }



highlight_re = re.compile(r'(\A|\s+)@(\S+)(\Z|\s+)')



def replace_highlights(text, student):
    """
    Detect highlights and wrap with HTML element.

    Returns a tuple of (rendered-text, set-of-highlighted-profiles).

    """
    name_map = get_highlight_names(student)
    highlighted = set()
    for _, highlight_name, _ in highlight_re.findall(text):
        highlight_user = name_map.get(normalize_name(highlight_name))
        if highlight_user:
            full_highlight = '@%s' % highlight_name
            replace_with = '<b class="nametag" data-user-id="%s">%s</b>' % (
                highlight_user.id, full_highlight)
            text = text.replace(full_highlight, replace_with)
            highlighted.add(highlight_user)
    return text, highlighted



def get_highlight_names(student):
    """
    Get highlightable names in given student's village.

    Returns dictionary mapping names to profiles.

    """
    map = {}
    for elder in student.elders:
        if elder.name:
            map[normalize_name(elder.name)] = elder
        # @@@ also do emails, phones, roles, if not all users will have names?
    return map



def normalize_name(name):
    """Normalize a name for highlight detection (lower-case, strip spaces)."""
    return name.lower().replace(' ', '')
