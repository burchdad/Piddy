"""
Advanced rate limiter with request throttling and monitoring.

Features:
- Per-provider rate limit tracking (Claude, GPT-4o, GitHub, Slack)
- Request queuing and throttling
- Adaptive backoff with exponential curves
- Rate limit monitoring and dashboarding
- Configurable thresholds
- Request prioritization
- Recovery strategies
"""

import time
import logging
import asyncio
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading


logger = logging.getLogger(__name__)


class Provider(Enum):
    """Supported API providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GITHUB = "github"
    SLACK = "slack"


class RequestPriority(Enum):
    """Request priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Request limits
    requests_per_minute: int = 60
    requests_per_hour: int = 500
    
    # Backoff strategy
    initial_backoff_seconds: int = 30
    max_backoff_seconds: int = 600
    backoff_multiplier: float = 2.0
    
    # Queue settings
    max_queue_size: int = 100
    queue_process_interval: float = 1.0  # seconds between processing queue
    
    # Recovery
    error_threshold: int = 3
    recovery_wait_minutes: int = 5
    
    # Monitoring
    track_metrics: bool = True
    metrics_window_minutes: int = 60


@dataclass
class RateLimitMetrics:
    """Metrics for a provider's rate limit status."""
    provider: Provider
    requests_in_window: int = 0
    errors_in_window: int = 0
    total_errors: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    backoff_until: float = 0.0
    backoff_count: int = 0
    recovery_until: float = 0.0
    queue_length: int = 0
    throughput_per_min: float = 0.0
    success_rate: float = 100.0
    last_request_time: Optional[datetime] = None
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if provider is currently rate limited."""
        return self.backoff_until > time.time()
    
    @property
    def is_in_recovery(self) -> bool:
        """Check if provider is in recovery mode."""
        return self.recovery_until > time.time()
    
    @property
    def time_until_available(self) -> float:
        """Get seconds until provider is available."""
        if self.is_rate_limited:
            return self.backoff_until - time.time()
        return 0.0


@dataclass
class QueuedRequest:
    """A request waiting to be processed."""
    request_id: str
    provider: Provider
    priority: RequestPriority = RequestPriority.NORMAL
    callback: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def age_seconds(self) -> float:
        """Get age of request in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class RateLimiter:
    """Advanced rate limiter with throttling and monitoring."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter."""
        self.config = config or RateLimitConfig()
        self._metrics: Dict[Provider, RateLimitMetrics] = {
            provider: RateLimitMetrics(provider=provider)
            for provider in Provider
        }
        self._request_queue: deque = deque(maxlen=self.config.max_queue_size)
        self._request_timestamps: Dict[Provider, deque] = {
            provider: deque(maxlen=self.config.requests_per_minute * 2)
            for provider in Provider
        }
        self._lock = threading.Lock()
        self._processing = False
        self._request_counter = 0
        logger.info(f"RateLimiter initialized with config: {self.config}")
    
    def can_make_request(self, provider: Provider) -> bool:
        """Check if a request can be made to provider immediately."""
        metrics = self._metrics[provider]
        
        # Check backoff
        if metrics.is_rate_limited:
            logger.debug(f"{provider.value} is backoff: {metrics.time_until_available:.1f}s remaining")
            return False
        
        # Check recovery
        if metrics.is_in_recovery:
            logger.debug(f"{provider.value} is in recovery")
            return False
        
        # Check rate limits
        if not self._check_rate_limits(provider):
            return False
        
        return True
    
    def _check_rate_limits(self, provider: Provider) -> bool:
        """Check per-minute and per-hour limits."""
        now = time.time()
        timestamps = self._request_timestamps[provider]
        
        # Clean old timestamps
        while timestamps and timestamps[0] + 3600 < now:
            timestamps.popleft()
        
        # Check per-hour limit
        if len(timestamps) >= self.config.requests_per_hour:
            logger.warning(f"{provider.value} hit hourly limit: {len(timestamps)} requests")
            self._record_rate_limit_error(provider, "hourly_limit")
            return False
        
        # Check per-minute limit
        minute_ago = now - 60
        recent = sum(1 for ts in timestamps if ts > minute_ago)
        if recent >= self.config.requests_per_minute:
            logger.warning(f"{provider.value} hit minute limit: {recent} requests in last 60s")
            self._record_rate_limit_error(provider, "minute_limit")
            return False
        
        return True
    
    async def queue_request(
        self,
        provider: Provider,
        callback: Optional[Callable] = None,
        priority: RequestPriority = RequestPriority.NORMAL,
        request_id: Optional[str] = None
    ) -> str:
        """Queue a request for processing."""
        if request_id is None:
            self._request_counter += 1
            request_id = f"{provider.value}_{self._request_counter}_{int(time.time() * 1000)}"
        
        request = QueuedRequest(
            request_id=request_id,
            provider=provider,
            priority=priority,
            callback=callback
        )
        
        with self._lock:
            self._request_queue.append(request)
            self._metrics[provider].queue_length = len(self._request_queue)
        
        logger.debug(f"Queued request {request_id} for {provider.value}")
        return request_id
    
    async def wait_for_availability(self, provider: Provider, timeout: float = 600) -> bool:
        """Wait until a request can be made to provider."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.can_make_request(provider):
                return True
            
            # Wait a bit before checking again
            await asyncio.sleep(min(2.0, self.config.queue_process_interval))
        
        logger.error(f"Timeout waiting for {provider.value} availability")
        return False
    
    def record_success(self, provider: Provider):
        """Record a successful request."""
        with self._lock:
            metrics = self._metrics[provider]
            metrics.last_request_time = datetime.now()
            
            # Add timestamp
            self._request_timestamps[provider].append(time.time())
            
            # Clear rate limit if recovered
            if metrics.is_rate_limited:
                if metrics.backoff_until <= time.time():
                    metrics.backoff_until = 0.0
                    metrics.backoff_count = 0
                    logger.info(f"{provider.value} recovered from rate limit")
            
            # Reduce error count on success
            if metrics.backoff_count > 0:
                metrics.backoff_count = max(0, metrics.backoff_count - 1)
            
            self._update_metrics(provider)
    
    def record_rate_limit_error(
        self,
        provider: Provider,
        error_msg: str = "",
        retry_after_seconds: Optional[int] = None
    ):
        """Record a rate limit error."""
        self._record_rate_limit_error(provider, error_msg, retry_after_seconds)
    
    def _record_rate_limit_error(
        self,
        provider: Provider,
        error_msg: str = "",
        retry_after_seconds: Optional[int] = None
    ):
        """Internal method to record rate limit error."""
        with self._lock:
            metrics = self._metrics[provider]
            metrics.total_errors += 1
            metrics.last_error = error_msg
            metrics.last_error_time = datetime.now()
            
            # Calculate backoff
            if retry_after_seconds:
                backoff_seconds = retry_after_seconds
            else:
                backoff_seconds = min(
                    self.config.initial_backoff_seconds * (self.config.backoff_multiplier ** metrics.backoff_count),
                    self.config.max_backoff_seconds
                )
            
            metrics.backoff_until = time.time() + backoff_seconds
            metrics.backoff_count += 1
            
            logger.warning(
                f"{provider.value} rate limited. "
                f"Backing off {backoff_seconds:.0f}s. "
                f"Error count: {metrics.backoff_count}. "
                f"Message: {error_msg}"
            )
            
            # Enter recovery mode after too many errors
            if metrics.backoff_count >= self.config.error_threshold:
                metrics.recovery_until = time.time() + (self.config.recovery_wait_minutes * 60)
                logger.error(
                    f"{provider.value} entering recovery mode for {self.config.recovery_wait_minutes} minutes"
                )
            
            self._update_metrics(provider)
    
    def record_general_error(self, provider: Provider, error_msg: str = ""):
        """Record a general error (not rate limit)."""
        with self._lock:
            metrics = self._metrics[provider]
            metrics.errors_in_window += 1
            metrics.last_error = error_msg
            metrics.last_error_time = datetime.now()
            self._update_metrics(provider)
    
    def _update_metrics(self, provider: Provider):
        """Update throughput and success metrics."""
        metrics = self._metrics[provider]
        
        # Calculate throughput
        now = time.time()
        minute_ago = now - 60
        timestamps = self._request_timestamps[provider]
        recent_requests = sum(1 for ts in timestamps if ts > minute_ago)
        metrics.throughput_per_min = float(recent_requests)
        
        # Calculate success rate
        total = max(1, metrics.requests_in_window + metrics.errors_in_window)
        metrics.success_rate = 100.0 * metrics.requests_in_window / total
    
    def get_metrics(self, provider: Optional[Provider] = None) -> Dict[str, Any]:
        """Get rate limit metrics."""
        with self._lock:
            if provider:
                return self._metrics_to_dict(self._metrics[provider])
            
            return {
                "providers": {
                    p.value: self._metrics_to_dict(metrics)
                    for p, metrics in self._metrics.items()
                },
                "queue_length": len(self._request_queue),
                "timestamp": datetime.now().isoformat()
            }
    
    def _metrics_to_dict(self, metrics: RateLimitMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "provider": metrics.provider.value,
            "is_rate_limited": metrics.is_rate_limited,
            "is_in_recovery": metrics.is_in_recovery,
            "time_until_available": max(0, metrics.time_until_available),
            "backoff_count": metrics.backoff_count,
            "total_errors": metrics.total_errors,
            "last_error": metrics.last_error,
            "throughput_per_min": metrics.throughput_per_min,
            "success_rate": metrics.success_rate,
            "queue_length": metrics.queue_length,
            "last_request": metrics.last_request_time.isoformat() if metrics.last_request_time else None,
            "last_error_time": metrics.last_error_time.isoformat() if metrics.last_error_time else None,
        }
    
    def reset_metrics(self, provider: Optional[Provider] = None):
        """Reset metrics for a provider."""
        with self._lock:
            if provider:
                self._metrics[provider] = RateLimitMetrics(provider=provider)
                logger.info(f"Reset metrics for {provider.value}")
            else:
                for p in Provider:
                    self._metrics[p] = RateLimitMetrics(provider=p)
                logger.info("Reset metrics for all providers")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health from rate limit perspective."""
        with self._lock:
            healthy_count = sum(
                1 for m in self._metrics.values()
                if not m.is_rate_limited and not m.is_in_recovery
            )
            
            return {
                "status": "healthy" if healthy_count == len(self._metrics) else "degraded",
                "healthy_providers": healthy_count,
                "total_providers": len(self._metrics),
                "queue_length": len(self._request_queue),
                "providers": {
                    p.value: {
                        "available": not m.is_rate_limited and not m.is_in_recovery,
                        "backoff_active": m.is_rate_limited,
                        "recovery_active": m.is_in_recovery,
                    }
                    for p, m in self._metrics.items()
                }
            }


# Global rate limiter instance
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()
    return _global_rate_limiter


def configure_rate_limiter(config: RateLimitConfig) -> RateLimiter:
    """Configure and return global rate limiter."""
    global _global_rate_limiter
    _global_rate_limiter = RateLimiter(config)
    return _global_rate_limiter
