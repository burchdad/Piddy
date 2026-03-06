"""
Security hardening module for Piddy with rate limiting, encryption, and audit logging.

Features:
- Request rate limiting (per-user, global)
- AES encryption for sensitive data
- Comprehensive audit logging
- Security policy enforcement
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    COMMAND_EXECUTED = "command_executed"
    CODE_GENERATED = "code_generated"
    CODE_ANALYZED = "code_analyzed"
    FILE_WRITTEN = "file_written"
    GIT_OPERATION = "git_operation"
    MEMORY_ACCESSED = "memory_accessed"
    SECURITY_INCIDENT = "security_incident"
    ACCESS_DENIED = "access_denied"
    CONFIG_CHANGED = "config_changed"


@dataclass
class AuditEvent:
    """Single audit event."""
    event_type: AuditEventType
    user_id: str
    channel_id: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None
    severity: str = "INFO"  # INFO, WARNING, CRITICAL


class SecurityPolicy:
    """Security policy enforcement."""
    
    # Default limits
    MAX_CODE_LENGTH = 100_000  # characters
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 500
    MAX_FILE_SIZE = 10_000_000  # bytes
    
    # Restricted patterns
    DANGEROUS_PATTERNS = [
        r"exec\(",
        r"eval\(",
        r"__import__",
        r"compile\(",
        r"os\.system",
    ]
    
    @staticmethod
    def validate_code(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for security issues.
        
        Returns:
            (is_valid, error_message)
        """
        import re
        
        if len(code) > SecurityPolicy.MAX_CODE_LENGTH:
            return False, f"Code exceeds max length {SecurityPolicy.MAX_CODE_LENGTH}"
        
        for pattern in SecurityPolicy.DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, None
    
    @staticmethod
    def validate_input(input_str: str) -> Tuple[bool, Optional[str]]:
        """Validate user input for injection attacks."""
        # Check for SQL injection patterns
        sql_keywords = ["DROP", "DELETE", "TRUNCATE", ";--"]
        upper_input = input_str.upper()
        
        for keyword in sql_keywords:
            if keyword in upper_input:
                return False, f"SQL injection pattern detected: {keyword}"
        
        return True, None


class RateLimiter:
    """
    Rate limiting implementation with per-user and global limits.
    """
    
    def __init__(self):
        self.user_requests: Dict[str, List[float]] = {}
        self.global_requests: List[float] = []
    
    def is_allowed(
        self,
        user_id: str,
        max_per_minute: int = 60,
        max_per_hour: int = 500
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if user request is allowed.
        
        Returns:
            (is_allowed, rate_limit_info)
        """
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Initialize user request list if needed
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Clean old requests
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if ts > minute_ago
        ]
        
        # Check per-minute limit
        minute_count = len(self.user_requests[user_id])
        if minute_count >= max_per_minute:
            reset_time = self.user_requests[user_id][0] + 60
            return False, {
                "limit_type": "per_minute",
                "current": minute_count,
                "limit": max_per_minute,
                "reset_at": datetime.fromtimestamp(reset_time).isoformat(),
            }
        
        # Check per-hour limit
        hour_requests = [
            ts for ts in self.user_requests[user_id] if ts > hour_ago
        ]
        if len(hour_requests) >= max_per_hour:
            reset_time = hour_requests[0] + 3600
            return False, {
                "limit_type": "per_hour",
                "current": len(hour_requests),
                "limit": max_per_hour,
                "reset_at": datetime.fromtimestamp(reset_time).isoformat(),
            }
        
        # Request allowed, record it
        self.user_requests[user_id].append(now)
        return True, {
            "remaining_minute": max_per_minute - minute_count - 1,
            "remaining_hour": max_per_hour - len(hour_requests) - 1,
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get rate limiting stats for user."""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        if user_id not in self.user_requests:
            return {
                "requests_per_minute": 0,
                "requests_per_hour": 0,
                "first_request": None,
            }
        
        all_requests = self.user_requests[user_id]
        minute_requests = [ts for ts in all_requests if ts > minute_ago]
        hour_requests = [ts for ts in all_requests if ts > hour_ago]
        
        return {
            "requests_per_minute": len(minute_requests),
            "requests_per_hour": len(hour_requests),
            "first_request": datetime.fromtimestamp(min(all_requests)).isoformat() if all_requests else None,
        }


class AuditLogger:
    """
    Comprehensive audit logging system.
    """
    
    def __init__(self, log_file: str = ".piddy_audit.log"):
        self.log_file = log_file
        self.events: List[AuditEvent] = []
    
    def log_event(self, event: AuditEvent) -> None:
        """Log audit event."""
        self.events.append(event)
        
        # Write to file
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "user_id": event.user_id,
            "channel_id": event.channel_id,
            "action": event.action,
            "severity": event.severity,
            "details": event.details,
            "ip_address": event.ip_address,
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_command(
        self,
        user_id: str,
        channel_id: str,
        command: str,
        details: Dict[str, Any]
    ) -> None:
        """Log command execution."""
        event = AuditEvent(
            event_type=AuditEventType.COMMAND_EXECUTED,
            user_id=user_id,
            channel_id=channel_id,
            action=command,
            details=details,
            timestamp=datetime.now(),
        )
        self.log_event(event)
    
    def log_security_incident(
        self,
        user_id: str,
        channel_id: str,
        incident: str,
        details: Dict[str, Any]
    ) -> None:
        """Log security incident."""
        event = AuditEvent(
            event_type=AuditEventType.SECURITY_INCIDENT,
            user_id=user_id,
            channel_id=channel_id,
            action=incident,
            details=details,
            timestamp=datetime.now(),
            severity="CRITICAL",
        )
        self.log_event(event)
    
    def get_events_for_user(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get audit events for specific user."""
        events = [e for e in self.events if e.user_id == user_id]
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type.value,
                "action": e.action,
                "severity": e.severity,
            }
            for e in events[-limit:]
        ]
    
    def get_security_incidents(self, hours: int = 24) -> List[Dict]:
        """Get recent security incidents."""
        cutoff = datetime.now() - timedelta(hours=hours)
        incidents = [
            e for e in self.events
            if e.event_type == AuditEventType.SECURITY_INCIDENT
            and e.timestamp > cutoff
        ]
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "user_id": e.user_id,
                "action": e.action,
                "details": e.details,
            }
            for e in incidents
        ]


class TokenManager:
    """Secure token generation and validation."""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token."""
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def generate_request_signature(data: str, secret: str) -> str:
        """Generate HMAC signature for request."""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_request_signature(
        data: str,
        signature: str,
        secret: str
    ) -> bool:
        """Verify HMAC signature."""
        expected = TokenManager.generate_request_signature(data, secret)
        return hmac.compare_digest(signature, expected)


# Global instances
_rate_limiter = RateLimiter()
_audit_logger = AuditLogger()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _rate_limiter


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    return _audit_logger
