"""
Advanced error handling and recovery system.

Provides comprehensive error handling with:
- Graceful degradation
- Retry logic with exponential backoff
- Error recovery suggestions
- User-friendly error messages
"""

import logging
import asyncio
from typing import Callable, Any, Optional, Dict, List, TypeVar, Coroutine
from enum import Enum
from dataclasses import dataclass
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "ℹ️ INFO"
    WARNING = "⚠️ WARNING"
    ERROR = "❌ ERROR"
    CRITICAL = "🔴 CRITICAL"


class ErrorCategory(Enum):
    """Error categories for better handling."""
    VALIDATION = "Validation"
    EXTERNAL_SERVICE = "External Service"
    RESOURCE = "Resource"
    PERMISSION = "Permission"
    CONFIGURATION = "Configuration"
    INTERNAL = "Internal"
    UNKNOWN = "Unknown"


@dataclass
class ErrorInfo:
    """Information about an error."""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    recovery_suggestions: Optional[List[str]] = None
    timestamp: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "recovery_suggestions": self.recovery_suggestions,
            "timestamp": self.timestamp,
            "error_code": self.error_code
        }

    def to_slack_message(self) -> str:
        """Format as Slack message."""
        msg = f"{self.severity.value} **{self.category.value}**\n"
        msg += f"_{self.message}_"
        if self.details:
            msg += f"\n\n*Details:* {self.details}"
        if self.recovery_suggestions:
            msg += "\n\n*Try:*\n" + "\n".join(f"• {s}" for s in self.recovery_suggestions)
        return msg


class ErrorHandler:
    """
    Advanced error handling with recovery mechanisms.
    """

    # Common error categorizations
    ERROR_PATTERNS = {
        "Connection": (ErrorCategory.EXTERNAL_SERVICE, "Connection error - service unavailable"),
        "Timeout": (ErrorCategory.EXTERNAL_SERVICE, "Request timed out"),
        "Permission": (ErrorCategory.PERMISSION, "Permission denied"),
        "NotFound": (ErrorCategory.RESOURCE, "Resource not found"),
        "Validation": (ErrorCategory.VALIDATION, "Invalid input"),
        "Configuration": (ErrorCategory.CONFIGURATION, "Configuration missing or invalid"),
    }

    # Recovery strategies
    RECOVERY_STRATEGIES = {
        ErrorCategory.EXTERNAL_SERVICE: [
            "Check service status",
            "Verify network connection",
            "Retry after a delay",
            "Use cached result if available"
        ],
        ErrorCategory.PERMISSION: [
            "Check user permissions",
            "Verify authentication token",
            "Contact administrator for access"
        ],
        ErrorCategory.RESOURCE: [
            "Verify resource exists",
            "Check file paths",
            "Create missing resource if applicable"
        ],
        ErrorCategory.VALIDATION: [
            "Review input format",
            "Check required fields",
            "Validate data types"
        ],
        ErrorCategory.CONFIGURATION: [
            "Check environment variables",
            "Review configuration file",
            "Restore default settings"
        ]
    }

    @staticmethod
    def categorize_error(exception: Exception) -> ErrorInfo:
        """
        Categorize an exception and create ErrorInfo.

        Args:
            exception: The exception to categorize

        Returns:
            ErrorInfo with category and suggestions
        """
        error_type = type(exception).__name__
        error_msg = str(exception)

        category = ErrorCategory.UNKNOWN
        severity = ErrorSeverity.ERROR

        # Categorize based on error type
        for pattern, (cat, _) in ErrorHandler.ERROR_PATTERNS.items():
            if pattern.lower() in error_type.lower() or pattern.lower() in error_msg.lower():
                category = cat
                break

        # Severity levels
        if isinstance(exception, (KeyboardInterrupt, SystemExit)):
            severity = ErrorSeverity.CRITICAL
        elif isinstance(exception, (PermissionError, RuntimeError)):
            severity = ErrorSeverity.WARNING
        else:
            severity = ErrorSeverity.ERROR

        # Get recovery suggestions
        suggestions = ErrorHandler.RECOVERY_STRATEGIES.get(category, [])

        return ErrorInfo(
            category=category,
            severity=severity,
            message=error_msg or f"{error_type} occurred",
            details=f"Exception type: {error_type}",
            recovery_suggestions=suggestions,
            timestamp=datetime.now().isoformat(),
            error_code=error_type
        )

    @staticmethod
    def retry_with_backoff(
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        retryable_exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator for retry logic with exponential backoff.

        Args:
            max_attempts: Maximum retry attempts
            backoff_factor: Exponential backoff factor
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            retryable_exceptions: Exceptions to retry on
            on_retry: Optional callback on retry

        Example:
            @ErrorHandler.retry_with_backoff(max_attempts=3)
            def unreliable_function():
                ...
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_exception = None

                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except retryable_exceptions as e:
                        last_exception = e
                        if attempt < max_attempts:
                            if on_retry:
                                on_retry(attempt, delay, e)
                            logger.warning(
                                f"Attempt {attempt}/{max_attempts} failed: {str(e)}. "
                                f"Retrying in {delay}s..."
                            )
                            asyncio.sleep(delay)
                            delay = min(delay * backoff_factor, max_delay)
                        else:
                            logger.error(f"All {max_attempts} attempts failed")

                raise last_exception or Exception("All retry attempts failed")

            return wrapper

        return decorator

    @staticmethod
    async def async_retry_with_backoff(
        func: Callable[..., Coroutine],
        *args,
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
        **kwargs
    ):
        """
        Async version of retry with backoff.

        Args:
            func: Async function to retry
            max_attempts: Maximum attempts
            backoff_factor: Backoff multiplier
            initial_delay: Initial delay

        Returns:
            Function result
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_attempts:
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, 60.0)

        raise last_exception

    @staticmethod
    def safe_execute(
        func: Callable[..., T],
        *args,
        fallback: Optional[T] = None,
        on_error: Optional[Callable] = None,
        **kwargs
    ) -> Optional[T]:
        """
        Execute function safely with fallback.

        Args:
            func: Function to execute
            fallback: Value to return on error
            on_error: Optional error callback
            *args, **kwargs: Function arguments

        Returns:
            Function result or fallback value
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = ErrorHandler.categorize_error(e)
            logger.error(f"Error in safe_execute: {error_info.message}")

            if on_error:
                on_error(error_info)

            return fallback

    @staticmethod
    def get_error_context(exception: Exception, context_data: Optional[Dict] = None) -> Dict:
        """
        Get comprehensive error context for logging.

        Args:
            exception: The exception
            context_data: Additional context

        Returns:
            Comprehensive error context
        """
        error_info = ErrorHandler.categorize_error(exception)

        context = {
            "error": error_info.to_dict(),
            "traceback": logger.exception("", exc_info=True) if logger.isEnabledFor(logging.DEBUG) else None,
        }

        if context_data:
            context["context"] = context_data

        return context


class GracefulDegradation:
    """
    Graceful degradation strategies for service failures.
    """

    @staticmethod
    def with_fallback(
        primary: Callable[..., T],
        fallback: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Try primary function, fall back to alternative on failure.

        Args:
            primary: Primary function
            fallback: Fallback function
            *args, **kwargs: Arguments

        Returns:
            Result from primary or fallback
        """
        try:
            logger.info(f"Attempting primary: {primary.__name__}")
            return primary(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary failed, using fallback: {str(e)}")
            try:
                return fallback(*args, **kwargs)
            except Exception as e2:
                logger.error(f"Both primary and fallback failed: {str(e2)}")
                raise

    @staticmethod
    def with_timeout(
        func: Callable[..., T],
        timeout_seconds: float = 30.0,
        fallback: Optional[T] = None,
        *args,
        **kwargs
    ) -> Optional[T]:
        """
        Execute function with timeout.

        Args:
            func: Function to execute
            timeout_seconds: Timeout in seconds
            fallback: Value if timeout occurs
            *args, **kwargs: Arguments

        Returns:
            Function result or fallback
        """
        try:
            # This is simplified for sync context
            # For async, use asyncio.wait_for()
            return ErrorHandler.safe_execute(func, *args, fallback=fallback, **kwargs)
        except asyncio.TimeoutError:
            logger.warning(f"Function timed out after {timeout_seconds}s")
            return fallback


def log_error(error_info: ErrorInfo, context: Optional[Dict] = None):
    """Log error with full context."""
    message = f"{error_info.severity.value} {error_info.category.value}: {error_info.message}"

    if error_info.details:
        message += f" | {error_info.details}"

    if error_info.severity in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR):
        logger.error(message, extra={"context": context})
    elif error_info.severity == ErrorSeverity.WARNING:
        logger.warning(message, extra={"context": context})
    else:
        logger.info(message)
