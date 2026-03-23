import logging
"""
logger = logging.getLogger(__name__)
Piddy - Advanced DevOps & MLOps Integration Platform
Phase 5: Advanced capabilities for production-grade systems
"""

__version__ = "5.2.0"
__author__ = "DevOps Team"
__description__ = "Advanced DevOps & MLOps Integration Platform"

try:
    from .core import Phase5Core
    from .ml_ops_handler import get_ml_ops_handler
    from .observability import get_observability_manager
    from .iac.validator import get_iac_validator
    
    __all__ = [
        "Phase5Core",
        "get_ml_ops_handler",
        "get_observability_manager",
        "get_iac_validator",
    ]
except ImportError:
    # Phase 5 components not yet loaded
    pass
