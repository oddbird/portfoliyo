"""Village models."""
from __future__ import absolute_import

from collections import defaultdict
import logging
import re
import socket

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import dateformat, html, timezone
from jsonfield import JSONField

from portfoliyo.pusher import get_pusher
from portfoliyo import notifications, sms
from ..users import models as user_models
from . import unread


logger = logging.getLogger(__name__)



def now():
    """Return current datetime as tz-aware UTC."""
    return timezone.now()



class BasePost(models.Model):
    """Common Post fields and methods."""
    author = models.ForeignKey(
        user_models.Profile,
        related_name='authored_%(class)ss',
        blank=True, null=True,
        ) # null author means "automated message sent by Portfoliyo"
    timestamp = models.DateTimeField(default=now)
    # the original text as entered by a user
    original_text = models.TextField()
    # the parsed text as HTML, with highlights wrapped in <b>
    html_text = models.TextField()
    # message was received via SMS
    from_sms = models.BooleanField(default=False)
    # message was sent to at least one SMS
    to_sms = models.BooleanField(default=False)
    # arbitrary additional metadata, currently just highlights
    meta = JSONField(default={})


    class Meta:
        abstract = True


    def __unicode__(self):
        return self.original_text


    @property
    def sms(self):
        """Post was either received from or sent by SMS."""
        return self.from_sms or self.to_sms


    def extra_data(self):
        """Return any extra data for serialization."""
        return {}


    def notify_sms(self, highlights, in_reply_to=None):
        """
        Send SMS notifications to highlighted users.

        ``highlights`` should be a mapping of elders (or relationships) to list
        of names that elder (or relationship) was mentioned as (such as the
        mapping returned by ``process_text``).

        Returns a tuple of (sms-sent, meta-highlights) where sms-sent is a
        boolean that is True if any SMS notifications were sent, and
        meta-highlights is a list of dictionaries providing details about each
        sent notification.

        """
        meta_highlights = []
        sms_sent = False
        if self.author:
            suffix = notification_suffix(self.get_relationship() or self.author)
        else:
            suffix = u""
        sms_body = self.original_text + suffix
        for elder_or_rel, mentioned_as in highlights.items():
            elder = elder_or_rel.elder
            role = elder_or_rel.description_or_role
            highlight_data = {
                'id': elder.id,
                'mentioned_as': mentioned_as,
                'role': role,
                'name': elder.name,
                'email': elder.user.email,
                'phone': elder.phone,
                'is_active': elder.user.is_active,
                'declined': elder.declined,
                'sms_sent': False,
                }
            if elder.user.is_active and elder.phone:
                if elder.phone != in_reply_to:
                    sms.send(
                        elder.phone,
                        strip_initial_mention(sms_body, mentioned_as),
                        )
                sms_sent = True
                highlight_data['sms_sent'] = True

            meta_highlights.append(highlight_data)

        return (sms_sent, meta_highlights)


    def get_relationship(self):
        return None


    def send_event(self, channel, **kwargs):
        """Send Pusher event for this Post, if Pusher is configured."""
        pusher = get_pusher()
        if pusher is not None:
            try:
                pusher[channel].trigger(
                    'message_posted',
                    {'posts': [post_dict(self, **kwargs)]},
                    )
            except socket.error as e:
                logger.error("Pusher socket error: %s" % str(e))



class BulkPost(BasePost):
    """A Post in multiple villages at once."""
    # the group this was posted to (null means all-students for this author)
    group = models.ForeignKey(
        user_models.Group, blank=True, null=True, related_name='bulk_posts')


    def extra_data(self):
        """Return any extra data for serialization."""
        return {
            'group_id': (
                self.group_id or user_models.AllStudentsGroup(self.author).id)
            }


    @classmethod
    def create(cls, author, group, text,
               sequence_id=None, from_sms=False):
        """
        Create/return a BulkPost and all associated Posts.

        If ``author`` is ``None``, the post is system-originated.

        If ``group`` is ``None``, the post goes to all students of ``author``.

        It is currently not allowed for both to be ``None``.

        ``sequence_id`` is an arbitrary ID generated on the client-side to
        uniquely identify posts by the current user within a given browser
        session; we just pass it through to the Pusher event(s).

        """
        if author is None and group is None:
            raise ValueError("BulkPost must have either author or group.""")

        orig_group = group
        if group is None:
            group = user_models.AllStudentsGroup(author)

        html_text, highlights = process_text(text, group)

        post = cls(
            author=author,
            group=orig_group,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_sent, meta_highlights = post.notify_sms(highlights)
        post.to_sms = sms_sent
        post.meta['highlights'] = meta_highlights

        post.save()

        for student in group.students.all():
            sub = Post.objects.create(
                author=author,
                student=student,
                original_text=text,
                html_text=html_text,
                from_sms=from_sms,
                to_sms=sms_sent,
                meta=post.meta,
                from_bulk=post,
                )
            sub.notify_email()
            sub.send_event(
                'student_%s' % student.id,
                author_sequence_id=sequence_id,
                mark_read_url=reverse(
                    'mark_post_read', kwargs={'post_id': sub.id}),
                unread=True,
                )
            # mark the sub0-ost unread by all web users in village
            for elder in student.elders:
                if elder.user.email:
                    unread.mark_unread(sub, elder)

        post.send_event('group_%s' % group.id, author_sequence_id=sequence_id)

        return post



class Post(BasePost):
    """A Post in a single student's village."""
    # the student in whose village this was posted
    student = models.ForeignKey(
        user_models.Profile, related_name='posts_in_village')
    # (optional) the bulk-post that triggered this post
    from_bulk = models.ForeignKey(
        BulkPost, blank=True, null=True, related_name='triggered')


    def extra_data(self):
        """Return any extra data for serialization."""
        return {'student_id': self.student_id}


    @classmethod
    def create(cls, author, student, text,
               sequence_id=None, from_sms=False, in_reply_to=None):
        """
        Create/return a Post, triggering a Pusher event and SMS notifications.

        ``sequence_id`` is an arbitrary ID generated on the client-side to
        uniquely identify posts by the current user within a given browser
        session; we just pass it through to the Pusher event.

        ``in_reply_to`` can be set to a phone number, in which case a mention
        of that phone number will be prepended to the post body, and it will be
        assumed that an SMS was already sent to that number (thus no additional
        notification will be sent).

        """
        if in_reply_to:
            text = u"@%s %s" % (in_reply_to, text)

        html_text, highlights = process_text(text, student)

        post = cls(
            author=author,
            student=student,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_sent, meta_highlights = post.notify_sms(highlights, in_reply_to)
        post.to_sms = sms_sent
        post.meta['highlights'] = meta_highlights

        post.save()

        # mark the post unread by all web users in village (except the author)
        for elder in student.elders:
            if elder.user.email and elder != author:
                unread.mark_unread(post, elder)

        post.notify_email()
        post.send_event(
            'student_%s' % student.id,
            author_sequence_id=sequence_id,
            mark_read_url=reverse(
                'mark_post_read', kwargs={'post_id': post.id}),
            unread=True,
            )

        return post


    def notify_email(self):
        """Send email notifications to eligible users."""
        # No email notifications on system-generated posts:
        if not self.author:
            return
        send_to = user_models.Profile.objects.filter(
            deleted=False,
            relationships_from__to_profile=self.student,
            user__email__isnull=False,
            email_notifications=True,
            ).exclude(pk=self.author.pk)
        for profile in send_to:
            notifications.send_email_notification(profile, self)


    def get_relationship(self):
        """Return Relationship between author and student, or None."""
        try:
            return self._rel
        except AttributeError:
            try:
                self._rel = user_models.Relationship.objects.select_related(
                    ).get(
                    kind=user_models.Relationship.KIND.elder,
                    from_profile=self.author,
                    to_profile=self.student,
                    )
            except user_models.Relationship.DoesNotExist:
                self._rel = None
        return self._rel



def process_text(text, student_or_group):
    """
    Process given post text in given student or group's village.

    Escape HTML, replace newlines with <br>, replace highlights.

    Return tuple of (rendered-text,
    dict-mapping-highlighted-relationships-to-list-of-names-highlighted-as).

    """
    name_map = get_highlight_names(student_or_group)
    html_text, highlights = replace_highlights(html.escape(text), name_map)
    html_text = html_text.replace('\n', '<br>')
    return html_text, highlights



# The ending delimiter here must use a lookahead assertion rather than a simple
# match, otherwise adjacent highlights separated by a single space fail to
# match the second highlight, because re.finditer returns only non-overlapping
# matches, and without the lookahead both highlight matches would want to grab
# that same intervening space. We could use lookbehind for the initial
# delimiter as well, except that lookbehind requires a fixed-width pattern, and
# our delimiter pattern is not fixed-width (it's zero or one).
highlight_re = re.compile(
    r"""(\A|[\s[(])          # string-start or whitespace/punctuation
        (@(\S+?))            # @ followed by (non-greedy) non-whitespace
        (?=\Z|[\s,;:)\]?])  # string-end or whitespace/punctuation
    """,
    re.VERBOSE,
    )



def replace_highlights(text, name_map):
    """
    Detect highlights and wrap with HTML element.

    Returns a tuple of (rendered-text,
    dict-mapping-highlighted-relationships-to-list-of-names-highlighted-as).

    ``name_map`` should be a mapping of highlightable names to the Relationship
    with the elder who has that name (such as the map returned by
    ``get_highlight_names``).

    """
    highlighted = {}
    offset = 0 # how much we've increased the length of ``text``
    for match in highlight_re.finditer(text):
        full_highlight = match.group(2)
        highlight_name = match.group(3)
        # special handling for period (rather than putting it into the regex as
        # highlight-terminating punctuation) so that we can support highlights
        # with internal periods (i.e. email addresses)
        stripped = 0
        while highlight_name.endswith('.'):
            highlight_name = highlight_name[:-1]
            full_highlight = full_highlight[:-1]
            stripped += 1
        highlight_rels = name_map.get(normalize_name(highlight_name))
        if highlight_rels:
            replace_with = u'<b class="nametag%s" data-user-id="%s">%s</b>' % (
                u' all me' if highlight_name == 'all' else u'',
                u','.join([unicode(r.elder.id) for r in highlight_rels]),
                full_highlight,
                )
            start, end = match.span(2)
            end -= stripped
            text = text[:start+offset] + replace_with + text[end+offset:]
            offset += len(replace_with) - (end - start)
            for rel in highlight_rels:
                highlighted.setdefault(rel, []).append(highlight_name)
    return text, highlighted



def get_highlight_names(student_or_group):
    """
    Get highlightable names in given student or group's village.

    Returns dictionary mapping names to sets of relationships.

    """
    name_map = defaultdict(set)
    for elder_rel in student_or_group.elder_relationships:
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
            name_map[name].add(elder_rel)
        name_map['all'].add(elder_rel)
    return name_map



def normalize_name(name):
    """Normalize a name for highlight detection (lower-case, strip spaces)."""
    return name.lower().replace(' ', '')


def notification_suffix(elder_or_rel):
    """The suffix for texts sent out from this elder or relationship."""
    return u' --%s' % elder_or_rel.name_or_role


def post_char_limit(elder_or_rel):
    """Max length for posts from this elder or relationship."""
    return 160 - len(notification_suffix(elder_or_rel))


def strip_initial_mention(sms_body, mentioned_as):
    """Given an SMS and a list of highlight names, strip initial mention."""
    initial_mention_re = re.compile(
        '^\s*@(%s)\s*' % '|'.join(mentioned_as), re.I)
    return initial_mention_re.sub(u"", sms_body)



def post_dict(post, **extra):
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

    data = {
        'post_id': post.id,
        'author_id': post.author_id if post.author else 0,
        'author': author_name,
        'role': role,
        'timestamp': timestamp.isoformat(),
        'date': dateformat.format(timestamp, 'n/j/Y'),
        'time': dateformat.time_format(timestamp, 'P'),
        'text': post.html_text,
        'sms': post.sms,
        'to_sms': post.to_sms,
        'from_sms': post.from_sms,
        'meta': post.meta,
        }

    data.update(post.extra_data())
    data.update(extra)

    return data
