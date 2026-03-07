"""Migration Guide: Refactoring Duplicate __init__ Patterns.

This file shows BEFORE/AFTER examples for each of the 10 duplicate
__init__ pattern groups being consolidated.

=== HOW TO MIGRATE ===
1. Import the appropriate base class from src.common.base_component
2. Replace duplicate __init__ body with super().__init__(...)
3. Move custom init logic to _post_init() or after super().__init__()
4. Run tests to verify behavior is preserved
"""

# ============================================================================
# EXAMPLE 1: phase12_enterprise_platform / phase26_enterprise_platform
# ============================================================================

# --- BEFORE (duplicated in 10 classes across phase12 & phase26) ---
"""
class TenantManager:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.services = {}                                  # DUPLICATE
        self.health_checks = {}                             # DUPLICATE
        self._shutdown_hooks = []                           # DUPLICATE
        # Custom logic
        self.tenants = {}
        self.max_tenants = self.config.get('max_tenants', 100)

class DeploymentOrchestrator:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.services = {}                                  # DUPLICATE
        self.health_checks = {}                             # DUPLICATE
        self._shutdown_hooks = []                           # DUPLICATE
        # Custom logic
        self.deployments = []
        self.rollback_stack = []
"""

# --- AFTER (consolidated via BaseServiceManager) ---
"""
from src.common.base_component import BaseServiceManager

class TenantManager(BaseServiceManager):
    def _post_init(self) -> None:
        self.tenants = {}
        self.max_tenants = self.config.get('max_tenants', 100)

class DeploymentOrchestrator(BaseServiceManager):
    def _post_init(self) -> None:
        self.deployments = []
        self.rollback_stack = []
"""

# ============================================================================
# EXAMPLE 2: phase14_streaming_analytics / phase16_quantum_mesh
# ============================================================================

# --- BEFORE (duplicated in 15 classes across phase14 & phase16) ---
"""
class StreamAggregator:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.buffer = []                                    # DUPLICATE
        self.batch_size = config.get('batch_size', 100) if config else 100  # DUPLICATE
        self.processed_count = 0                            # DUPLICATE
        # Custom logic
        self.aggregation_window = self.config.get('window_sec', 60)
        self.aggregation_fn = None

class QuantumMeshRouter:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.buffer = []                                    # DUPLICATE
        self.batch_size = config.get('batch_size', 100) if config else 100  # DUPLICATE
        self.processed_count = 0                            # DUPLICATE
        # Custom logic
        self.mesh_topology = {}
        self.routing_table = {}
"""

# --- AFTER (consolidated via BaseStreamProcessor) ---
"""
from src.common.base_component import BaseStreamProcessor

class StreamAggregator(BaseStreamProcessor):
    def _post_init(self) -> None:
        self.aggregation_window = self.config.get('window_sec', 60)
        self.aggregation_fn = None

class QuantumMeshRouter(BaseStreamProcessor):
    def _post_init(self) -> None:
        self.mesh_topology = {}
        self.routing_table = {}
"""

# ============================================================================
# EXAMPLE 3: phase18_ai_developer_autonomy / phase24_autonomous_refactoring
# ============================================================================

# --- BEFORE (duplicated in 10 classes across phase18 & phase24) ---
"""
class CodeAnalysisAgent:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.agents = []                                    # DUPLICATE
        self.task_queue = []                                # DUPLICATE
        self.completed_tasks = []                           # DUPLICATE
        # Custom logic
        self.analysis_results = {}
        self.confidence_threshold = self.config.get('confidence', 0.8)
"""

# --- AFTER (consolidated via BaseAutonomyEngine) ---
"""
from src.common.base_component import BaseAutonomyEngine

class CodeAnalysisAgent(BaseAutonomyEngine):
    def _post_init(self) -> None:
        self.analysis_results = {}
        self.confidence_threshold = self.config.get('confidence', 0.8)
"""

# ============================================================================
# EXAMPLE 4: phase6_ecosystem
# ============================================================================

# --- BEFORE (duplicated in 5 classes in phase6) ---
"""
class PluginRegistry:
    def __init__(self, config=None, logger=None):
        self.config = config or {}                          # DUPLICATE
        self.logger = logger or logging.getLogger(__name__) # DUPLICATE
        self.is_initialized = False                         # DUPLICATE
        self.metrics = {}                                   # DUPLICATE
        self._lock = threading.Lock()                       # DUPLICATE
        self.plugins = {}                                   # DUPLICATE
        self.hooks = {}                                     # DUPLICATE
        # Custom logic
        self.plugin_versions = {}
"""

# --- AFTER (consolidated via BaseEcosystemPlugin) ---
"""
from src.common.base_component import BaseEcosystemPlugin

class PluginRegistry(BaseEcosystemPlugin):
    def _post_init(self) -> None:
        self.plugin_versions = {}
"""
