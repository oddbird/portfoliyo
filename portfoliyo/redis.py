from __future__ import absolute_import

from django.conf import settings



class InMemoryRedis(object):
    """
    An in-memory fake Redis, for when Redis is not available.

    In-memory and not thread-safe; for use only in local development and for
    running tests.

    """
    def __init__(self):
        self.data = {}


    def smembers(self, key):
        return self.data.get(key, set())


    def sadd(self, key, val):
        s = self.data.setdefault(key, set())
        ret = 1 if val in s else 0
        s.add(val)
        return ret


    def srem(self, key, val):
        s = self.data.setdefault(key, set())
        ret = 1 if val in s else 0
        s.discard(val)
        return ret


    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False


    def scard(self, key):
        s = self.data.setdefault(key, set())
        return len(s)


    def sismember(self, key, val):
        s = self.data.setdefault(key, set())
        return val in s


    def incr(self, key):
        val = self.data.get(key, 0)
        val += 1
        self.data[key] = val
        return val


    def pipeline(self):
        """
        Fake pipelining by just returning this instance.

        This'll fail if we try to use the "chaining" feature of real redis.py
        pipeline API. So we won't.

        """
        return self


    def execute(self):
        """Do nothing; pipelining is faked and the calls already happened."""
        pass



if settings.REDIS_URL: # pragma: no cover
    import redis # pragma: no cover
    client = redis.StrictRedis.from_url(settings.REDIS_URL) # pragma: no cover
else:
    client = InMemoryRedis()
