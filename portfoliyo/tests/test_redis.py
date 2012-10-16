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


def test_redis_delete():
    """Test in-memory implementation of Redis delete."""
    c = InMemoryRedis()
    c.delete('foo')
    c.sadd('foo', 'bar')
    c.delete('foo')

    assert not c.sismember('foo', 'bar')

