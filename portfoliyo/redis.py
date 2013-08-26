from __future__ import absolute_import

import time

from django.conf import settings
import redis
from redis.exceptions import ResponseError



class InMemoryRedis(object):
    """
    An in-memory fake Redis, for when Redis is not available.

    In-memory and not thread-safe; for use only in local development and for
    running tests.

    """
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.num_calls = 0


    def _get(self, key, default=None):
        self._check_expiry(key)
        return self.data.get(key, default)


    def _setdefault(self, key, default):
        self._check_expiry(key)
        return self.data.setdefault(key, default)


    def _check_expiry(self, key):
        # All queries call this (indirectly via _get or _setdefault) once
        self.num_calls += 1
        expiry = self.expiry.get(key)
        if expiry and time.time() > expiry:
            del self.data[key]
            del self.expiry[key]


    def expireat(self, key, timestamp):
        if not isinstance(timestamp, int):
            raise ResponseError("value is not an integer or out of range")
        self.expiry[key] = timestamp


    def smembers(self, key):
        return self._get(key, set())


    def sadd(self, key, val):
        val = str(val)
        s = self._setdefault(key, set())
        ret = 1 if val in s else 0
        s.add(val)
        return ret


    def srem(self, key, val):
        val = str(val)
        s = self._setdefault(key, set())
        ret = 1 if val in s else 0
        s.discard(val)
        return ret


    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False


    def scard(self, key):
        s = self._setdefault(key, set())
        return len(s)


    def sismember(self, key, val):
        val = str(val)
        s = self._setdefault(key, set())
        return val in s


    def incr(self, key):
        val = self._get(key, 0)
        val += 1
        self.data[key] = val
        return val


    def hmset(self, key, mapping):
        d = self._setdefault(key, {})
        d.update((k, str(v)) for k, v in mapping.items())
        return True


    def hgetall(self, key):
        return self._get(key, {}).copy()


    def zadd(self, key, score, val):
        score = float(score)
        val = str(val)
        l = self._setdefault(key, [])
        add_index = 0
        rem_index = None
        for i, (iscore, ival) in enumerate(l):
            if iscore < score:
                add_index = i + 1
            if val == ival:
                rem_index = i
        l.insert(add_index, (score, val))
        if rem_index is not None:
            if add_index <= rem_index:
                rem_index += 1
            l.pop(rem_index)
        return 1


    def zrangebyscore(self, key, min, max):
        min = float(min)
        max = float(max)
        ret = []
        for score, val in self._get(key, []):
            if score >= min and score <= max:
                ret.append(val)
        return ret


    def pipeline(self):
        return Pipeline(self)



class Pipeline(object):
    def __init__(self, client):
        self.client = client
        self.calls = []


    def execute(self):
        results = []
        start_calls = self.client.num_calls
        for method_name, args, kwargs in self.calls:
            results.append(getattr(self.client, method_name)(*args, **kwargs))
        # a pipelined set of commands counts as one call to Redis
        self.client.num_calls = start_calls + 1
        return results


def _make_pipelined_method(name):
    def _pipelined_method(self, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return self

    return _pipelined_method

for method_name in dir(InMemoryRedis):
    if not method_name.startswith('_') and method_name != 'pipeline':
        setattr(Pipeline, method_name, _make_pipelined_method(method_name))



if settings.REDIS_URL: # pragma: no cover
    client = redis.StrictRedis.from_url(settings.REDIS_URL)
else: # pragma: no cover
    client = InMemoryRedis()
