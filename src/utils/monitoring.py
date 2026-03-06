"""
Monitoring and metrics system for Piddy.

Tracks:
- Tool execution metrics
- Agent performance
- Error rates and types
- Code generation quality
- System health
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"  # Incrementing value
    GAUGE = "gauge"      # Current value
    HISTOGRAM = "histogram"  # Distribution
    TIMER = "timer"      # Elapsed time


@dataclass
class Metric:
    """Single metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collect and aggregate metrics for monitoring and analysis.
    """
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.aggregates: Dict[str, Dict] = defaultdict(dict)
        self.timers: Dict[str, float] = {}
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> None:
        """Increment counter metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self.metrics.append(metric)
        
        # Aggregate
        key = f"{name}:{str(tags)}"
        if "total" not in self.aggregates[key]:
            self.aggregates[key] = {"total": 0, "count": 0}
        self.aggregates[key]["total"] += value
        self.aggregates[key]["count"] += 1
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Set gauge metric (current value)."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {}
        )
        self.metrics.append(metric)
        
        key = f"{name}:{str(tags)}"
        self.aggregates[key] = {
            "last_value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def start_timer(self, name: str) -> str:
        """Start a timer, returns timer ID."""
        timer_id = f"{name}:{time.time()}"
        self.timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str, tags: Dict[str, str] = None) -> float:
        """Stop timer and record elapsed time."""
        if timer_id not in self.timers:
            logger.warning(f"Timer {timer_id} not found")
            return 0.0
        
        elapsed = time.time() - self.timers[timer_id]
        del self.timers[timer_id]
        
        name = timer_id.split(':')[0]
        metric = Metric(
            name=name,
            value=elapsed,
            metric_type=MetricType.TIMER,
            tags=tags or {}
        )
        self.metrics.append(metric)
        
        return elapsed
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record histogram value."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def get_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get summary of metrics from last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]
        
        # Group by metric name and type
        summary: Dict[str, Any] = defaultdict(dict)
        
        for metric in recent_metrics:
            key = metric.name
            
            if key not in summary:
                summary[key] = {
                    "count": 0,
                    "total": 0.0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "values": []
                }
            
            summary[key]["count"] += 1
            summary[key]["total"] += metric.value
            summary[key]["min"] = min(summary[key]["min"], metric.value)
            summary[key]["max"] = max(summary[key]["max"], metric.value)
            summary[key]["values"].append(metric.value)
        
        # Calculate statistics
        for key, stats in summary.items():
            if stats["count"] > 0:
                values = stats["values"]
                values.sort()
                stats["average"] = stats["total"] / stats["count"]
                stats["median"] = values[len(values) // 2]
                stats["p95"] = values[int(len(values) * 0.95)] if len(values) > 1 else values[0]
                # Remove raw values
                del stats["values"]
        
        return dict(summary)
    
    def get_tool_metrics(self) -> Dict[str, Any]:
        """Get metrics for all tools."""
        summary = self.get_summary()
        tool_metrics = {}
        
        for key, stats in summary.items():
            if "tool_" in key:
                tool_metrics[key] = stats
        
        return tool_metrics
    
    def clear_old_metrics(self, hours: int = 24) -> int:
        """Remove metrics older than N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        old_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff]
        removed = old_count - len(self.metrics)
        return removed


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""
    task_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    duration: float = 0.0
    input_size: int = 0
    output_size: int = 0
    
    def complete(self, success: bool = True, error: Optional[str] = None) -> None:
        """Mark task as complete."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_name": self.task_name,
            "duration_ms": self.duration * 1000,
            "success": self.success,
            "error": self.error,
            "input_size": self.input_size,
            "output_size": self.output_size,
        }


class PerformanceMonitor:
    """Monitor performance of tasks and operations."""
    
    def __init__(self):
        self.tasks: List[TaskMetrics] = []
    
    def start_task(self, task_name: str, input_size: int = 0) -> TaskMetrics:
        """Start monitoring a task."""
        task = TaskMetrics(task_name=task_name, input_size=input_size)
        self.tasks.append(task)
        return task
    
    def get_task_stats(self, task_name: Optional[str] = None, minutes: int = 60) -> Dict[str, Any]:
        """Get statistics for tasks."""
        cutoff = time.time() - (minutes * 60)
        
        if task_name:
            tasks = [
                t for t in self.tasks
                if t.task_name == task_name and t.start_time > cutoff
            ]
        else:
            tasks = [t for t in self.tasks if t.start_time > cutoff]
        
        if not tasks:
            return {}
        
        successful = [t for t in tasks if t.success]
        failed = [t for t in tasks if not t.success]
        
        durations = [t.duration for t in successful]
        durations.sort()
        
        return {
            "total": len(tasks),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": f"{len(successful)/len(tasks)*100:.1f}%" if tasks else "0%",
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "errors": list(set([t.error for t in failed if t.error])),
        }


class HealthCheck:
    """System health monitoring."""
    
    def __init__(self):
        self.last_check = datetime.now()
        self.status = "healthy"
        self.warnings: List[str] = []
    
    def check_health(self, metrics: MetricsCollector) -> Dict[str, Any]:
        """Perform health check."""
        self.warnings.clear()
        
        # Check error rates
        summary = metrics.get_summary(minutes=60)
        
        total_errors = 0
        total_operations = 0
        
        for metric_name, stats in summary.items():
            if "error" in metric_name:
                total_errors += stats.get("total", 0)
            if "operation" in metric_name:
                total_operations += stats.get("total", 0)
        
        error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0
        
        if error_rate > 10:
            self.warnings.append(f"High error rate: {error_rate:.1f}%")
            self.status = "degraded"
        elif error_rate > 5:
            self.warnings.append(f"Elevated error rate: {error_rate:.1f}%")
        else:
            self.status = "healthy"
        
        return {
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "error_rate": f"{error_rate:.1f}%",
            "warnings": self.warnings,
            "total_metrics": len(metrics.metrics),
        }


# Global instances
_collector = MetricsCollector()
_monitor = PerformanceMonitor()
_health = HealthCheck()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _collector


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor."""
    return _monitor


def get_health_check() -> HealthCheck:
    """Get global health check."""
    return _health
