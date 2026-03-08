"""Cache module for Phase 4 - Distributed caching with Redis backend."""
from .redis_cache import RedisCache, get_cache, distributed_cache
import logging

logger = logging.getLogger(__name__)
__all__ = ["RedisCache", "get_cache", "distributed_cache"]
