"""Village models."""
from __future__ import absolute_import

from collections import defaultdict
import re

from django.db import models
from django.utils import dateformat, html, timezone
from jsonfield import JSONField

from portfoliyo.pusher import get_pusher
from portfoliyo import sms
from ..users import models as user_models


def now():
    """Return current datetime as tz-aware UTC."""
    return timezone.now()


class Post(models.Model):
    author = models.ForeignKey(
        user_models.Profile,
        related_name='authored_posts',
        blank=True, null=True,
        ) # null author means "automated message sent by Portfoliyo"
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
    # arbitrary additional metadata, currently just highlights
    meta = JSONField(default={})


    def __unicode__(self):
        return self.original_text


    @property
    def sms(self):
        """Post was either received from or sent by SMS."""
        return self.from_sms or self.to_sms


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
            to_sms=False,
            )

        # notify highlighted SMS users
        meta_highlights = []
        sender_rel = post.get_relationship()
        if sender_rel:
            suffix = relationship_notification_suffix(sender_rel)
        else:
            suffix = u''
        sms_body = post.original_text + suffix
        for rel, mentioned_as in highlights.items():
            highlight_data = {
                'id': rel.elder.id,
                'mentioned_as': mentioned_as,
                'role': rel.description_or_role,
                'name': rel.elder.name,
                'email': rel.elder.user.email,
                'phone': rel.elder.phone,
                'is_active': rel.elder.user.is_active,
                'declined': rel.elder.declined,
                'sms_sent': False,
                }
            if rel.elder.user.is_active and rel.elder.phone:
                if rel.elder.phone != in_reply_to:
                    sms.send(
                        rel.elder.phone,
                        strip_initial_mention(sms_body, mentioned_as),
                        )
                post.to_sms = True
                highlight_data['sms_sent'] = True

            meta_highlights.append(highlight_data)

        post.meta['highlights'] = meta_highlights

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



def process_text(text, student):
    """
    Process given post text in given student's village.

    Escapes HTML, replaces newlines with <br>, replaces highlights.

    Returns tuple of (rendered-text,
    dict-mapping-highlighted-relationships-to-list-of-names-highlighted-as).

    """
    name_map = get_highlight_names(student)
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



def get_highlight_names(student):
    """
    Get highlightable names in given student's village.

    Returns dictionary mapping names to sets of relationships.

    """
    name_map = defaultdict(set)
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
            name_map[name].add(elder_rel)
        name_map['all'].add(elder_rel)
    return name_map



def normalize_name(name):
    """Normalize a name for highlight detection (lower-case, strip spaces)."""
    return name.lower().replace(' ', '')


def relationship_notification_suffix(relationship):
    """The suffix for texts sent out from this elder/student relationship."""
    return notification_suffix(
        relationship.elder.name or relationship.description_or_role)


def notification_suffix(name):
    """The suffix for texts sent out from this name."""
    return u' --%s' % name


def post_char_limit(relationship):
    """Max length for posts from this profile/student relationship."""
    return 160 - len(relationship_notification_suffix(relationship))


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
        'student_id': post.student_id,
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

    data.update(extra)

    return data
