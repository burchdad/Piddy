"""
Distributed tracing and observability for Phase 5.
Provides request tracing, performance monitoring, and system observability across Piddy instances.
"""
import logging
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class SpanKind(str, Enum):
    """Type of span (trace segment)."""
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class SpanStatus(str, Enum):
    """Status of a span."""
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class SpanEvent:
    """Event that occurred during span execution."""
    name: str
    timestamp: float
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class Span:
    """Distributed trace span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    kind: SpanKind
    status: SpanStatus
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    attributes: Dict[str, Any] = None
    events: List[SpanEvent] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.events is None:
            self.events = []

        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time) * 1000  # ms


@dataclass
class Trace:
    """Complete distributed trace with multiple spans."""
    trace_id: str
    root_span_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    spans: Dict[str, Span] = None
    service_name: str = "piddy"
    status: str = "active"

    def __post_init__(self):
        if self.spans is None:
            self.spans = {}

        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time) * 1000  # ms


class DistributedTracer:
    """
    Distributed tracing system for observability across Piddy instances.
    Tracks requests through multiple services and generates insights.
    """

    def __init__(self, service_name: str = "piddy", max_traces: int = 10000):
        """Initialize distributed tracer."""
        self.service_name = service_name
        self.max_traces = max_traces
        self.traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, Span] = {}
        self.span_stack: Dict[str, List[str]] = {}  # trace_id -> [span_ids]
        logger.info("✅ Distributed Tracer initialized")

    def start_trace(
        self,
        trace_name: str,
        trace_id: Optional[str] = None,
        attributes: Optional[Dict] = None,
    ) -> Trace:
        """
        Start a new distributed trace.

        Args:
            trace_name: Name of the trace
            trace_id: Optional trace ID (auto-generates if not provided)
            attributes: Trace-level attributes

        Returns:
            Started Trace object
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        root_span_id = str(uuid.uuid4())
        now = time.time()

        trace = Trace(
            trace_id=trace_id,
            root_span_id=root_span_id,
            start_time=now,
            service_name=self.service_name,
        )

        # Create root span
        root_span = Span(
            trace_id=trace_id,
            span_id=root_span_id,
            parent_span_id=None,
            name=trace_name,
            kind=SpanKind.INTERNAL,
            status=SpanStatus.UNSET,
            start_time=now,
            attributes=attributes or {},
        )

        self.traces[trace_id] = trace
        self.active_spans[root_span_id] = root_span
        self.span_stack[trace_id] = [root_span_id]

        trace.spans[root_span_id] = root_span

        # Cleanup old traces if exceeding max
        if len(self.traces) > self.max_traces:
            oldest_id = min(self.traces.keys(), key=lambda k: self.traces[k].start_time)
            del self.traces[oldest_id]

        logger.debug(f"Trace started: {trace_id} - {trace_name}")
        return trace

    def start_span(
        self,
        trace_id: str,
        span_name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict] = None,
    ) -> Span:
        """
        Start a new span within a trace.

        Args:
            trace_id: Trace ID this span belongs to
            span_name: Name of the span
            kind: Type of span
            attributes: Span attributes

        Returns:
            Started Span object
        """
        if trace_id not in self.traces:
            logger.warning(f"Trace not found: {trace_id}")
            return None

        span_id = str(uuid.uuid4())
        now = time.time()

        # Get parent span (current active span in this trace)
        parent_span_id = None
        if trace_id in self.span_stack and self.span_stack[trace_id]:
            parent_span_id = self.span_stack[trace_id][-1]

        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=span_name,
            kind=kind,
            status=SpanStatus.UNSET,
            start_time=now,
            attributes=attributes or {},
        )

        self.active_spans[span_id] = span
        self.traces[trace_id].spans[span_id] = span

        if trace_id not in self.span_stack:
            self.span_stack[trace_id] = []
        self.span_stack[trace_id].append(span_id)

        logger.debug(f"Span started: {span_id} in trace {trace_id}")
        return span

    def end_span(
        self,
        span_id: str,
        status: SpanStatus = SpanStatus.OK,
        error: Optional[str] = None,
    ) -> bool:
        """
        End a span and mark its status.

        Args:
            span_id: Span ID to end
            status: Final span status
            error: Error message if failed

        Returns:
            True if successful
        """
        if span_id not in self.active_spans:
            logger.warning(f"Span not found: {span_id}")
            return False

        span = self.active_spans[span_id]
        span.end_time = time.time()
        span.status = status
        span.error = error

        # Pop from span stack
        if span.trace_id in self.span_stack:
            if self.span_stack[span.trace_id] and self.span_stack[span.trace_id][-1] == span_id:
                self.span_stack[span.trace_id].pop()

        del self.active_spans[span_id]

        logger.debug(f"Span ended: {span_id} - Status: {status.value}")
        return True

    def end_trace(self, trace_id: str) -> bool:
        """End a trace."""
        if trace_id not in self.traces:
            logger.warning(f"Trace not found: {trace_id}")
            return False

        trace = self.traces[trace_id]
        trace.end_time = time.time()
        trace.status = "completed"

        logger.debug(f"Trace ended: {trace_id}")
        return True

    def add_span_event(self, span_id: str, event_name: str, attributes: Optional[Dict] = None) -> bool:
        """Add an event to a span."""
        if span_id not in self.active_spans:
            logger.warning(f"Span not found: {span_id}")
            return False

        span = self.active_spans[span_id]
        event = SpanEvent(
            name=event_name,
            timestamp=time.time(),
            attributes=attributes or {},
        )

        span.events.append(event)
        return True

    def set_span_attribute(self, span_id: str, key: str, value: Any) -> bool:
        """Set attribute on a span."""
        if span_id not in self.active_spans:
            logger.warning(f"Span not found: {span_id}")
            return False

        self.active_spans[span_id].attributes[key] = value
        return True

    def get_trace(self, trace_id: str) -> Optional[Dict]:
        """Get trace details."""
        if trace_id not in self.traces:
            return None

        trace = self.traces[trace_id]
        return {
            "trace_id": trace.trace_id,
            "duration_ms": trace.duration,
            "status": trace.status,
            "spans": [asdict(span) for span in trace.spans.values()],
            "span_count": len(trace.spans),
            "service": trace.service_name,
        }

    def get_trace_metrics(self, trace_id: str) -> Optional[Dict]:
        """Get metrics for a trace."""
        if trace_id not in self.traces:
            return None

        trace = self.traces[trace_id]
        spans = trace.spans.values()

        if not spans:
            return None

        durations = [s.duration for s in spans if s.duration]
        error_count = len([s for s in spans if s.status == SpanStatus.ERROR])

        return {
            "trace_id": trace_id,
            "total_duration_ms": trace.duration or 0,
            "span_count": len(spans),
            "average_span_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_span_ms": min(durations) if durations else 0,
            "max_span_ms": max(durations) if durations else 0,
            "error_count": error_count,
            "success_rate": ((len(spans) - error_count) / len(spans) * 100) if spans else 0,
        }

    def get_service_metrics(self) -> Dict[str, Any]:
        """Get metrics across all traces."""
        if not self.traces:
            return {
                "total_traces": 0,
                "active_traces": 0,
                "average_trace_duration_ms": 0,
                "total_spans": 0,
                "error_rate": 0,
            }

        all_spans = []
        for trace in self.traces.values():
            all_spans.extend(trace.spans.values())

        completed_traces = [t for t in self.traces.values() if t.status == "completed"]
        durations = [t.duration for t in completed_traces if t.duration]

        error_count = len([s for s in all_spans if s.status == SpanStatus.ERROR])

        return {
            "total_traces": len(self.traces),
            "active_traces": len(self.span_stack),
            "completed_traces": len(completed_traces),
            "average_trace_duration_ms": sum(durations) / len(durations) if durations else 0,
            "total_spans": len(all_spans),
            "error_count": error_count,
            "error_rate": (error_count / len(all_spans) * 100) if all_spans else 0,
            "service": self.service_name,
        }

    def export_traces(self, limit: int = 100) -> List[Dict]:
        """Export traces for analysis/visualization."""
        traces = list(self.traces.values())[-limit:]
        return [asdict(t) for t in traces]

    def get_slow_traces(self, threshold_ms: int = 1000, limit: int = 10) -> List[Dict]:
        """Get slowest traces (useful for performance investigation)."""
        slow_traces = [
            t for t in self.traces.values()
            if t.duration and t.duration > threshold_ms
        ]
        slow_traces.sort(key=lambda t: t.duration or 0, reverse=True)
        return [
            {
                "trace_id": t.trace_id,
                "duration_ms": t.duration,
                "service": t.service_name,
                "status": t.status,
            }
            for t in slow_traces[:limit]
        ]

    def get_error_traces(self, limit: int = 10) -> List[Dict]:
        """Get traces with errors."""
        error_traces = []
        for trace in self.traces.values():
            error_spans = [s for s in trace.spans.values() if s.status == SpanStatus.ERROR]
            if error_spans:
                error_traces.append({
                    "trace_id": trace.trace_id,
                    "error_count": len(error_spans),
                    "errors": [s.error for s in error_spans if s.error],
                    "duration_ms": trace.duration,
                })

        return error_traces[:limit]


# Global tracer instance
_tracer_instance: Optional[DistributedTracer] = None


def get_tracer() -> DistributedTracer:
    """Get or create global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = DistributedTracer()
    return _tracer_instance
