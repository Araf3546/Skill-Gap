"""
Verifies the app behaves correctly whether Redis is present or absent.
"""
from src.cache.redis_client import CacheClient


def test_cache_unavailable_when_no_url():
    client = CacheClient(redis_url=None)
    assert client.is_available is False


def test_cache_get_returns_none_when_unavailable():
    client = CacheClient(redis_url=None)
    assert client.get("any-key") is None


def test_cache_set_returns_false_when_unavailable():
    client = CacheClient(redis_url=None)
    assert client.set("any-key", {"data": "value"}) is False


def test_cache_unreachable_url_degrades_gracefully():
    client = CacheClient(redis_url="redis://nonexistent-host:6379/0")
    assert client.is_available is False
    assert client.get("key") is None
    assert client.set("key", "value") is False


def test_skill_matcher_works_without_redis():
    from src.matching.skill_matcher import SkillMatcher

    matcher = SkillMatcher()
    score = matcher.calculate_similarity("Python", "Python programming")
    assert 0.0 <= score <= 1.0