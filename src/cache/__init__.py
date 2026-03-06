"""Cache module for Phase 4 - Distributed caching with Redis backend."""
from .redis_cache import RedisCache, get_cache, distributed_cache

__all__ = ["RedisCache", "get_cache", "distributed_cache"]
