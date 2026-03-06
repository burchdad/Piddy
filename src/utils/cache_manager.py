"""
Advanced caching system for Piddy with TTL, LRU eviction, and statistics.

Provides multi-tier caching for:
- Code analysis results
- Language detection
- Pattern matching results
- Generated boilerplate
"""

import hashlib
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """Cache tier levels."""
    L1 = "memory"  # In-memory cache (fastest)
    L2 = "disk"    # Persistent cache
    NONE = "none"  # Skip cache


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    ttl: int = 3600  # seconds
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> None:
        """Record access time and increment hit count."""
        self.accessed_at = time.time()
        self.hit_count += 1


class CacheManager:
    """
    Advanced caching system with LRU eviction and multi-tier support.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of entries in memory
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "entries": 0,
        }
    
    def _make_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            self.stats["misses"] += 1
            return None
        
        entry.access()
        self.access_order.remove(key)
        self.access_order.append(key)
        self.stats["hits"] += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (uses default if None)
        """
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        entry = CacheEntry(
            value=value,
            ttl=ttl or self.default_ttl
        )
        
        if key in self.cache:
            self.access_order.remove(key)
        
        self.cache[key] = entry
        self.access_order.append(key)
        self.stats["entries"] = len(self.cache)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.access_order:
            return
        
        lru_key = self.access_order.pop(0)
        del self.cache[lru_key]
        self.stats["evictions"] += 1
    
    def delete(self, key: str) -> None:
        """Delete specific cache entry."""
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
            self.stats["entries"] = len(self.cache)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()
        self.stats["entries"] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.1f}%",
            "size_bytes": sum(
                len(str(e.value).encode()) for e in self.cache.values()
            )
        }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)


# Global cache instance
_cache_manager = CacheManager()


def cached(ttl: int = 3600, tier: CacheTier = CacheTier.L1):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        tier: Cache tier (L1=memory, L2=disk, NONE=skip)
    
    Example:
        @cached(ttl=1800)
        def analyze_code(code: str) -> Dict:
            return expensive_analysis(code)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if tier == CacheTier.NONE:
                return func(*args, **kwargs)
            
            # Generate cache key from function args
            cache_key = f"{func.__name__}:{_cache_manager._make_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = _cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache_manager.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache set for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


class AnalysisCache:
    """Specialized cache for code analysis results."""
    
    def __init__(self):
        self.manager = _cache_manager
    
    def get_analysis(self, code: str, language: str) -> Optional[Dict]:
        """Get cached analysis for code."""
        key = f"analysis:{hashlib.md5(f'{code}:{language}'.encode()).hexdigest()}"
        return self.manager.get(key)
    
    def set_analysis(self, code: str, language: str, result: Dict, ttl: int = 7200) -> None:
        """Cache analysis result."""
        key = f"analysis:{hashlib.md5(f'{code}:{language}'.encode()).hexdigest()}"
        self.manager.set(key, result, ttl=ttl)
    
    def invalidate_analysis(self, code: str, language: str) -> None:
        """Invalidate cached analysis."""
        key = f"analysis:{hashlib.md5(f'{code}:{language}'.encode()).hexdigest()}"
        self.manager.delete(key)


class PatternCache:
    """Specialized cache for pattern matching results."""
    
    def __init__(self):
        self.manager = _cache_manager
    
    def get_patterns(self, language: str, pattern_type: str) -> Optional[Dict]:
        """Get cached patterns."""
        key = f"patterns:{language}:{pattern_type}"
        return self.manager.get(key)
    
    def set_patterns(self, language: str, pattern_type: str, patterns: Dict) -> None:
        """Cache patterns."""
        key = f"patterns:{language}:{pattern_type}"
        self.manager.set(key, patterns, ttl=86400)  # 24 hours


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    return _cache_manager


def get_analysis_cache() -> AnalysisCache:
    """Get analysis cache instance."""
    return AnalysisCache()


def get_pattern_cache() -> PatternCache:
    """Get pattern cache instance."""
    return PatternCache()
