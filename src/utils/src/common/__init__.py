"""Common base classes for phase modules.

Consolidates duplicate __init__ patterns into reusable base classes.
"""
import logging
from src.common.base_component import (
    BaseAutonomyEngine,
    BaseComponent,
    BaseEcosystemPlugin,
    BaseServiceManager,
    BaseStreamProcessor,
)

logger = logging.getLogger(__name__)

__all__ = [
    "BaseComponent",
    "BaseServiceManager",
    "BaseStreamProcessor",
    "BaseAutonomyEngine",
    "BaseEcosystemPlugin",
]
