"""
In-Memory Cache Service with TTL support.

This is a simple dict-based cache for development.
Can be upgraded to Redis for production by implementing the same interface.
"""

from typing import Any, Optional, Dict
import time
import json
from dataclasses import dataclass
import asyncio
from threading import Lock


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""
    value: Any
    expires_at: float  # Unix timestamp


class MemoryCacheService:
    """
    Simple in-memory cache with TTL (Time To Live) support.

    Features:
    - TTL-based expiration
    - JSON serialization support
    - Thread-safe operations
    - Periodic cleanup of expired entries

    This provides the same interface as Redis cache, making it easy to swap later.
    """

    def __init__(self, cleanup_interval: int = 300):
        """
        Initialize memory cache.

        Args:
            cleanup_interval: Seconds between cleanup of expired entries (default: 300s = 5min)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task = None
        self._running = False

    async def start(self):
        """Start background cleanup task."""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop background cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """Background task to periodically clean up expired entries."""
        while self._running:
            try:
                await asyncio.sleep(self._cleanup_interval)
                self._remove_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cache cleanup error: {e}")

    def _remove_expired(self):
        """Remove all expired entries from cache."""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expires_at < current_time
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                print(f"Cleaned up {len(expired_keys)} expired cache entries")

    async def get(self, key: str) -> Optional[str]:
        """
        Get cached value by key.

        Args:
            key: Cache key

        Returns:
            Cached value as string, or None if not found or expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            # Check if expired
            if entry.expires_at < time.time():
                del self._cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: str, ttl: int = 3600):
        """
        Set cache value with TTL.

        Args:
            key: Cache key
            value: Value to cache (string)
            ttl: Time to live in seconds (default: 3600 = 1 hour)
        """
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at
            )

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached JSON object.

        Args:
            key: Cache key

        Returns:
            Parsed JSON dict, or None if not found or expired
        """
        value = await self.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Invalid JSON, remove from cache
            await self.delete(key)
            return None

    async def set_json(self, key: str, value: Dict[str, Any], ttl: int = 3600):
        """
        Set cache value as JSON.

        Args:
            key: Cache key
            value: Dictionary to cache
            ttl: Time to live in seconds
        """
        json_str = json.dumps(value)
        await self.set(key, json_str, ttl)

    async def delete(self, key: str):
        """
        Delete cached value.

        Args:
            key: Cache key to delete
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired, False otherwise
        """
        value = await self.get(key)
        return value is not None

    async def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (entry count, expired count, etc.)
        """
        current_time = time.time()

        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values()
                if entry.expires_at < current_time
            )

            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries,
                "cache_type": "memory"
            }


# Singleton instance for easy access
_cache_instance: Optional[MemoryCacheService] = None


def get_cache_service() -> MemoryCacheService:
    """
    Get singleton cache service instance.

    Returns:
        MemoryCacheService instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MemoryCacheService()
    return _cache_instance


# Future: Redis cache implementation (same interface)
"""
class RedisCacheService:
    '''Redis-based cache service (for production)'''

    def __init__(self, redis_url: str):
        import redis.asyncio as redis
        self.client = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600):
        await self.client.setex(key, ttl, value)

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Dict[str, Any], ttl: int = 3600):
        await self.set(key, json.dumps(value), ttl)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def clear(self):
        await self.client.flushdb()
"""
