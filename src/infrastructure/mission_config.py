"""
logger = logging.getLogger(__name__)
Mission Configuration Framework
Standardizes mission definitions for Phases 40-42+

Supports:
- Phase 40: Simulation configuration
- Phase 42: Nightly missions
- Phase 50+: Agent pipelines
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from enum import Enum
import json
import yaml
from pathlib import Path
import logging


class MissionType(Enum):
    """Types of autonomous missions"""
    CLEANUP = "cleanup"              # Remove dead code
    REFACTOR = "refactor"            # Restructure code
    COVERAGE = "coverage_improvement"  # Add tests
    OPTIMIZATION = "optimization"    # Performance improvements
    TYPE_IMPROVEMENT = "type_improvement"  # Add type hints
    SECURITY = "security"            # Security improvements
    CUSTOM = "custom"                # Custom task


class RiskTolerance(Enum):
    """Risk tolerance levels for missions"""
    LOW = "low"                      # Conservative, small changes
    MEDIUM = "medium"                # Balanced approach
    HIGH = "high"                    # Aggressive, large changes


@dataclass
class MissionConfig:
    """Standardized mission configuration"""
    
    # Identity
    name: str                        # Unique mission name
    type: MissionType                # Mission type
    description: str                 # What it does
    
    # Execution settings
    priority: int                    # Execution priority (1-10)
    risk_tolerance: RiskTolerance   # Risk level
    approval_required: bool          # Needs human approval?
    auto_merge: bool = False         # Auto-merge PR?
    
    # Constraints
    max_changes: Optional[int] = None  # Max files to change
    max_time: int = 300              # Max execution time (seconds)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Other missions
    
    # Targeting
    target_modules: List[str] = field(default_factory=list)
    exclude_modules: List[str] = field(default_factory=list)
    
    # Safety
    min_confidence: float = 0.7      # Don't execute if below this
    retry_on_failure: bool = True    # Retry on failure?
    max_retries: int = 2             # Maximum retry attempts
    
    # Metrics
    target_metrics: Dict = field(default_factory=dict)  # Coverage, lines, etc.
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    owner: str = "system"
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'priority': self.priority,
            'risk_tolerance': self.risk_tolerance.value,
            'approval_required': self.approval_required,
            'auto_merge': self.auto_merge,
            'max_changes': self.max_changes,
            'max_time': self.max_time,
            'dependencies': self.dependencies,
            'target_modules': self.target_modules,
            'exclude_modules': self.exclude_modules,
            'min_confidence': self.min_confidence,
            'retry_on_failure': self.retry_on_failure,
            'max_retries': self.max_retries,
            'target_metrics': self.target_metrics,
            'tags': self.tags,
            'owner': self.owner,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MissionConfig':
        """Create from dictionary"""
        data = data.copy()
        data['type'] = MissionType(data['type']) if isinstance(data['type'], str) else data['type']
        data['risk_tolerance'] = RiskTolerance(data['risk_tolerance']) if isinstance(data['risk_tolerance'], str) else data['risk_tolerance']
        return cls(**data)


class MissionConfigManager:
    """Manages mission configurations"""
    
    def __init__(self, config_dir: str = "config/missions"):
        """Initialize config manager"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, MissionConfig] = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load configurations from YAML files"""
        if not self.config_dir.exists():
            return
        
        for config_file in self.config_dir.glob('*.yaml'):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)
                if data:
                    config = MissionConfig.from_dict(data)
                    self.configs[config.name] = config
            except Exception as e:
                logger.info(f"Error loading {config_file}: {e}")
    
    def get_config(self, mission_name: str) -> Optional[MissionConfig]:
        """Get configuration for mission"""
        return self.configs.get(mission_name)
    
    def get_configs_by_type(self, mission_type: MissionType) -> List[MissionConfig]:
        """Get all configs of a specific type"""
        return [c for c in self.configs.values() if c.type == mission_type]
    
    def get_configs_by_priority(self, min_priority: int = 1, max_priority: int = 10) -> List[MissionConfig]:
        """Get configs within priority range"""
        return [c for c in self.configs.values() 
                if min_priority <= c.priority <= max_priority]
    
    def save_config(self, config: MissionConfig) -> None:
        """Save configuration to file"""
        config_file = self.config_dir / f"{config.name}.yaml"
        
        with open(config_file, 'w') as f:
            yaml.safe_dump(config.to_dict(), f, default_flow_style=False)
        
        self.configs[config.name] = config
    
    def validate_config(self, config: MissionConfig) -> tuple[bool, List[str]]:
        """Validate mission configuration"""
        errors = []
        
        # Check name is not empty
        if not config.name or not config.name.strip():
            errors.append("Mission name cannot be empty")
        
        # Check priority range
        if not 1 <= config.priority <= 10:
            errors.append(f"Priority must be 1-10, got {config.priority}")
        
        # Check dependencies exist
        for dep in config.dependencies:
            if dep not in self.configs:
                errors.append(f"Dependency '{dep}' not found")
        
        # Check confidence range
        if not 0.0 <= config.min_confidence <= 1.0:
            errors.append(f"Confidence must be 0.0-1.0, got {config.min_confidence}")
        
        # Check max_retries is non-negative
        if config.max_retries < 0:
            errors.append(f"max_retries cannot be negative, got {config.max_retries}")
        
        # Check max_time is positive
        if config.max_time <= 0:
            errors.append(f"max_time must be positive, got {config.max_time}")
        
        return len(errors) == 0, errors
    
    def create_default_missions(self) -> None:
        """Create default mission configurations"""
        
        # Cleanup mission
        cleanup_config = MissionConfig(
            name="cleanup_dead_code",
            type=MissionType.CLEANUP,
            description="Remove unreachable and unused code",
            priority=3,
            risk_tolerance=RiskTolerance.LOW,
            approval_required=False,
            auto_merge=True,
            max_changes=50,
            max_time=600,
            min_confidence=0.8,
            target_metrics={'files_removed_min': 5, 'functions_removed_min': 10},
            tags=["code quality", "cleanup"],
            owner="system",
        )
        self.save_config(cleanup_config)
        
        # Coverage improvement mission
        coverage_config = MissionConfig(
            name="improve_coverage",
            type=MissionType.COVERAGE,
            description="Add tests for uncovered code",
            priority=4,
            risk_tolerance=RiskTolerance.LOW,
            approval_required=False,
            auto_merge=True,
            max_changes=20,
            max_time=900,
            min_confidence=0.7,
            target_modules=["src"],
            target_metrics={'coverage_increase_min': 1.0},
            tags=["testing", "coverage"],
            owner="system",
        )
        self.save_config(coverage_config)
        
        # Refactor complex functions
        refactor_config = MissionConfig(
            name="refactor_complex_functions",
            type=MissionType.REFACTOR,
            description="Simplify functions with high complexity",
            priority=5,
            risk_tolerance=RiskTolerance.MEDIUM,
            approval_required=True,  # Requires review
            auto_merge=False,
            max_changes=15,
            max_time=1200,
            min_confidence=0.8,
            target_modules=["src"],
            target_metrics={'complexity_reduction_min': 0.2},
            tags=["refactoring", "maintainability"],
            owner="system",
        )
        self.save_config(refactor_config)
        
        # Type improvements
        type_config = MissionConfig(
            name="improve_type_hints",
            type=MissionType.TYPE_IMPROVEMENT,
            description="Add type hints to untyped code",
            priority=2,
            risk_tolerance=RiskTolerance.LOW,
            approval_required=False,
            auto_merge=True,
            max_changes=30,
            max_time=800,
            min_confidence=0.7,
            target_modules=["src"],
            target_metrics={'typed_functions_min': 10},
            tags=["types", "type safety"],
            owner="system",
        )
        self.save_config(type_config)
        
        # Security improvements
        security_config = MissionConfig(
            name="security_hardening",
            type=MissionType.SECURITY,
            description="Fix security vulnerabilities and improve hardening",
            priority=9,  # High priority
            risk_tolerance=RiskTolerance.LOW,
            approval_required=True,  # Always requires review
            auto_merge=False,
            max_changes=25,
            max_time=600,
            min_confidence=0.95,  # Very high confidence required
            target_metrics={'vulnerabilities_fixed_min': 1},
            tags=["security", "hardening"],
            owner="system",
        )
        self.save_config(security_config)
        
        # Optimization mission
        optimization_config = MissionConfig(
            name="performance_optimization",
            type=MissionType.OPTIMIZATION,
            description="Optimize performance bottlenecks",
            priority=6,
            risk_tolerance=RiskTolerance.MEDIUM,
            approval_required=True,
            auto_merge=False,
            max_changes=20,
            max_time=1500,
            min_confidence=0.85,
            target_metrics={'performance_improvement_min': 0.1},
            tags=["performance", "optimization"],
            owner="system",
        )
        self.save_config(optimization_config)


# Default configurations to create
DEFAULT_MISSIONS = {
    "cleanup_dead_code": "Remove unreachable and unused code",
    "improve_coverage": "Add tests for uncovered code",
    "refactor_complex_functions": "Simplify functions with high complexity",
    "improve_type_hints": "Add type hints to untyped code",
    "security_hardening": "Fix security vulnerabilities",
    "performance_optimization": "Optimize performance bottlenecks",
}
