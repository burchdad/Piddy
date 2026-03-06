"""
Health check and monitoring system for Piddy service.

Provides real-time status, metrics, and diagnostics.
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status of the service."""
    status: str  # "healthy", "degraded", "unhealthy"
    pid: Optional[int] = None
    uptime: float = 0.0
    messages_processed: int = 0
    errors: int = 0
    last_heartbeat: Optional[str] = None
    latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    recent_errors: list = None
    checks: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.recent_errors is None:
            self.recent_errors = []
        if self.checks is None:
            self.checks = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class HealthChecker:
    """
    Monitor and report on service health.
    """
    
    def __init__(self, status_file: str = ".piddy_service_status.json"):
        self.status_file = status_file
        self.log_file = ".piddy_service.log"
    
    def check_health(self) -> HealthStatus:
        """Perform comprehensive health check."""
        start_time = time.time()
        
        health = HealthStatus(status="healthy")
        health.checks = {}
        
        # Check 1: Process running
        process_running = self._check_process_running()
        health.checks["process_running"] = process_running
        if not process_running:
            health.status = "unhealthy"
        
        # Check 2: Status file exists
        status_ok = self._check_status_file(health)
        health.checks["status_file"] = status_ok
        
        # Check 3: Recent heartbeat
        heartbeat_ok = self._check_recent_heartbeat(health)
        health.checks["recent_heartbeat"] = heartbeat_ok
        if not heartbeat_ok:
            health.status = "degraded"
        
        # Check 4: Log file accessible
        log_ok = self._check_logs_accessible()
        health.checks["logs_accessible"] = log_ok
        
        # Check 5: Memory usage
        memory_ok = self._check_memory_usage(health)
        health.checks["memory_ok"] = memory_ok
        if not memory_ok:
            health.status = "degraded"
        
        # Record latency
        health.latency_ms = (time.time() - start_time) * 1000
        
        return health
    
    def _check_process_running(self) -> bool:
        """Check if Piddy process is running."""
        try:
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "src.service.background_runner"],
                capture_output=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Failed to check process: {e}")
            return False
    
    def _check_status_file(self, health: HealthStatus) -> bool:
        """Check status file and load metrics."""
        try:
            if not Path(self.status_file).exists():
                return False
            
            with open(self.status_file, 'r') as f:
                status = json.load(f)
            
            health.uptime = status.get("uptime_seconds", 0)
            health.messages_processed = status.get("messages_processed", 0)
            health.errors = status.get("errors", 0)
            health.last_heartbeat = status.get("last_heartbeat")
            health.pid = status.get("pid")
            
            return True
        except Exception as e:
            logger.warning(f"Failed to read status file: {e}")
            return False
    
    def _check_recent_heartbeat(self, health: HealthStatus) -> bool:
        """Check if recent heartbeat exists (within 30 seconds)."""
        if not health.last_heartbeat:
            return False
        
        try:
            last_beat = datetime.fromisoformat(health.last_heartbeat)
            age = (datetime.now() - last_beat).total_seconds()
            return age < 30  # Heartbeat within 30 seconds
        except Exception:
            return False
    
    def _check_logs_accessible(self) -> bool:
        """Check if logs are accessible."""
        try:
            log_path = Path(self.log_file)
            if log_path.exists():
                with open(self.log_file, 'r') as f:
                    f.read(100)  # Read first 100 bytes
            return True
        except Exception as e:
            logger.warning(f"Log file not accessible: {e}")
            return False
    
    def _check_memory_usage(self, health: HealthStatus) -> bool:
        """Check process memory usage."""
        if not health.pid:
            return True
        
        try:
            with open(f"/proc/{health.pid}/status", 'r') as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        # VmRSS is in kB
                        memory_kb = int(line.split()[1])
                        health.memory_usage_mb = memory_kb / 1024
                        # Warn if exceeding 1GB
                        return memory_kb < (1024 * 1024)
        except Exception as e:
            logger.warning(f"Failed to check memory: {e}")
        
        return True
    
    def get_recent_errors(self, lines: int = 10) -> list:
        """Get recent errors from logs."""
        errors = []
        try:
            if not Path(self.log_file).exists():
                return errors
            
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
            
            for line in log_lines[-lines:]:
                if "ERROR" in line or "CRITICAL" in line:
                    errors.append(line.strip())
        
        except Exception as e:
            logger.warning(f"Failed to read errors: {e}")
        
        return errors
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        try:
            if not Path(self.status_file).exists():
                return {}
            
            with open(self.status_file, 'r') as f:
                status = json.load(f)
            
            uptime = status.get("uptime_seconds", 0)
            messages = status.get("messages_processed", 0)
            errors = status.get("errors", 0)
            
            # Calculate rates
            rate = (messages / uptime) if uptime > 0 else 0
            error_rate = (errors / messages * 100) if messages > 0 else 0
            
            return {
                "uptime_hours": round(uptime / 3600, 2),
                "messages_processed": messages,
                "messages_per_hour": round(rate * 3600, 2),
                "errors": errors,
                "error_rate_percent": round(error_rate, 2),
                "availability": f"{100 - error_rate:.1f}%",
            }
        except Exception as e:
            logger.warning(f"Failed to get performance summary: {e}")
            return {}


class ServiceMonitor:
    """
    Continuous monitoring of service health.
    """
    
    def __init__(self):
        self.checker = HealthChecker()
        self.history: list = []
        self.max_history = 100
    
    def record_check(self) -> HealthStatus:
        """Record a health check."""
        health = self.checker.check_health()
        
        # Add recent errors
        health.recent_errors = self.checker.get_recent_errors(lines=5)
        
        # Keep history
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "status": health.status,
            "uptime": health.uptime,
            "latency_ms": health.latency_ms,
        })
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return health
    
    def get_status_json(self) -> str:
        """Get status as JSON."""
        health = self.record_check()
        performance = self.checker.get_performance_summary()
        
        data = {
            "health": health.to_dict(),
            "performance": performance,
            "timestamp": datetime.now().isoformat(),
        }
        
        return json.dumps(data, indent=2)
    
    def get_status_dict(self) -> dict:
        """Get status as dictionary."""
        data = json.loads(self.get_status_json())
        return data


# Global monitor instance
_monitor = ServiceMonitor()


def get_monitor() -> ServiceMonitor:
    """Get global service monitor."""
    return _monitor


def check_health() -> HealthStatus:
    """Quick health check."""
    return _monitor.record_check()


def get_status() -> dict:
    """Get complete status."""
    return _monitor.get_status_dict()
