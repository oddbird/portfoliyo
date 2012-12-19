"""Tests for redis client config."""
import mock

from portfoliyo.redis import InMemoryRedis



def test_sets():
    """Test in-memory implementation of Redis sets."""
    c = InMemoryRedis()
    c.sadd('foo', 'bar')
    c.sadd('foo', 'baz')
    c.srem('foo', 'baz')
    assert c.scard('foo') == 1
    assert c.sismember('foo', 'bar')
    assert not c.sismember('foo', 'baz')
    assert c.smembers('foo') == {'bar'}


def test_delete():
    """Test in-memory implementation of Redis delete."""
    c = InMemoryRedis()
    c.delete('foo')
    c.sadd('foo', 'bar')
    c.delete('foo')

    assert not c.sismember('foo', 'bar')


def test_incr():
    """Test in-memory implementation of Redis incr."""
    c = InMemoryRedis()
    assert c.incr('foo') == 1
    assert c.incr('foo') == 2


def test_pipeline():
    """Test in-memory implementation of Redis pipelining."""
    c = InMemoryRedis()
    p = c.pipeline()
    p.incr('foo').incr('bar')
    p.incr('foo')
    res = p.execute()

    assert res == [1, 1, 2]
    assert c.incr('foo') == 3
    assert c.incr('bar') == 2


def test_hashes():
    """Test in-memory implementation of Redis hashes."""
    c = InMemoryRedis()
    c.hmset('foo', {'one': 'two', 'two': 'three'})
    c.hmset('foo', {'one': 'three', 'four': 'five'})

    assert c.hgetall('foo') == {'one': 'three', 'two': 'three', 'four': 'five'}


def test_sorted_sets():
    """Test in-memory implementation of Redis sorted sets."""
    c = InMemoryRedis()
    c.zadd('foo', 7, 'five')
    c.zadd('foo', 5, 'five')
    c.zadd('foo', 2, 'three')
    c.zadd('foo', 3, 'three')
    c.zadd('foo', 8, 'eight')
    c.zadd('foo', 0, 0)

    assert c.zrangebyscore('foo', 3, 6) == ['three', 'five']
    assert c.zrangebyscore('foo', '-inf', '+inf') == [
        '0', 'three', 'five', 'eight']


def test_expireat():
    """Test in-memory implementation of expireat."""
    c = InMemoryRedis()
    with mock.patch('portfoliyo.redis.time') as mock_time:
        mock_time.return_value = 5
        c.hmset('foo', {'one': 'one'})
        c.expireat('foo', 10)
        mock_time.return_value = 11

        assert c.hgetall('foo') == {}
