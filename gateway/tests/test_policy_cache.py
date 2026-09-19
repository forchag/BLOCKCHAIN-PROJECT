import logging

from policy_cache import PolicyCache


def test_policy_cache_expiry():
    now = [100.0]
    cache = PolicyCache(ttl_seconds=5, clock=lambda: now[0])
    cache.set("k", "GRANT")
    assert cache.get("k") == "GRANT"
    now[0] = 106.0
    assert cache.get("k") is None


def test_policy_cache_invalidation():
    cache = PolicyCache(ttl_seconds=300)
    cache.set("a", "GRANT")
    cache.set("b", "DENY")
    cache.invalidate("a")
    assert cache.get("a") is None
    assert cache.get("b") == "DENY"
    cache.invalidate_all()
    assert cache.get("b") is None


def test_invalidate_logs_episode_id_when_given(caplog):
    cache = PolicyCache(ttl_seconds=300)
    cache.set("a", "GRANT")
    with caplog.at_level(logging.INFO, logger="policy_cache"):
        cache.invalidate("a", episode_id="episode-123")
    assert cache.get("a") is None
    assert any("episode-123" in record.message for record in caplog.records)


def test_invalidate_without_episode_id_logs_nothing(caplog):
    cache = PolicyCache(ttl_seconds=300)
    cache.set("a", "GRANT")
    with caplog.at_level(logging.INFO, logger="policy_cache"):
        cache.invalidate("a")
    assert cache.get("a") is None
    assert caplog.records == []


def test_invalidate_all_logs_episode_id_when_given(caplog):
    cache = PolicyCache(ttl_seconds=300)
    cache.set("a", "GRANT")
    cache.set("b", "DENY")
    with caplog.at_level(logging.INFO, logger="policy_cache"):
        cache.invalidate_all(episode_id="episode-456")
    assert cache.get("a") is None and cache.get("b") is None
    assert any("episode-456" in record.message for record in caplog.records)
