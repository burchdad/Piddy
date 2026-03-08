"""ML module for Phase 4 - Machine learning pattern detection."""
from .pattern_detector import MLPatternDetector, get_pattern_detector, CodePattern, PatternInsight
import logging

logger = logging.getLogger(__name__)
__all__ = ["MLPatternDetector", "get_pattern_detector", "CodePattern", "PatternInsight"]
