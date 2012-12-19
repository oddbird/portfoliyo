"""Tests for redis client config."""
from portfoliyo.redis import InMemoryRedis



def test_redis_sets():
    """Test in-memory implementation of Redis sets."""
    c = InMemoryRedis()
    c.sadd('foo', 'bar')
    c.sadd('foo', 'baz')
    c.srem('foo', 'baz')
    assert c.scard('foo') == 1
    assert c.sismember('foo', 'bar')
    assert not c.sismember('foo', 'baz')
    assert c.smembers('foo') == {'bar'}


def test_redis_delete():
    """Test in-memory implementation of Redis delete."""
    c = InMemoryRedis()
    c.delete('foo')
    c.sadd('foo', 'bar')
    c.delete('foo')

    assert not c.sismember('foo', 'bar')


def test_redis_incr():
    """Test in-memory implementation of Redis incr."""
    c = InMemoryRedis()
    assert c.incr('foo') == 1
    assert c.incr('foo') == 2


def test_redis_pipeline():
    """Test in-memory faking of redis pipelining."""
    c = InMemoryRedis()
    p = c.pipeline()
    p.incr('foo')
    p.execute()

    assert c.incr('foo') == 2
