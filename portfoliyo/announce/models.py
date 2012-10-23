"""Site announcement models."""
from django.db import models
from django.utils import timezone

from portfoliyo import redis, model



class Announcement(models.Model):
    text = models.CharField(max_length=300)
    timestamp = models.DateTimeField(default=timezone.now)


    def __unicode__(self):
        return self.text



def to_all(text):
    """Create an announcement, mark it unread by all web users."""
    a = Announcement.objects.create(text=text)

    for profile_id in model.Profile.objects.filter(
            user__email__isnull=False).values_list('id', flat=True):
        redis.client.sadd(make_key(profile_id), a.pk)

    return a



def get_unread(profile):
    """Get unread announcements for given profile."""
    announcement_ids = redis.client.smembers(make_key(profile.id))

    return Announcement.objects.filter(pk__in=announcement_ids).order_by(
        'timestamp')



def mark_read(profile, announcement_id):
    return redis.client.srem(make_key(profile.id), announcement_id)



def make_key(profile_id):
    """Return Redis key for given profile's set of unread announcement IDs."""
    return 'announcements:unread:%s' % profile_id
