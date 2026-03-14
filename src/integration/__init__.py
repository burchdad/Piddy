"""
Phase 51 Integration Module

Provides integration layer between autonomous phases (39-42) and
new sub-agents (51+) for task distribution and autonomous operation.

Week 1 Deployment: Test Generation Agent integration with Phase 42
"""

from .phase42_test_generation_integration import (
    Phase42TestGenerationIntegration,
    Phase42PRMetadata,
    TestGenerationResult,
    phase42_post_refactor_hook,
)

__all__ = [
    "Phase42TestGenerationIntegration",
    "Phase42PRMetadata",
    "TestGenerationResult",
    "phase42_post_refactor_hook",
]

__version__ = "0.1.0-week1"
