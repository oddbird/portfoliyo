from __future__ import absolute_import

from django.conf import settings
import redis

client = redis.StrictRedis.from_url(settings.REDIS_URL)
