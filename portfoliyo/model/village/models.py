"""Village models."""
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import html, timezone
from jsonfield import JSONField
from model_utils import Choices

from portfoliyo import tasks
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
    # additional metadata (SMSes sent, users contacted...)
    meta = JSONField(default={})

    is_bulk = None


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


    def send_sms(self, profile_ids=None, in_reply_to=None):
        """
        Send SMS notifications for this post.

        ``profile_ids`` is a list of Profile IDs who should receive SMSes. Only
        profiles in this list who also are active, have phone numbers, and have
        not declined SMSes, will receive texts. If set to "all", all eligible
        users will receive SMSes.

        Sets self.to_sms to True if any texts were sent, False otherwise, and
        self.meta['sms'] to a list of dictionaries containing basic metadata
        about each SMS sent.

        """
        meta_sms = []
        sms_sent = False
        if self.author:
            suffix = sms_suffix(self.get_relationship() or self.author)
        else:
            suffix = u""
        sms_body = self.original_text + suffix

        to_sms = sms_eligible(self.elders_in_context)

        if profile_ids != 'all':
            filters = models.Q(pk__in=profile_ids or [])
            if in_reply_to:
                filters = filters | models.Q(phone=in_reply_to)
            to_sms = to_sms.filter(filters)

        to_mark_done = []

        for elder in to_sms:
            sms_data = {
                'id': elder.id,
                'role': elder.role_in_context,
                'name': elder.name,
                'phone': elder.phone,
                }
            # with in_reply_to we assume caller sent SMS
            if elder.phone != in_reply_to:
                elder.send_sms(sms_body)
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



    def notify(self):
        """Record notifications for eligible users."""
        tasks.record_notification.delay('post_all', self)


    def get_relationship(self):
        return None



class BulkPost(BasePost):
    """A Post in multiple villages at once."""
    # the group this was posted to (null means all-students for this author)
    group = models.ForeignKey(
        user_models.Group, blank=True, null=True, related_name='bulk_posts')

    # bulk posts are always messages, and don't support attachments
    post_type = 'message'
    attachment = None


    is_bulk = True


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
               profile_ids=None, sequence_id=None, from_sms=False):
        """
        Create/return a BulkPost and all associated Posts.

        If ``author`` is ``None``, the post is system-originated.

        If ``group`` is ``None``, the post goes to all students of ``author``.

        It is currently not allowed for both to be ``None``.

        ``profile_ids`` is a list of Profile IDs who should receive this
        post as an SMS. If set to "all", will send to all SMS-eligible elders
        in the group.

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

        post.send_sms(profile_ids)

        post.save()

        students = list(group.students.all())

        relationships = user_models.Relationship.objects.filter(
            from_profile=author, to_profile__in=students).select_related(
            'to_profile')
        rels_by_student = {}
        for rel in relationships:
            rels_by_student[rel.student] = rel

        for student in group.students.all():
            sub = Post.objects.create(
                author=author,
                student=student,
                relationship=rels_by_student.get(student, None),
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

        post.notify()

        if author and not author.has_posted:
            user_models.Profile.objects.filter(pk=author.pk).update(
                has_posted=True)

        return post



class Post(BasePost):
    """A Post in a single student's village."""
    # the student in whose village this was posted
    TYPES = Choices("message", "note", "call", "meeting")

    student = models.ForeignKey(
        user_models.Profile, related_name='posts_in_village')
    post_type = models.CharField(
        max_length=20, choices=TYPES, default=TYPES.message)
    # relationship between author and student (nullable b/c might be deleted)
    relationship = models.ForeignKey(
        user_models.Relationship,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        )
    # attached file, if any
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True)
    # (optional) the bulk-post that triggered this post
    from_bulk = models.ForeignKey(
        BulkPost, blank=True, null=True, related_name='triggered')


    is_bulk = False


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
               profile_ids=None, sequence_id=None, from_sms=False,
               in_reply_to=None, notifications=True,
               post_type=None, attachment=None, extra_names=None):
        """
        Create/return a Post, triggering a Pusher event and SMSes.

        ``post_type`` is "message" (default), "note", "call", or "meeting".

        ``profile_ids`` is a list of Profile IDs who are related to this
        post. If ``post_type`` is "message", it's a list of profiles who should
        receive this post as an SMS (if "all", all eligible users will receive
        SMSes). For "call" or "meeting" post types, its a list of who was
        present at the meeting / on the call.

        ``sequence_id`` is an arbitrary ID generated on the client-side to
        uniquely identify posts by the current user within a given browser
        session; we just pass it through to the Pusher event.

        ``from_sms`` indicates whether this post was received over SMS.

        ``in_reply_to`` can be set to a phone number, in which case it will be
        assumed that an SMS was already sent to that number.

        If ``notifications`` is ``False``, this post won't be included in
        activity notifications.

        """
        html_text = text2html(text)

        try:
            rel = user_models.Relationship.objects.get(
                from_profile=author, to_profile=student)
        except user_models.Relationship.DoesNotExist:
            rel = None

        post = cls(
            author=author,
            student=student,
            relationship=rel,
            original_text=text,
            html_text=html_text,
            from_sms=from_sms,
            )

        if post_type:
            post.post_type = post_type

        if post.post_type == 'message':
            post.send_sms(profile_ids, in_reply_to)
        elif profile_ids:
            post.meta['present'] = [
                {'id': e.id, 'name': e.name, 'role': e.role_in_context}
                for e in post.elders_in_context.filter(pk__in=profile_ids)
                ]

        if attachment:
            post.attachment = attachment

        if extra_names:
            post.meta['extra_names'] = extra_names

        post.save()

        # mark the post unread by all web users in village (except the author)
        for elder in student.elders:
            if elder.user.email and elder != author:
                unread.mark_unread(post, elder)

        tasks.push_event.delay(
            'posted',
            post.id,
            author_sequence_id=sequence_id,
            mark_read_url=reverse(
                'mark_post_read', kwargs={'post_id': post.id}),
            )

        if notifications:
            post.notify()

        if author and not author.has_posted:
            user_models.Profile.objects.filter(pk=author.pk).update(
                has_posted=True)

        return post


    def get_relationship(self):
        """Return Relationship between author and student, or None."""
        return self.relationship


    def get_absolute_url(self):
        """A Post's URL is its village; this is for admin convenience."""
        return reverse('village', kwargs={'student_id': self.student_id})



def text2html(text):
    """Process given post text to HTML."""
    return html.escape(text).replace('\n', '<br>')


def sms_suffix(elder_or_rel):
    """The suffix for texts sent out from this elder or relationship."""
    return u' --%s' % elder_or_rel.name_or_role



def post_char_limit(elder_or_rel):
    """Max length for posts from this elder or relationship."""
    return 160 - len(sms_suffix(elder_or_rel))
