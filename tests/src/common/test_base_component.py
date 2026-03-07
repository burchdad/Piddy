"""Tests for common base classes.

Verifies that the extracted base classes correctly consolidate
the duplicate __init__ patterns from phase modules.
"""
import logging
import threading
import pytest
from unittest.mock import MagicMock

from src.common.base_component import (
    BaseComponent,
    BaseServiceManager,
    BaseStreamProcessor,
    BaseAutonomyEngine,
    BaseEcosystemPlugin,
)


# ---------------------------------------------------------------------------
# Concrete test subclasses (since BaseComponent is ABC)
# ---------------------------------------------------------------------------
class ConcreteComponent(BaseComponent):
    """Minimal concrete subclass for testing."""
    pass


class ComponentWithPostInit(BaseComponent):
    """Subclass that uses _post_init hook."""
    def _post_init(self):
        self.custom_attr = "initialized"
        self.counter = 0


class ComponentWithDoInit(BaseComponent):
    """Subclass that uses _do_initialize."""
    def _do_initialize(self):
        self.setup_complete = True


# ===========================================================================
# BaseComponent Tests
# ===========================================================================
class TestBaseComponent:
    """Tests for the universal BaseComponent base class."""

    def test_default_init(self):
        """All 5 common attributes are initialized with defaults."""
        comp = ConcreteComponent()
        assert comp.config == {}
        assert isinstance(comp.logger, logging.Logger)
        assert comp.is_initialized is False
        assert comp.metrics == {}
        assert isinstance(comp._lock, type(threading.Lock()))

    def test_custom_config(self):
        cfg = {"batch_size": 50, "timeout": 30}
        comp = ConcreteComponent(config=cfg)
        assert comp.config == cfg
        assert comp.config["batch_size"] == 50

    def test_custom_logger(self):
        custom_logger = logging.getLogger("test.custom")
        comp = ConcreteComponent(logger=custom_logger)
        assert comp.logger is custom_logger

    def test_component_name_in_logger(self):
        comp = ConcreteComponent(component_name="my.component")
        assert comp.logger.name == "my.component"

    def test_default_logger_uses_class_name(self):
        comp = ConcreteComponent()
        assert "ConcreteComponent" in comp.logger.name

    def test_post_init_hook(self):
        comp = ComponentWithPostInit()
        assert comp.custom_attr == "initialized"
        assert comp.counter == 0

    def test_initialize_thread_safe(self):
        comp = ComponentWithDoInit()
        assert comp.is_initialized is False
        comp.initialize()
        assert comp.is_initialized is True
        assert comp.setup_complete is True

    def test_initialize_idempotent(self):
        """Calling initialize() twice should not re-run _do_initialize."""
        call_count = 0
        class CountingComponent(BaseComponent):
            def _do_initialize(self_inner):
                nonlocal call_count
                call_count += 1
        comp = CountingComponent()
        comp.initialize()
        comp.initialize()
        assert call_count == 1

    def test_record_metric(self):
        comp = ConcreteComponent()
        comp.record_metric("latency_ms", 42)
        comp.record_metric("throughput", 1000)
        assert comp.get_metrics() == {"latency_ms": 42, "throughput": 1000}

    def test_get_metrics_returns_copy(self):
        comp = ConcreteComponent()
        comp.record_metric("key", "value")
        snapshot = comp.get_metrics()
        snapshot["key"] = "modified"
        assert comp.get_metrics()["key"] == "value"

    def test_repr(self):
        comp = ConcreteComponent()
        r = repr(comp)
        assert "ConcreteComponent" in r
        assert "initialized=False" in r
        assert "metrics_count=0" in r

    def test_created_at_timestamp(self):
        comp = ConcreteComponent()
        assert comp._created_at > 0


# ===========================================================================
# BaseServiceManager Tests
# ===========================================================================
class TestBaseServiceManager:
    """Tests for enterprise platform service manager base."""

    def test_inherits_base_component(self):
        mgr = BaseServiceManager()
        assert isinstance(mgr, BaseComponent)
        assert mgr.config == {}
        assert mgr.is_initialized is False

    def test_service_attributes(self):
        mgr = BaseServiceManager()
        assert mgr.services == {}
        assert mgr.health_checks == {}
        assert mgr._shutdown_hooks == []

    def test_register_service(self):
        mgr = BaseServiceManager()
        mock_svc = MagicMock()
        mgr.register_service("auth", mock_svc)
        assert mgr.services["auth"] is mock_svc
        assert mgr.health_checks["auth"] is True

    def test_add_shutdown_hook(self):
        mgr = BaseServiceManager()
        hook = MagicMock()
        mgr.add_shutdown_hook(hook)
        assert hook in mgr._shutdown_hooks

    def test_config_passthrough(self):
        cfg = {"region": "us-east-1"}
        mgr = BaseServiceManager(config=cfg)
        assert mgr.config["region"] == "us-east-1"


# ===========================================================================
# BaseStreamProcessor Tests
# ===========================================================================
class TestBaseStreamProcessor:
    """Tests for streaming/analytics processor base."""

    def test_inherits_base_component(self):
        proc = BaseStreamProcessor()
        assert isinstance(proc, BaseComponent)

    def test_default_batch_size(self):
        proc = BaseStreamProcessor()
        assert proc.batch_size == 100
        assert proc.buffer == []
        assert proc.processed_count == 0

    def test_custom_batch_size(self):
        proc = BaseStreamProcessor(config={"batch_size": 25})
        assert proc.batch_size == 25

    def test_enqueue_below_batch(self):
        proc = BaseStreamProcessor(config={"batch_size": 3})
        result = proc.enqueue("item1")
        assert result is None
        result = proc.enqueue("item2")
        assert result is None

    def test_enqueue_triggers_batch(self):
        proc = BaseStreamProcessor(config={"batch_size": 3})
        proc.enqueue("a")
        proc.enqueue("b")
        batch = proc.enqueue("c")
        assert batch == ["a", "b", "c"]
        assert proc.buffer == []
        assert proc.processed_count == 3

    def test_flush(self):
        proc = BaseStreamProcessor(config={"batch_size": 100})
        proc.enqueue("x")
        proc.enqueue("y")
        batch = proc.flush()
        assert batch == ["x", "y"]
        assert proc.buffer == []
        assert proc.processed_count == 2

    def test_flush_empty(self):
        proc = BaseStreamProcessor()
        assert proc.flush() == []


# ===========================================================================
# BaseAutonomyEngine Tests
# ===========================================================================
class TestBaseAutonomyEngine:
    """Tests for AI autonomy engine base."""

    def test_inherits_base_component(self):
        engine = BaseAutonomyEngine()
        assert isinstance(engine, BaseComponent)

    def test_default_attributes(self):
        engine = BaseAutonomyEngine()
        assert engine.agents == []
        assert engine.task_queue == []
        assert engine.completed_tasks == []

    def test_submit_task(self):
        engine = BaseAutonomyEngine()
        engine.submit_task({"type": "analyze", "target": "module.py"})
        assert len(engine.task_queue) == 1

    def test_register_agent(self):
        engine = BaseAutonomyEngine()
        agent = MagicMock()
        engine.register_agent(agent)
        assert agent in engine.agents

    def test_next_task_fifo(self):
        engine = BaseAutonomyEngine()
        engine.submit_task("task1")
        engine.submit_task("task2")
        assert engine.next_task() == "task1"
        assert engine.next_task() == "task2"
        assert engine.next_task() is None

    def test_config_passthrough(self):
        engine = BaseAutonomyEngine(config={"confidence": 0.9})
        assert engine.config["confidence"] == 0.9


# ===========================================================================
# BaseEcosystemPlugin Tests
# ===========================================================================
class TestBaseEcosystemPlugin:
    """Tests for ecosystem plugin base."""

    def test_inherits_base_component(self):
        plugin = BaseEcosystemPlugin()
        assert isinstance(plugin, BaseComponent)

    def test_default_attributes(self):
        plugin = BaseEcosystemPlugin()
        assert plugin.plugins == {}
        assert plugin.hooks == {}

    def test_register_plugin(self):
        eco = BaseEcosystemPlugin()
        mock_plugin = MagicMock()
        eco.register_plugin("formatter", mock_plugin)
        assert eco.plugins["formatter"] is mock_plugin

    def test_add_and_trigger_hook(self):
        eco = BaseEcosystemPlugin()
        callback = MagicMock(return_value="result")
        eco.add_hook("on_load", callback)
        results = eco.trigger_hook("on_load", "arg1", key="val")
        callback.assert_called_once_with("arg1", key="val")
        assert results == ["result"]

    def test_trigger_hook_no_handlers(self):
        eco = BaseEcosystemPlugin()
        assert eco.trigger_hook("nonexistent") == []

    def test_trigger_hook_error_handling(self):
        eco = BaseEcosystemPlugin()
        bad_cb = MagicMock(side_effect=ValueError("boom"))
        good_cb = MagicMock(return_value="ok")
        eco.add_hook("evt", bad_cb)
        eco.add_hook("evt", good_cb)
        results = eco.trigger_hook("evt")
        # Bad callback error is caught, good callback still runs
        assert len(results) == 1
        assert results[0] == "ok"


# ===========================================================================
# Cross-cutting: Thread Safety
# ===========================================================================
class TestThreadSafety:
    """Verify thread-safe operations across base classes."""

    def test_concurrent_metric_recording(self):
        comp = ConcreteComponent()
        errors = []

        def record(n):
            try:
                for i in range(100):
                    comp.record_metric(f"thread_{n}_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record, args=(t,)) for t in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(comp.get_metrics()) == 1000

    def test_concurrent_enqueue(self):
        proc = BaseStreamProcessor(config={"batch_size": 1000})
        errors = []

        def enqueue_items(start):
            try:
                for i in range(100):
                    proc.enqueue(start + i)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=enqueue_items, args=(t * 100,))
            for t in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        remaining = proc.flush()
        assert proc.processed_count == 1000
