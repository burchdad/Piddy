"""
Advanced rate limiting with token bucket algorithm for Phase 5.
Sophisticated rate limiting for API protection and resource management.
"""
import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_tokens: int  # Bucket capacity
    refill_rate: float  # Tokens per second
    window_size: int = 60  # Seconds for rate limit window


class TokenBucket:
    """
    Token bucket algorithm for rate limiting.
    Allows for burst traffic while maintaining average rate limits.
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize token bucket."""
        self.config = config
        self.tokens = config.max_tokens  # Start with full bucket
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time and refill rate."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.config.refill_rate

        self.tokens = min(
            self.config.max_tokens,
            self.tokens + tokens_to_add
        )
        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens available, False otherwise
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_available_tokens(self) -> float:
        """Get current available tokens."""
        self._refill()
        return self.tokens

    def get_reset_time(self) -> float:
        """Get time until bucket refills to max capacity."""
        self._refill()
        if self.tokens >= self.config.max_tokens:
            return 0

        needed = self.config.max_tokens - self.tokens
        return needed / self.config.refill_rate


class AdvancedRateLimiter:
    """
    Advanced rate limiting system using token bucket algorithm.
    Supports per-user, per-IP, and per-endpoint rate limits.
    """

    def __init__(self):
        """Initialize rate limiter."""
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.ip_buckets: Dict[str, TokenBucket] = {}
        self.endpoint_buckets: Dict[str, TokenBucket] = {}

        # Presets for different use cases
        self.presets = {
            "strict": RateLimitConfig(max_tokens=10, refill_rate=1.0),  # 10 per second
            "normal": RateLimitConfig(max_tokens=100, refill_rate=10.0),  # 100 per second
            "generous": RateLimitConfig(max_tokens=1000, refill_rate=100.0),  # 1000 per second
            "burst": RateLimitConfig(max_tokens=500, refill_rate=50.0),  # 500 per second with bursts
        }

        # Rate limit stats
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "denied_requests": 0,
            "users_limited": 0,
            "ips_limited": 0,
        }

        logger.info("✅ Advanced Rate Limiter initialized")

    def check_user_limit(self, user_id: str, limit_preset: str = "normal") -> Dict[str, Any]:
        """
        Check rate limit for a user.

        Args:
            user_id: User identifier
            limit_preset: Preset to use (strict, normal, generous, burst)

        Returns:
            Dict with allowed status and metadata
        """
        self.stats["total_requests"] += 1

        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(self.presets[limit_preset])

        bucket = self.user_buckets[user_id]
        allowed = bucket.consume()

        if allowed:
            self.stats["allowed_requests"] += 1
        else:
            self.stats["denied_requests"] += 1
            self.stats["users_limited"] += 1

        return {
            "allowed": allowed,
            "user_id": user_id,
            "available_tokens": bucket.get_available_tokens(),
            "reset_seconds": bucket.get_reset_time(),
            "limit_preset": limit_preset,
        }

    def check_ip_limit(self, ip_address: str, limit_preset: str = "normal") -> Dict[str, Any]:
        """Check rate limit for an IP address."""
        self.stats["total_requests"] += 1

        if ip_address not in self.ip_buckets:
            self.ip_buckets[ip_address] = TokenBucket(self.presets[limit_preset])

        bucket = self.ip_buckets[ip_address]
        allowed = bucket.consume()

        if allowed:
            self.stats["allowed_requests"] += 1
        else:
            self.stats["denied_requests"] += 1
            self.stats["ips_limited"] += 1

        return {
            "allowed": allowed,
            "ip_address": ip_address,
            "available_tokens": bucket.get_available_tokens(),
            "reset_seconds": bucket.get_reset_time(),
            "limit_preset": limit_preset,
        }

    def check_endpoint_limit(self, endpoint: str, limit_preset: str = "generous") -> Dict[str, Any]:
        """Check rate limit for an endpoint."""
        self.stats["total_requests"] += 1

        if endpoint not in self.endpoint_buckets:
            self.endpoint_buckets[endpoint] = TokenBucket(self.presets[limit_preset])

        bucket = self.endpoint_buckets[endpoint]
        allowed = bucket.consume()

        if allowed:
            self.stats["allowed_requests"] += 1
        else:
            self.stats["denied_requests"] += 1

        return {
            "allowed": allowed,
            "endpoint": endpoint,
            "available_tokens": bucket.get_available_tokens(),
            "reset_seconds": bucket.get_reset_time(),
            "limit_preset": limit_preset,
        }

    def check_burst_limit(
        self,
        identifier: str,
        cost: float = 1.0,
        burst_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Check rate limit with custom burst token cost.
        Useful for variable-cost operations.

        Args:
            identifier: User/IP/endpoint identifier
            cost: Token cost of this operation
            burst_size: Bucket size for bursts

        Returns:
            Dict with allowed status
        """
        if identifier not in self.user_buckets:
            config = RateLimitConfig(max_tokens=burst_size, refill_rate=burst_size / 60)
            self.user_buckets[identifier] = TokenBucket(config)

        bucket = self.user_buckets[identifier]
        allowed = bucket.consume(cost)

        return {
            "allowed": allowed,
            "identifier": identifier,
            "cost": cost,
            "available_tokens": bucket.get_available_tokens(),
            "reset_seconds": bucket.get_reset_time(),
        }

    def get_limit_status(self, identifier: str, identifier_type: str = "user") -> Dict[str, Any]:
        """Get current rate limit status for an identifier."""
        if identifier_type == "user":
            bucket = self.user_buckets.get(identifier)
        elif identifier_type == "ip":
            bucket = self.ip_buckets.get(identifier)
        elif identifier_type == "endpoint":
            bucket = self.endpoint_buckets.get(identifier)
        else:
            return {"error": "Invalid identifier type"}

        if not bucket:
            return {
                "available": 0,
                "limited": False,
                "message": f"No {identifier_type} record found"
            }

        return {
            "available_tokens": bucket.get_available_tokens(),
            "max_tokens": bucket.config.max_tokens,
            "refill_rate": bucket.config.refill_rate,
            "reset_seconds": bucket.get_reset_time(),
            "limited": bucket.get_available_tokens() < 1,
        }

    def reset_limit(self, identifier: str, identifier_type: str = "user") -> bool:
        """Reset rate limit for an identifier."""
        if identifier_type == "user":
            self.user_buckets.pop(identifier, None)
        elif identifier_type == "ip":
            self.ip_buckets.pop(identifier, None)
        elif identifier_type == "endpoint":
            self.endpoint_buckets.pop(identifier, None)
        else:
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        total = self.stats["total_requests"]
        allowed = self.stats["allowed_requests"]
        denied = self.stats["denied_requests"]

        return {
            "total_requests": total,
            "allowed_requests": allowed,
            "denied_requests": denied,
            "allow_rate": (allowed / total * 100) if total > 0 else 0,
            "deny_rate": (denied / total * 100) if total > 0 else 0,
            "active_users": len(self.user_buckets),
            "active_ips": len(self.ip_buckets),
            "active_endpoints": len(self.endpoint_buckets),
            "users_limited": self.stats["users_limited"],
            "ips_limited": self.stats["ips_limited"],
        }

    def get_preset_info(self) -> Dict[str, Dict]:
        """Get information about available presets."""
        return {
            name: {
                "max_tokens": preset.max_tokens,
                "refill_rate": preset.refill_rate,
                "tokens_per_second": preset.refill_rate,
                "description": f"{preset.max_tokens} tokens, {preset.refill_rate} refill rate",
            }
            for name, preset in self.presets.items()
        }

    def estimate_retry_after(self, identifier: str, identifier_type: str = "user") -> int:
        """Estimate seconds until next request should be allowed."""
        status = self.get_limit_status(identifier, identifier_type)
        return int(status.get("reset_seconds", 0)) + 1


# Global rate limiter instance
_rate_limiter_instance: Optional[AdvancedRateLimiter] = None


def get_rate_limiter() -> AdvancedRateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = AdvancedRateLimiter()
    return _rate_limiter_instance
