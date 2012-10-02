"""Tests for redis client config."""
from portfoliyo import redis



def test_redis_client_exists():
    """Redis client instantiated, can connect."""
    redis.client.set('foo', 'bar')
    assert redis.client.get('foo') == 'bar'
