"""In-memory, thread-safe policy decision cache."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class _CacheEntry:
    value: Any
    expires_at: float


class PolicyCache:
    """TTL cache for access-control decisions.

    The cache is intentionally process-local only and never persists decisions to
    disk, so revocation exposure is bounded by the configured TTL for any entry
    that event-driven invalidation (``invalidate``/``invalidate_all`` below)
    does not reach first.
    """

    def __init__(self, ttl_seconds: float = 300, clock=time.time) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._lock = threading.RLock()
        self._entries: dict[str, _CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= self._clock():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        ttl = self.ttl_seconds if ttl_seconds is None else ttl_seconds
        if ttl <= 0:
            raise ValueError("ttl_seconds must be positive")
        with self._lock:
            self._entries[key] = _CacheEntry(value=value, expires_at=self._clock() + ttl)

    def invalidate(self, key: str, episode_id: str | None = None) -> None:
        """Drop one cached decision, for instance because a CRL event named
        the subject it belongs to.

        ``episode_id`` is the correlation token
        chaincode/hrbac-corrected/contract.go's ``RevokeRole`` and
        ``UpdateCRL`` stamp on their audit entries. Logging it here, rather
        than only performing the cache eviction silently, is what makes
        cache invalidation a joinable stage of the revocation pipeline
        instead of an unobserved side effect: see this repository's
        revocation-observability discussion for why that join previously
        did not exist.
        """
        with self._lock:
            self._entries.pop(key, None)
        if episode_id is not None:
            LOG.info("revocation cache invalidation key=%s episode_id=%s", key, episode_id)

    def invalidate_all(self, episode_id: str | None = None) -> None:
        with self._lock:
            self._entries.clear()
        if episode_id is not None:
            LOG.info("revocation cache invalidation key=* episode_id=%s", episode_id)
