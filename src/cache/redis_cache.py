"""
Distributed caching system with Redis backend for Phase 4.
Provides distributed cache management for multi-instance Piddy deployments.
"""
import redis
import json
import logging
import time
from typing import Any, Optional, Dict, List
from functools import wraps
import hashlib
import pickle
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Distributed cache using Redis backend.
    Supports multi-instance Piddy deployments with shared cache.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,
        max_connections: int = 50,
    ):
        """
        Initialize Redis cache connection pool.

        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            default_ttl: Default time-to-live in seconds
            max_connections: Maximum connection pool size
        """
        self.default_ttl = default_ttl
        self.host = host
        self.port = port
        self.db = db

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                max_connections=max_connections,
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis cache connected to {host}:{port}")
            self.connected = True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using fallback in-memory cache.")
            self.redis_client = None
            self.connected = False
            self.fallback_cache: Dict[str, Any] = {}

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """
        Set a value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (uses default_ttl if None)
            namespace: Cache namespace for isolation

        Returns:
            True if successful, False otherwise
        """
        ttl = ttl or self.default_ttl
        full_key = f"{namespace}:{key}"

        try:
            # Try to serialize as JSON first (efficient for common types)
            try:
                json_value = json.dumps(value)
                if self.connected and self.redis_client:
                    self.redis_client.setex(full_key, ttl, json_value)
                else:
                    self.fallback_cache[full_key] = (value, time.time() + ttl)
                logger.debug(f"Cache set: {full_key} (TTL: {ttl}s)")
                return True
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects
                pickled = pickle.dumps(value)
                if self.connected and self.redis_client:
                    self.redis_client.setex(full_key, ttl, pickled)
                else:
                    self.fallback_cache[full_key] = (value, time.time() + ttl)
                return True
        except Exception as e:
            logger.error(f"Cache set error for {full_key}: {e}")
            return False

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key
            namespace: Cache namespace

        Returns:
            Cached value or None if not found/expired
        """
        full_key = f"{namespace}:{key}"

        try:
            if self.connected and self.redis_client:
                value = self.redis_client.get(full_key)
                if value is None:
                    return None

                # Try to parse as JSON first
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fall back to unpickling
                    try:
                        return pickle.loads(value.encode() if isinstance(value, str) else value)
                    except:
                        return value
            else:
                # Fallback cache
                if full_key in self.fallback_cache:
                    value, expiry = self.fallback_cache[full_key]
                    if time.time() < expiry:
                        return value
                    else:
                        del self.fallback_cache[full_key]
                return None
        except Exception as e:
            logger.error(f"Cache get error for {full_key}: {e}")
            return None

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete a cache entry."""
        full_key = f"{namespace}:{key}"
        try:
            if self.connected and self.redis_client:
                self.redis_client.delete(full_key)
            else:
                self.fallback_cache.pop(full_key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {full_key}: {e}")
            return False

    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        try:
            if self.connected and self.redis_client:
                pattern = f"{namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Fallback cache
                count = 0
                for key in list(self.fallback_cache.keys()):
                    if key.startswith(f"{namespace}:"):
                        del self.fallback_cache[key]
                        count += 1
                return count
        except Exception as e:
            logger.error(f"Namespace clear error: {e}")
            return 0

    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if a key exists in cache."""
        full_key = f"{namespace}:{key}"
        try:
            if self.connected and self.redis_client:
                return self.redis_client.exists(full_key) > 0
            else:
                return full_key in self.fallback_cache
        except Exception as e:
            logger.error(f"Exists check error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.connected and self.redis_client:
                info = self.redis_client.info()
                return {
                    "status": "connected",
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands": info.get("total_commands_processed", 0),
                }
            else:
                return {
                    "status": "fallback",
                    "entries": len(self.fallback_cache),
                    "message": "Using in-memory fallback cache",
                }
        except Exception as e:
            logger.error(f"Stats retrieval error: {e}")
            return {"status": "error", "message": str(e)}

    def increment(self, key: str, amount: int = 1, namespace: str = "default") -> int:
        """Increment a numeric value in cache."""
        full_key = f"{namespace}:{key}"
        try:
            if self.connected and self.redis_client:
                return self.redis_client.incrby(full_key, amount)
            else:
                if full_key not in self.fallback_cache or self.fallback_cache[full_key][1] < time.time():
                    value = 0
                else:
                    value = self.fallback_cache[full_key][0]
                value += amount
                self.fallback_cache[full_key] = (value, time.time() + self.default_ttl)
                return value
        except Exception as e:
            logger.error(f"Increment error: {e}")
            return 0


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        import os
        _cache_instance = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            default_ttl=int(os.getenv("CACHE_TTL", "3600")),
        )
    return _cache_instance


def distributed_cache(
    namespace: str = "function",
    ttl: Optional[int] = None,
):
    """
    Decorator for distributed caching of function results.
    Works with multi-instance deployments via Redis.

    Args:
        namespace: Cache namespace for organization
        ttl: Time-to-live in seconds

    Usage:
        @distributed_cache(namespace="code_analysis", ttl=3600)
        def analyze_code(code: str) -> Dict:
            # analysis logic
            return result
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function name, args, and kwargs
            cache_key_parts = [func.__name__]
            cache_key_parts.extend(str(arg) for arg in args)
            cache_key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5("".join(cache_key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get(cache_key, namespace=namespace)
            if cached_value is not None:
                logger.debug(f"Cache hit: {func.__name__}")
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, namespace=namespace)
            logger.debug(f"Cached result: {func.__name__}")

            return result

        return wrapper

    return decorator
