"""
Execution Modes - User-configurable safety levels for mission execution

Four modes provide different levels of autonomy and safety:
- SAFE: Default, requires approval for risky operations
- AUTO: Auto-approves low-risk, blocks high-risk
- PR_ONLY: Creates PRs instead of direct commits
- DRY_RUN: Shows consequences without executing
"""

from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for Nova"""
    
    SAFE = "safe"          # Default - high oversight, blocks risky operations
    AUTO = "auto"          # Developer mode - auto-approves low-risk
    PR_ONLY = "pr_only"    # Safe push - creates PR instead of direct commit
    DRY_RUN = "dry_run"    # Simulation - shows consequences, no execution


# Default configuration per mode
EXECUTION_MODE_CONFIG = {
    ExecutionMode.SAFE: {
        "description": "Default - High oversight, blocks risky operations",
        "auto_approve_low_risk": False,  # Require approval for all
        "require_approval_medium_risk": True,
        "require_approval_high_risk": True,
        "allow_direct_commit": False,  # Create PR instead
        "allow_network_access": False,
        "allow_internet_access": False,
        "timeout_seconds": 600,
        "max_files_changed": 50,
        "max_lines_changed": 5000,
        "max_execution_time_sec": 600,
    },
    ExecutionMode.AUTO: {
        "description": "Developer mode - Auto-approves low-risk operations",
        "auto_approve_low_risk": True,  # Auto-approve LOW risk
        "require_approval_medium_risk": True,
        "require_approval_high_risk": True,
        "allow_direct_commit": True,  # Direct commit for approved tasks
        "allow_network_access": True,
        "allow_internet_access": True,  # Needed for package downloads
        "timeout_seconds": 1200,
        "max_files_changed": 100,
        "max_lines_changed": 10000,
        "max_execution_time_sec": 1200,
    },
    ExecutionMode.PR_ONLY: {
        "description": "Safe push - Creates PR instead of direct commit",
        "auto_approve_low_risk": False,
        "require_approval_medium_risk": False,
        "require_approval_high_risk": False,  # PR is the "approval"
        "allow_direct_commit": False,  # Always create PR
        "allow_network_access": True,
        "allow_internet_access": False,
        "timeout_seconds": 600,
        "max_files_changed": 100,
        "max_lines_changed": 10000,
        "max_execution_time_sec": 600,
    },
    ExecutionMode.DRY_RUN: {
        "description": "Simulation - Shows consequences, no execution",
        "auto_approve_low_risk": True,  # Dry runs are always allowed
        "require_approval_medium_risk": False,
        "require_approval_high_risk": False,
        "allow_direct_commit": False,  # Never commits in dry-run
        "allow_network_access": False,
        "allow_internet_access": False,
        "timeout_seconds": 300,
        "max_files_changed": 500,  # No limit - won't execute anyway
        "max_lines_changed": 50000,
        "max_execution_time_sec": 300,
    },
}


def get_mode_config(mode: ExecutionMode) -> dict:
    """Get configuration for an execution mode"""
    return EXECUTION_MODE_CONFIG.get(mode, EXECUTION_MODE_CONFIG[ExecutionMode.SAFE])


def describe_mode(mode: ExecutionMode) -> str:
    """Get human-readable description of a mode"""
    config = get_mode_config(mode)
    return config["description"]


def validate_execution_mode(mode_str: str) -> ExecutionMode:
    """
    Parse and validate execution mode string
    
    Args:
        mode_str: Mode string (safe, auto, pr_only, dry_run)
    
    Returns:
        ExecutionMode enum value
    
    Raises:
        ValueError: If mode is not valid
    """
    try:
        return ExecutionMode(mode_str.lower())
    except ValueError:
        valid_modes = ", ".join([m.value for m in ExecutionMode])
        raise ValueError(f"Invalid execution mode: {mode_str}. Valid modes: {valid_modes}")


class ExecutionModeContext:
    """Context for execution mode - holds configuration for a mission"""
    
    def __init__(self, mode: ExecutionMode):
        self.mode = mode
        self.config = get_mode_config(mode)
    
    @property
    def requires_approval_for_medium_risk(self) -> bool:
        """Does this mode require approval for medium-risk operations?"""
        return self.config["require_approval_medium_risk"]
    
    @property
    def requires_approval_for_high_risk(self) -> bool:
        """Does this mode require approval for high-risk operations?"""
        return self.config["require_approval_high_risk"]
    
    @property
    def auto_approves_low_risk(self) -> bool:
        """Does this mode auto-approve low-risk operations?"""
        return self.config["auto_approve_low_risk"]
    
    @property
    def allows_direct_commit(self) -> bool:
        """Does this mode allow direct commits to main branch?"""
        return self.config["allow_direct_commit"]
    
    @property
    def should_create_pr(self) -> bool:
        """Should this mode create a PR instead of direct commit?"""
        return not self.config["allow_direct_commit"]
    
    @property
    def allows_network_access(self) -> bool:
        """Does this mode allow network access in sandboxed execution?"""
        return self.config["allow_network_access"]
    
    @property
    def allows_internet_access(self) -> bool:
        """Does this mode allow internet access in sandboxed execution?"""
        return self.config["allow_internet_access"]
    
    @property
    def timeout_seconds(self) -> int:
        """Execution timeout for this mode"""
        return self.config["timeout_seconds"]
    
    @property
    def max_files_changed(self) -> int:
        """Maximum files that can be changed"""
        return self.config["max_files_changed"]
    
    @property
    def max_lines_changed(self) -> int:
        """Maximum total lines that can be changed"""
        return self.config["max_lines_changed"]
    
    @property
    def max_execution_time_sec(self) -> int:
        """Maximum execution time in seconds"""
        return self.config["max_execution_time_sec"]
    
    def __str__(self):
        return f"{self.mode.value.upper()}: {self.config['description']}"
    
    def get_summary(self) -> dict:
        """Get summary of mode configuration"""
        return {
            "mode": self.mode.value,
            "description": self.config["description"],
            "auto_approve_low_risk": self.auto_approves_low_risk,
            "requires_approval_medium_risk": self.requires_approval_for_medium_risk,
            "requires_approval_high_risk": self.requires_approval_for_high_risk,
            "allows_direct_commit": self.allows_direct_commit,
            "allows_network_access": self.allows_network_access,
            "allows_internet_access": self.allows_internet_access,
            "timeout_seconds": self.timeout_seconds,
            "max_files_changed": self.max_files_changed,
            "max_lines_changed": self.max_lines_changed,
            "max_execution_time_sec": self.max_execution_time_sec,
        }
