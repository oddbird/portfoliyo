"""Village models."""
from __future__ import absolute_import

from collections import defaultdict
import logging
import re

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



def sms_eligible(elders):
    """Given queryset of elders, return queryset of SMS-eligible elders."""
    return elders.filter(
        declined=False,
        user__is_active=True,
        phone__isnull=False,
        )



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
    # arbitrary additional metadata, currently just highlights and SMSes
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


    def prepare_sms(self, profile_ids, in_reply_to=None):
        """
        Prepare and return SMS notifications for this post.

        ``profile_ids`` is a list of Profile IDs who should receive
        notifications. Only profiles in this list who also are active, have
        phone numbers, and have not declined sms notifications, will receive
        texts.

        Sets self.to_sms to True if any texts were sent, False otherwise, and
        self.meta['sms'] to a list of dictionaries containing basic metadata
        about each SMS sent.

        Return a list of (phone, sms-body) tuples to be sent.

        """
        meta_sms = []
        sms_sent = False
        if self.author:
            suffix = notification_suffix(self.get_relationship() or self.author)
        else:
            suffix = u""
        sms_body = self.original_text + suffix

        to_notify = sms_eligible(self.elders_in_context).filter(
            pk__in=profile_ids)

        to_send = []

        for elder in to_notify:
            sms_data = {
                'id': elder.id,
                'role': elder.role_in_context,
                'name': elder.name,
                'phone': elder.phone,
                }
            # with in_reply_to we assume caller sent SMS
            if elder.phone != in_reply_to:
                to_send.append((elder.phone, sms_body))
                if elder.state != user_models.Profile.STATE.done:
                    elder.state = user_models.Profile.STATE.done
                    elder.save()
            sms_sent = True

            meta_sms.append(sms_data)

        self.to_sms = sms_sent
        self.meta['sms'] = meta_sms

        return to_send


    def store_highlights(self, highlights):
        """
        Store info from given highlights dict to self.meta['highlights'].

        ``highlights`` should be dictionary mapping highlighted relationships
        to list of names highlighted as (i.e. as returned by ``process_text``).

        """
        meta_highlights = []
        for elder, mentioned_as in highlights.items():
            meta_highlights.append(
                {
                    'id': elder.id,
                    'mentioned_as': mentioned_as,
                    'role': elder.role_in_context,
                    'name': elder.name,
                    'email': elder.user.email,
                    'phone': elder.phone,
                    }
                )

        self.meta['highlights'] = meta_highlights


    def notify_email(self):
        """Send email notifications to eligible users."""
        # No email notifications on system-generated posts:
        if not self.author:
            return
        send_to = self.elders_in_context.filter(
            user__email__isnull=False,
            email_notifications=True,
            ).exclude(pk=self.author.pk)
        for profile in send_to:
            notifications.send_post_email_notification(profile, self)


    def get_relationship(self):
        return None


    def send_event(self, channel, **kwargs):
        """
        Send Pusher event for this Post, if Pusher is configured.

        Catch all exceptions from Pusher and log them to Sentry, but proceed -
        a Pusher failure is never worth aborting the post over.

        """
        pusher = get_pusher()
        if pusher is not None:
            try:
                pusher[channel].trigger(
                    'message_posted',
                    {'posts': [post_dict(self, **kwargs)]},
                    )
            except Exception as e:
                logger.error("Pusher exception: %s" % str(e))



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


    @property
    def safe_group(self):
        """Return self.group or AllStudentsGroup."""
        return self.group or user_models.AllStudentsGroup(self.author)


    @property
    def elders_in_context(self):
        """Queryset of elders in context."""
        return user_models.contextualized_elders(self.safe_group.all_elders)


    @classmethod
    def create(cls, author, group, text,
               sms_profile_ids=None, sequence_id=None, from_sms=False):
        """
        Create/return a BulkPost and all associated Posts.

        If ``author`` is ``None``, the post is system-originated.

        If ``group`` is ``None``, the post goes to all students of ``author``.

        It is currently not allowed for both to be ``None``.

        ``sms_profile_ids`` is a list of Profile IDs who should receive SMS
        notification of this post.

        ``sequence_id`` is an arbitrary ID generated on the client-side to
        uniquely identify posts by the current user within a given browser
        session; we just pass it through to the Pusher event(s).

        ``from_sms`` indicates whether this post was received over SMS.

        """
        if author is None and group is None:
            raise ValueError("BulkPost must have either author or group.""")

        orig_group = group
        if group is None:
            group = user_models.AllStudentsGroup(author)

        html_text, highlights = process_text(
            text, user_models.contextualized_elders(group.all_elders))

        post = cls(
            author=author,
            group=orig_group,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_to_send = post.prepare_sms(sms_profile_ids or [])

        post.store_highlights(highlights)

        post.save()

        for student in group.students.all():
            sub = Post.objects.create(
                author=author,
                student=student,
                original_text=text,
                html_text=html_text,
                from_sms=from_sms,
                to_sms=post.to_sms,
                meta=post.meta,
                from_bulk=post,
                )
            sub.send_event(
                'student_%s' % student.id,
                author_sequence_id=sequence_id,
                mark_read_url=reverse(
                    'mark_post_read', kwargs={'post_id': sub.id}),
                )
            # mark the subpost unread by all web users in village (not author)
            for elder in student.elders:
                if elder.user.email and elder != author:
                    unread.mark_unread(sub, elder)

        post.send_event('group_%s' % group.id, author_sequence_id=sequence_id)

        post.notify_email()

        for number, body in sms_to_send:
            sms.send(number, body)

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


    @property
    def elders_in_context(self):
        """Queryset of elders."""
        return user_models.contextualized_elders(
            self.student.elder_relationships)


    @classmethod
    def create(cls, author, student, text,
               sms_profile_ids=None, sequence_id=None, from_sms=False,
               in_reply_to=None, email_notifications=True):
        """
        Create/return a Post, triggering a Pusher event and SMS notifications.

        ``sms_profile_ids`` is a list of Profile IDs who should receive SMS
        notification of this post.

        ``sequence_id`` is an arbitrary ID generated on the client-side to
        uniquely identify posts by the current user within a given browser
        session; we just pass it through to the Pusher event.

        ``from_sms`` indicates whether this post was received over SMS.

        ``in_reply_to`` can be set to a phone number, in which case it will be
        assumed that an SMS was already sent to that number.

        If ``email_notifications`` is ``False``, no email notifications of this
        post will be sent.

        """
        html_text, highlights = process_text(
            text, user_models.contextualized_elders(student.elder_relationships))

        post = cls(
            author=author,
            student=student,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_to_send = post.prepare_sms(sms_profile_ids or [], in_reply_to)
        post.store_highlights(highlights)
        post.save()

        # mark the post unread by all web users in village (except the author)
        for elder in student.elders:
            if elder.user.email and elder != author:
                unread.mark_unread(post, elder)

        if email_notifications:
            post.notify_email()

        post.send_event(
            'student_%s' % student.id,
            author_sequence_id=sequence_id,
            mark_read_url=reverse(
                'mark_post_read', kwargs={'post_id': post.id}),
            )

        for number, body in sms_to_send:
            sms.send(number, body)

        return post


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


    def get_absolute_url(self):
        """A Post's URL is its village; this is for admin convenience."""
        return reverse('village', kwargs={'student_id': self.student_id})



def process_text(text, elders_in_context):
    """
    Process given post text in context of given (contextualized) elders.

    Escape HTML, replace newlines with <br>, replace highlights.

    Return tuple of (rendered-text,
    dict-mapping-highlighted-relationships-to-list-of-names-highlighted-as).

    """
    name_map = get_highlight_names(elders_in_context)
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
    dict-mapping-highlighted-elders-to-list-of-names-highlighted-as).

    ``name_map`` should be a mapping of highlightable names to contextualized
    elders (such as the map returned by ``get_highlight_names``).

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
        highlight_elders = name_map.get(normalize_name(highlight_name))
        if highlight_elders:
            replace_with = u'<b class="nametag%s" data-user-id="%s">%s</b>' % (
                u' all me' if highlight_name == 'all' else u'',
                u','.join([unicode(e.id) for e in highlight_elders]),
                full_highlight,
                )
            start, end = match.span(2)
            end -= stripped
            text = text[:start+offset] + replace_with + text[end+offset:]
            offset += len(replace_with) - (end - start)
            for elder in highlight_elders:
                highlighted.setdefault(elder, []).append(highlight_name)
    return text, highlighted



def get_highlight_names(elders_in_context):
    """
    Get highlightable names in context of given contextualized elders.

    Returns dictionary mapping names to sets of elders.

    """
    name_map = defaultdict(set)

    for elder in elders_in_context:
        possible_names = []
        if elder.name:
            possible_names.append(normalize_name(elder.name))
        if elder.phone:
            possible_names.append(normalize_name(elder.phone))
            possible_names.append(
                normalize_name(elder.phone.lstrip('+').lstrip('1')))
        if elder.user.email:
            possible_names.append(normalize_name(elder.user.email))
        possible_names.append(normalize_name(elder.role_in_context))
        for name in possible_names:
            name_map[name].add(elder)
        name_map['all'].add(elder)
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
        # strip SMS metadata down to minimal size
        'meta': {
            'sms': [
                {'id': s['id'], 'display': s['name'] or s['role']}
                for s in post.meta.get('sms', [])
                ]
            },
        }

    data.update(post.extra_data())
    data.update(extra)

    return data
