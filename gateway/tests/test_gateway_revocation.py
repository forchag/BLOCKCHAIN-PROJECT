"""Tests for Gateway.handle_revocation, the event-driven cache-invalidation
hook added to close the gap where PolicyCache.invalidate/invalidate_all had
no caller anywhere in this codebase (see gateway.py's docstring for
handle_revocation)."""

import logging

from fabric_client import FabricClient
from gateway import Gateway
from lora_rx import LoRaReceiver
from policy_cache import PolicyCache


def make_gateway(policy_cache: PolicyCache) -> Gateway:
    return Gateway(
        zone="North",
        fabric_client=FabricClient(invoker=lambda *_a, **_k: {"decision": "GRANT"}),
        policy_cache=policy_cache,
        lora_receiver=LoRaReceiver(packet_sources=()),
    )


def test_handle_revocation_clears_cached_decisions():
    cache = PolicyCache(ttl_seconds=300)
    cache.set("sensor-1:North:submit_reading", "GRANT")
    gateway = make_gateway(cache)

    gateway.handle_revocation()

    assert cache.get("sensor-1:North:submit_reading") is None


def test_handle_revocation_logs_episode_id_for_correlation(caplog):
    cache = PolicyCache(ttl_seconds=300)
    cache.set("sensor-1:North:submit_reading", "GRANT")
    gateway = make_gateway(cache)

    with caplog.at_level(logging.INFO, logger="policy_cache"):
        gateway.handle_revocation(episode_id="revoke-usr-0048-1735689600")

    assert cache.get("sensor-1:North:submit_reading") is None
    assert any(
        "revoke-usr-0048-1735689600" in record.message for record in caplog.records
    )
