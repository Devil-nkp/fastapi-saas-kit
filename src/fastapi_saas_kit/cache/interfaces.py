"""
Cache interfaces — abstract base class for pluggable cache providers.
"""

from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    """Abstract interface for cache providers.

    Implement this interface to integrate your preferred cache backend
    (e.g., Redis, Memcached, DynamoDB, etc.).

    The boilerplate ships with an InMemoryCacheProvider for development
    and testing. For production, implement a Redis-backed provider.

    Example:
        class RedisCacheProvider(CacheProvider):
            def __init__(self, redis_client):
                self._client = redis_client

            async def get(self, key: str) -> Any | None:
                value = await self._client.get(key)
                return json.loads(value) if value else None

            async def set(self, key: str, value: Any, ttl: int = 300) -> None:
                await self._client.setex(key, ttl, json.dumps(value))

            async def delete(self, key: str) -> None:
                await self._client.delete(key)

            async def exists(self, key: str) -> bool:
                return await self._client.exists(key)
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found or expired.
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache (must be serializable).
            ttl: Time-to-live in seconds (default: 5 minutes).
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a value from the cache.

        Args:
            key: The cache key to delete.
        """
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            True if the key exists and hasn't expired.
        """
        ...
