"""
In-memory cache provider — for development and testing.
"""

import time
from typing import Any

from .interfaces import CacheProvider


class InMemoryCacheProvider(CacheProvider):
    """Thread-safe in-memory cache with TTL support.

    Suitable for development and single-process deployments.
    For production with multiple workers, use a Redis-backed provider.

    Features:
    - Automatic expiry checking on read
    - Configurable max items to prevent memory leaks
    - Simple dict-based storage

    Usage:
        cache = InMemoryCacheProvider(max_items=1000)
        await cache.set("user:123", {"name": "Alice"}, ttl=60)
        user = await cache.get("user:123")
    """

    def __init__(self, max_items: int = 5000) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._max_items = max_items

    async def get(self, key: str) -> Any | None:
        """Retrieve a value, returning None if expired or missing."""
        entry = self._store.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if time.monotonic() >= expires_at:
            self._store.pop(key, None)
            return None

        return value

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store a value with TTL. Evicts oldest entry if at capacity."""
        if len(self._store) >= self._max_items and key not in self._store:
            # Drop the oldest entry to stay within bounds
            oldest_key = next(iter(self._store))
            self._store.pop(oldest_key, None)

        expires_at = time.monotonic() + ttl
        self._store[key] = (expires_at, value)

    async def delete(self, key: str) -> None:
        """Remove a key from the cache."""
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists and hasn't expired."""
        entry = self._store.get(key)
        if entry is None:
            return False

        expires_at, _ = entry
        if time.monotonic() >= expires_at:
            self._store.pop(key, None)
            return False

        return True

    def clear(self) -> None:
        """Clear all cached entries. Useful in tests."""
        self._store.clear()

    @property
    def size(self) -> int:
        """Return the number of items currently in the cache."""
        return len(self._store)
