"""
Phase 51 Integration Module

Provides integration layer between autonomous phases (39-42) and
new sub-agents (51+) for task distribution and autonomous operation.

Week 1: Test Generation Agent integration with Phase 42
Week 2: PR Review Agent integration (auto-triggered when Week 1 → 2,000 tests)
Week 3: Merge Conflict Agent integration (auto-triggered when Week 2 → 85% approval)
"""

from .phase42_test_generation_integration import (
    Phase42TestGenerationIntegration,
    Phase42PRMetadata,
    TestGenerationResult,
    phase42_post_refactor_hook,
)

from .week2_pr_review_integration import (
    Week2PRReviewIntegration,
    Phase42PRForReview,
    ReviewCascadeResult,
)

__all__ = [
    # Week 1
    "Phase42TestGenerationIntegration",
    "Phase42PRMetadata",
    "TestGenerationResult",
    "phase42_post_refactor_hook",
    # Week 2
    "Week2PRReviewIntegration",
    "Phase42PRForReview",
    "ReviewCascadeResult",
]

__version__ = "0.2.0-week2"
__deployment_status__ = "Week 1 ✅ → Week 2 READY → Week 3 QUEUED"
