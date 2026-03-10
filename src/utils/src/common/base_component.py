"""Common Base Classes for Phase Modules.

Extracts duplicate __init__ patterns into reusable base classes.
Consolidates shared initialization logic across:
  - phase6_ecosystem
  - phase12_enterprise_platform
  - phase14_streaming_analytics
  - phase16_quantum_mesh
  - phase18_ai_developer_autonomy
  - phase24_autonomous_refactoring
  - phase26_enterprise_platform

Pattern Groups Addressed:
  1. BaseComponent         - Core init shared by ALL 10+ classes
  2. BaseServiceManager    - Enterprise/platform service managers
  3. BaseStreamProcessor   - Analytics & streaming processors
  4. BaseAutonomyEngine    - AI autonomy & refactoring engines
  5. BaseEcosystemPlugin   - Ecosystem plugin components
"""
import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio


class BaseComponent(ABC):
    """Universal base class extracting the 5 common __init__ lines
    duplicated across all phase modules.

    Consolidates:
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        self.metrics = {}
        self._lock = threading.Lock()
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        component_name: Optional[str] = None,
    ) -> None:
        self.config = config or {}
        self.logger = logger or logging.getLogger(
            component_name or self.__class__.__qualname__
        )
        self.is_initialized = False
        self.metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._created_at = time.monotonic()

        # Hook for subclasses to add init logic without overriding __init__
        self._post_init()

    def _post_init(self) -> None:
        """Override in subclasses for additional initialization."""
        pass

    def initialize(self) -> None:
        """Thread-safe lazy initialization."""
        with self._lock:
            if not self.is_initialized:
                self._do_initialize()
                self.is_initialized = True
                self.logger.info("%s initialized", self.__class__.__name__)

    def _do_initialize(self) -> None:
        """Override to provide custom initialization logic."""
        pass

    def record_metric(self, key: str, value: Any) -> None:
        """Thread-safe metric recording."""
        with self._lock:
            self.metrics[key] = value

    def get_metrics(self) -> Dict[str, Any]:
        """Return a snapshot of current metrics."""
        with self._lock:
            return dict(self.metrics)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"initialized={self.is_initialized} "
            f"metrics_count={len(self.metrics)}>"
        )


# ---------------------------------------------------------------------------
# Pattern 1 & 2: Enterprise / Platform Service Managers
# Covers: phase12_enterprise_platform (5 classes)
#         phase26_enterprise_platform (5 classes)
# ---------------------------------------------------------------------------
class BaseServiceManager(BaseComponent):
    """Base for service-manager classes in enterprise platform phases.

    Adds shared:
        self.services: Dict[str, Any]
        self.health_checks: Dict[str, bool]
        self._shutdown_hooks: List[callable]
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        component_name: Optional[str] = None,
    ) -> None:
        self.services: Dict[str, Any] = {}
        self.health_checks: Dict[str, bool] = {}
        self._shutdown_hooks: List[Any] = []
        super().__init__(config=config, logger=logger, component_name=component_name)

    def register_service(self, name: str, service: Any) -> None:
        with self._lock:
            self.services[name] = service
            self.health_checks[name] = True
            self.logger.debug("Registered service: %s", name)

    def add_shutdown_hook(self, hook: Any) -> None:
        self._shutdown_hooks.append(hook)

    async def shutdown(self) -> None:
        for hook in reversed(self._shutdown_hooks):
            try:
                await hook() if callable(hook) else None
            except Exception as exc:
                self.logger.error("Shutdown hook failed: %s", exc)


# ---------------------------------------------------------------------------
# Pattern 3: Streaming / Analytics Processors
# Covers: phase14_streaming_analytics (7 classes)
#         phase16_quantum_mesh         (8 classes)
# ---------------------------------------------------------------------------
class BaseStreamProcessor(BaseComponent):
    """Base for streaming and analytics processor classes.

    Adds shared:
        self.buffer: List[Any]
        self.batch_size: int
        self.processed_count: int
    """

    DEFAULT_BATCH_SIZE = 100

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        component_name: Optional[str] = None,
    ) -> None:
        self.buffer: List[Any] = []
        self.processed_count: int = 0
        super().__init__(config=config, logger=logger, component_name=component_name)
        self.batch_size: int = self.config.get(
            "batch_size", self.DEFAULT_BATCH_SIZE
        )

    def enqueue(self, item: Any) -> Optional[List[Any]]:
        """Add item to buffer; returns batch when full."""
        with self._lock:
            self.buffer.append(item)
            if len(self.buffer) >= self.batch_size:
                batch = list(self.buffer)
                self.buffer.clear()
                self.processed_count += len(batch)
                return batch
        return None

    def flush(self) -> List[Any]:
        """Flush remaining buffer."""
        with self._lock:
            batch = list(self.buffer)
            self.buffer.clear()
            self.processed_count += len(batch)
            return batch


# ---------------------------------------------------------------------------
# Pattern 4: AI Autonomy / Refactoring Engines
# Covers: phase18_ai_developer_autonomy  (5 classes)
#         phase24_autonomous_refactoring (5 classes)
# ---------------------------------------------------------------------------
class BaseAutonomyEngine(BaseComponent):
    """Base for AI autonomy and refactoring engine classes.

    Adds shared:
        self.agents: List[Any]
        self.task_queue: List[Any]
        self.completed_tasks: List[Any]
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        component_name: Optional[str] = None,
    ) -> None:
        self.agents: List[Any] = []
        self.task_queue: List[Any] = []
        self.completed_tasks: List[Any] = []
        super().__init__(config=config, logger=logger, component_name=component_name)

    def submit_task(self, task: Any) -> None:
        with self._lock:
            self.task_queue.append(task)
            self.logger.debug("Task queued (queue_size=%d)", len(self.task_queue))

    def register_agent(self, agent: Any) -> None:
        with self._lock:
            self.agents.append(agent)

    def next_task(self) -> Optional[Any]:
        with self._lock:
            return self.task_queue.pop(0) if self.task_queue else None


# ---------------------------------------------------------------------------
# Pattern 5: Ecosystem Plugin Components
# Covers: phase6_ecosystem (5 classes)
# ---------------------------------------------------------------------------
class BaseEcosystemPlugin(BaseComponent):
    """Base for ecosystem plugin / extension classes.

    Adds shared:
        self.plugins: Dict[str, Any]
        self.hooks: Dict[str, List[callable]]
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        component_name: Optional[str] = None,
    ) -> None:
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Any]] = {}
        super().__init__(config=config, logger=logger, component_name=component_name)

    def register_plugin(self, name: str, plugin: Any) -> None:
        with self._lock:
            self.plugins[name] = plugin
            self.logger.debug("Plugin registered: %s", name)

    def add_hook(self, event: str, callback: Any) -> None:
        with self._lock:
            self.hooks.setdefault(event, []).append(callback)

    def trigger_hook(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        results = []
        for cb in self.hooks.get(event, []):
            try:
                results.append(cb(*args, **kwargs))
            except Exception as exc:
                self.logger.error("Hook %s failed: %s", event, exc)
        return results
