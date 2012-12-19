"""
Tests for redis in-memory implementation.

These tests will also run against a real Redis, if configured, verifying the
tests themselves.

"""
import mock

import pytest
from redis.exceptions import ResponseError



def test_sets(redis):
    """Test in-memory implementation of Redis sets."""
    redis.sadd('foo', 'bar')
    redis.sadd('foo', 'baz')
    redis.srem('foo', 'baz')
    assert redis.scard('foo') == 1
    assert redis.sismember('foo', 'bar')
    assert not redis.sismember('foo', 'baz')
    assert redis.smembers('foo') == {'bar'}


def test_sets_convert_to_str(redis):
    """Set values are converted to strings."""
    redis.sadd('foo', 3)
    assert redis.sismember('foo', 3)
    assert redis.sismember('foo', '3')
    assert redis.smembers('foo') == {'3'}
    redis.srem('foo', 3)
    assert redis.smembers('foo') == set()


def test_delete(redis):
    """Test in-memory implementation of Redis delete."""
    redis.delete('foo')
    redis.sadd('foo', 'bar')
    redis.delete('foo')

    assert not redis.sismember('foo', 'bar')


def test_incr(redis):
    """Test in-memory implementation of Redis incr."""
    assert redis.incr('foo') == 1
    assert redis.incr('foo') == 2


def test_pipeline(redis):
    """Test in-memory implementation of Redis pipelining."""
    p = redis.pipeline()
    p.incr('foo').incr('bar')
    p.incr('foo')
    res = p.execute()

    assert res == [1, 1, 2]
    assert redis.incr('foo') == 3
    assert redis.incr('bar') == 2


def test_hashes(redis):
    """Test in-memory implementation of Redis hashes."""
    redis.hmset('foo', {'one': 'two', 'two': 2})
    redis.hmset('foo', {'one': 'three', 'four': 'five'})

    assert redis.hgetall('foo') == {'one': 'three', 'two': '2', 'four': 'five'}


def test_sorted_sets(redis):
    """Test in-memory implementation of Redis sorted sets."""
    redis.zadd('foo', 7, 'five')
    redis.zadd('foo', 5, 'five')
    redis.zadd('foo', 2, 'three')
    redis.zadd('foo', 3, 'three')
    redis.zadd('foo', 8, 'eight')
    redis.zadd('foo', 0, 0)

    assert redis.zrangebyscore('foo', 3, 6) == ['three', 'five']
    assert redis.zrangebyscore('foo', '-inf', '+inf') == [
        '0', 'three', 'five', 'eight']


def test_expireat(redis):
    """Test in-memory implementation of expireat."""
    with mock.patch('portfoliyo.redis.time') as mock_time:
        mock_time.return_value = 5.123
        redis.hmset('foo', {'one': 'one'})
        redis.expireat('foo', 10)
        mock_time.return_value = 11.331

        assert redis.hgetall('foo') == {}


def test_expireat_timestamp_must_be_integer(redis):
    """Expireat raises an error-"""
    redis.hmset('foo', {'one': 'one'})

    with pytest.raises(ResponseError):
        redis.expireat('foo', 10.231)
