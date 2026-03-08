"""Common base classes for phase modules.

logger = logging.getLogger(__name__)
Consolidates duplicate __init__ patterns into reusable base classes.
"""
from src.common.base_component import (
import logging
    BaseAutonomyEngine,
    BaseComponent,
    BaseEcosystemPlugin,
    BaseServiceManager,
    BaseStreamProcessor,
)

__all__ = [
    "BaseComponent",
    "BaseServiceManager",
    "BaseStreamProcessor",
    "BaseAutonomyEngine",
    "BaseEcosystemPlugin",
]
