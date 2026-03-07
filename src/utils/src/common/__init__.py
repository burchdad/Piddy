"""Common base classes for phase modules.

Consolidates duplicate __init__ patterns into reusable base classes.
"""
from src.common.base_component import (
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
