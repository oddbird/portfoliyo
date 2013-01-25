"""Village models."""
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import dateformat, html, timezone
from jsonfield import JSONField

from portfoliyo import notifications, tasks
from ..users import models as user_models
from . import unread



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


def is_sms_eligible(elder):
    """Return True if given elder is eligible to receive SMSes."""
    return elder.phone and not elder.declined and elder.user.is_active



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
    # the parsed text as HTML
    html_text = models.TextField()
    # message was received via SMS
    from_sms = models.BooleanField(default=False)
    # message was sent to at least one SMS
    to_sms = models.BooleanField(default=False)
    # arbitrary additional metadata, currently just SMSes
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
            models.Q(pk__in=profile_ids) | models.Q(phone=in_reply_to))

        to_send = []
        to_mark_done = []

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
                to_mark_done.append(elder)
            sms_sent = True

            meta_sms.append(sms_data)

        # when we send an elder who didn't finish answering their signup
        # questions an SMS, we can no longer assume their next reply is
        # answering the last question we asked. So we mark all in-process
        # signups done for all users we are sending an SMS to.
        user_models.TextSignup.objects.filter(family__in=to_mark_done).update(
            state=user_models.TextSignup.STATE.done)

        self.to_sms = sms_sent
        self.meta['sms'] = meta_sms

        return to_send



    def notify_email(self, from_sms):
        """Send email notifications to eligible users."""
        # No email notifications on system-generated posts:
        if not self.author:
            return
        filters = {
            'user__email__isnull': False,
            'user__is_active': True,
            }
        if from_sms:
            filters['notify_parent_text'] = True
        else:
            filters['notify_teacher_post'] = True
        send_to = self.elders_in_context.filter(
            **filters).exclude(pk=self.author.pk)
        for profile in send_to:
            notifications.send_post_email_notification(profile, self)


    def get_relationship(self):
        return None



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

        html_text = text2html(text)

        post = cls(
            author=author,
            group=orig_group,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_to_send = post.prepare_sms(sms_profile_ids or [])

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
            tasks.push_event.delay(
                'posted',
                sub.id,
                author_sequence_id=sequence_id,
                mark_read_url=reverse(
                    'mark_post_read', kwargs={'post_id': sub.id}),
                )
            # mark the subpost unread by all web users in village (not author)
            for elder in student.elders:
                if elder.user.email and elder != author:
                    unread.mark_unread(sub, elder)

        tasks.push_event.delay(
            'bulk_posted', post.id, author_sequence_id=sequence_id)

        post.notify_email(from_sms)

        for number, body in sms_to_send:
            tasks.send_sms.delay(number, body)

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
        html_text = text2html(text)

        post = cls(
            author=author,
            student=student,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        sms_to_send = post.prepare_sms(sms_profile_ids or [], in_reply_to)
        post.save()

        # mark the post unread by all web users in village (except the author)
        for elder in student.elders:
            if elder.user.email and elder != author:
                unread.mark_unread(post, elder)

        if email_notifications:
            post.notify_email(from_sms)

        tasks.push_event.delay(
            'posted',
            post.id,
            author_sequence_id=sequence_id,
            mark_read_url=reverse(
                'mark_post_read', kwargs={'post_id': post.id}),
            )

        for number, body in sms_to_send:
            tasks.send_sms.delay(number, body)

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



def text2html(text):
    """Process given post text to HTML."""
    return html.escape(text).replace('\n', '<br>')



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

    sms_recipients = [s['name'] or s['role'] for s in post.meta.get('sms', [])]

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
        'sms_recipients': ', '.join(sms_recipients),
        'num_sms_recipients': len(sms_recipients),
        'plural_sms': 's' if len(sms_recipients) > 1 else '',
        }

    data.update(post.extra_data())
    data.update(extra)

    return data
