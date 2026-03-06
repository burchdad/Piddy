"""
ML-based pattern detection for Phase 4.
Uses machine learning to detect code patterns, anti-patterns, and optimization opportunities.
"""
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CodePattern:
    """Detected code pattern."""
    name: str
    pattern_type: str  # 'positive', 'negative', 'optimization'
    language: str
    confidence: float  # 0.0 to 1.0
    examples: List[str]
    description: str
    recommendation: str
    frequency: int = 0


@dataclass
class PatternInsight:
    """ML-generated insights about code patterns."""
    detected_patterns: List[CodePattern]
    risk_score: float
    optimization_score: float
    quality_score: float
    recommendations: List[str]
    pattern_summary: Dict[str, int]


class MLPatternDetector:
    """
    Machine learning-based pattern detection engine.
    Detects code patterns, anti-patterns, and optimization opportunities.
    """

    def __init__(self, learning_file: str = ".pattern_database.json"):
        """Initialize ML pattern detector."""
        self.learning_file = learning_file
        self.patterns_db = self._load_patterns()
        self.pattern_frequencies: Counter = Counter()
        self.language_patterns = self._init_language_patterns()
        logger.info("✅ ML Pattern Detector initialized")

    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from database."""
        try:
            with open(self.learning_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"patterns": {}, "insights": {}}

    def _save_patterns(self) -> None:
        """Save patterns to learning database."""
        try:
            with open(self.learning_file, "w") as f:
                json.dump(self.patterns_db, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def _init_language_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize language-specific pattern detection rules."""
        return {
            "python": {
                "good_practices": [
                    r"def\s+\w+\([^)]*\)\s*->",  # Type hints
                    r"\"\"\"[\s\S]*?\"\"\"",  # Docstrings
                    r"try:\s*.*\s*except\s+\w+\s*as\s+\w+:",  # Proper exception handling
                    r"@(property|staticmethod|classmethod)",  # Decorators
                    r"with\s+\w+\s+as\s+\w+:",  # Context managers
                ],
                "anti_patterns": [
                    r"except\s*:",  # Bare except
                    r"except\s+Exception\s*:",  # Catching all exceptions
                    r"import\s+\*",  # Star imports
                    r"global\s+\w+",  # Global variables
                    r"=\s*\[\w+\s*for\s+\w+\s+in\s+range\(len\(",  # Range+len anti-pattern
                ],
                "optimization_opportunities": [
                    r"for\s+\w+\s+in\s+range\(len\(",  # Use enumerate
                    r"if\s+\w+\s+==\s+True",  # Simplify boolean checks
                    r"\.append\(\)",  # Multiple appends could use list comprehension
                    r"while\s+True",  # Infinite loops (should use break/return)
                ],
            },
            "javascript": {
                "good_practices": [
                    r"const\s+\w+\s*=",  # Use const
                    r"let\s+\w+\s*=",  # Use let
                    r"async\s+function",  # Async functions
                    r"await\s+",  # Proper async handling
                    r"=>\s*\{",  # Arrow functions
                ],
                "anti_patterns": [
                    r"var\s+\w+\s*=",  # Old var keyword
                    r"==\s+",  # Loose equality
                    r"window\.\w+\s*=",  # Global variables
                    r"callback\(\)",  # Callback hell
                ],
                "optimization_opportunities": [
                    r"for\s*\(\w+\s*=\s*0;\s*\w+\s*<\s*\w+\.length",  # Use forEach/map
                    r"\.then\(\)\.then\(\)",  # Multiple promises (use async/await)
                ],
            },
            "typescript": {
                "good_practices": [
                    r"interface\s+\w+\s*\{",  # Interfaces
                    r"type\s+\w+\s*=",  # Type aliases
                    r":\s*\w+",  # Type annotations
                    r"public|private|protected",  # Access modifiers
                ],
                "anti_patterns": [
                    r":\s*any",  # Use of any type
                    r"as\s+any",  # Type assertion to any
                ],
            },
        }

    def detect_patterns(
        self,
        code: str,
        language: str = "python",
    ) -> PatternInsight:
        """
        Detect patterns in code using ML-based rules.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            PatternInsight with detected patterns and recommendations
        """
        detected_patterns: List[CodePattern] = []
        good_count = 0
        bad_count = 0
        optimization_count = 0

        # Get language-specific patterns
        lang_patterns = self.language_patterns.get(language, {})

        # Detect good practices
        for pattern_regex in lang_patterns.get("good_practices", []):
            matches = re.findall(pattern_regex, code)
            if matches:
                good_count += len(matches)
                pattern_name = self._pattern_name_from_regex(pattern_regex)
                detected_patterns.append(
                    CodePattern(
                        name=f"Good: {pattern_name}",
                        pattern_type="positive",
                        language=language,
                        confidence=0.85 + (len(matches) * 0.05),
                        examples=matches[:3],
                        description=f"Found {len(matches)} instances of {pattern_name}",
                        recommendation="Continue using this pattern",
                        frequency=len(matches),
                    )
                )

        # Detect anti-patterns
        for pattern_regex in lang_patterns.get("anti_patterns", []):
            matches = re.findall(pattern_regex, code)
            if matches:
                bad_count += len(matches)
                pattern_name = self._pattern_name_from_regex(pattern_regex)
                confidence = min(0.7 + (len(matches) * 0.1), 0.95)
                detected_patterns.append(
                    CodePattern(
                        name=f"Anti-pattern: {pattern_name}",
                        pattern_type="negative",
                        language=language,
                        confidence=confidence,
                        examples=matches[:2],
                        description=f"Found {len(matches)} instances of {pattern_name}",
                        recommendation=self._get_anti_pattern_fix(pattern_name, language),
                        frequency=len(matches),
                    )
                )

        # Detect optimization opportunities
        for pattern_regex in lang_patterns.get("optimization_opportunities", []):
            matches = re.findall(pattern_regex, code)
            if matches:
                optimization_count += len(matches)
                pattern_name = self._pattern_name_from_regex(pattern_regex)
                detected_patterns.append(
                    CodePattern(
                        name=f"Optimization: {pattern_name}",
                        pattern_type="optimization",
                        language=language,
                        confidence=0.65 + (len(matches) * 0.05),
                        examples=matches[:2],
                        description=f"Found {len(matches)} optimization opportunities",
                        recommendation=self._get_optimization_suggestion(pattern_name, language),
                        frequency=len(matches),
                    )
                )

        # Calculate quality scores
        total_patterns = len(code.split("\n")) / 10  # Normalized by lines
        risk_score = (bad_count / max(total_patterns, 1)) * 100
        optimization_score = (optimization_count / max(total_patterns, 1)) * 100
        quality_score = max(0, 100 - risk_score - (optimization_score * 0.5))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            detected_patterns, good_count, bad_count, optimization_count
        )

        # Create pattern summary
        pattern_summary = {
            "good_practices": good_count,
            "anti_patterns": bad_count,
            "optimization_opportunities": optimization_count,
        }

        # Update pattern database
        for pattern in detected_patterns:
            self.pattern_frequencies[pattern.name] += pattern.frequency

        return PatternInsight(
            detected_patterns=detected_patterns,
            risk_score=min(risk_score, 100),
            optimization_score=min(optimization_score, 100),
            quality_score=max(quality_score, 0),
            recommendations=recommendations,
            pattern_summary=pattern_summary,
        )

    def _pattern_name_from_regex(self, regex: str) -> str:
        """Extract human-readable name from regex pattern."""
        patterns_map = {
            r"def\s+\w+\([^)]*\)\s*->": "Type hints",
            r"\"\"\"[\s\S]*?\"\"\"": "Docstrings",
            r"except\s+\w+\s+as\s+\w+": "Proper exception handling",
            r"@(property|staticmethod|classmethod)": "Decorators",
            r"with\s+\w+\s+as\s+\w+": "Context managers",
            r"except\s*:": "Bare except clause",
            r"except\s+Exception\s*:": "Catch-all exceptions",
            r"import\s+\*": "Star imports",
            r"global\s+\w+": "Global variables",
            r"for\s+\w+\s+in\s+range\(len\(": "Range+len pattern",
            r"if\s+\w+\s+==\s+True": "Boolean comparison",
            r"\.append\(\)": "Multiple appends",
            r"while\s+True": "Infinite loops",
            r"const\s+\w+\s*=": "Const declaration",
            r"var\s+\w+\s*=": "Old var keyword",
            r"==\s+": "Loose equality",
            r":\s*any": "Any type usage",
        }
        return patterns_map.get(regex, "Unknown pattern")

    def _get_anti_pattern_fix(self, pattern_name: str, language: str) -> str:
        """Get fix recommendation for anti-pattern."""
        fixes = {
            "Bare except clause": "Use specific exception types: except SpecificError as e:",
            "Catch-all exceptions": "Catch specific exceptions you can handle",
            "Star imports": "Import specific functions/classes: from module import function",
            "Global variables": "Use function parameters or class attributes instead",
            "Range+len pattern": "Use enumerate() for cleaner iteration",
            "Old var keyword": "Use const or let for proper scoping",
            "Loose equality": "Use strict equality (=== or !==)",
            "Any type usage": "Define specific types instead of using any",
        }
        return fixes.get(pattern_name, "Consider refactoring this pattern")

    def _get_optimization_suggestion(self, pattern_name: str, language: str) -> str:
        """Get optimization suggestion."""
        suggestions = {
            "Range+len pattern": "Use enumerate(list) for direct access and cleaner code",
            "Boolean comparison": "Use: if condition: instead of if condition == True:",
            "Multiple appends": "Consider using list comprehension [item for item in items]",
            "Infinite loops": "Use break statements or return to exit loops explicitly",
            "For loop with length": "Use forEach, map, or filter for functional style",
            "Multiple promises": "Use async/await for cleaner promise handling",
        }
        return suggestions.get(pattern_name, "Review this pattern for optimization")

    def _generate_recommendations(
        self,
        patterns: List[CodePattern],
        good: int,
        bad: int,
        optimization: int,
    ) -> List[str]:
        """Generate AI-driven recommendations."""
        recommendations = []

        if bad == 0 and good > 5:
            recommendations.append("✅ Excellent code quality with strong best practices")
        elif bad > 0:
            recommendations.append(
                f"⚠️ Address {bad} anti-pattern(s) to improve code quality"
            )

        if optimization > 0:
            recommendations.append(
                f"💡 {optimization} optimization opportunity/opportunities available"
            )

        if good < 3:
            recommendations.append("📚 Consider applying more best practices from your language")

        if not recommendations:
            recommendations.append("➡️ Code is acceptable; continue current practices")

        return recommendations

    def learn_from_pattern(
        self,
        code: str,
        language: str,
        outcome: str,  # 'success' or 'failure'
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Learn from code patterns and outcomes.

        Args:
            code: Source code
            language: Programming language
            outcome: 'success' or 'failure'
            metadata: Additional context
        """
        insight = self.detect_patterns(code, language)

        # Store in learning database
        key = f"{language}_{outcome}"
        if key not in self.patterns_db["insights"]:
            self.patterns_db["insights"][key] = []

        self.patterns_db["insights"][key].append({
            "timestamp": datetime.now().isoformat(),
            "patterns": [asdict(p) for p in insight.detected_patterns],
            "scores": {
                "risk": insight.risk_score,
                "optimization": insight.optimization_score,
                "quality": insight.quality_score,
            },
            "metadata": metadata or {},
        })

        self._save_patterns()
        logger.debug(f"Learned pattern: {language} {outcome}")

    def get_pattern_recommendations(self, language: str) -> List[Dict[str, Any]]:
        """Get AI recommendations based on learned patterns."""
        recommendations = []

        success_patterns = self.patterns_db["insights"].get(f"{language}_success", [])
        failure_patterns = self.patterns_db["insights"].get(f"{language}_failure", [])

        if success_patterns:
            avg_quality = np.mean([p["scores"]["quality"] for p in success_patterns])
            recommendations.append({
                "type": "quality_level",
                "language": language,
                "average_quality": avg_quality,
                "message": f"Average code quality for successful {language} patterns: {avg_quality:.1f}%",
            })

        if failure_patterns:
            failure_antis = Counter()
            for p in failure_patterns:
                for pattern in p["patterns"]:
                    if pattern["pattern_type"] == "negative":
                        failure_antis[pattern["name"]] += pattern["frequency"]

            if failure_antis:
                top_anti = failure_antis.most_common(1)[0]
                recommendations.append({
                    "type": "avoid_pattern",
                    "pattern": top_anti[0],
                    "frequency_in_failures": top_anti[1],
                    "message": f"Avoid '{top_anti[0]}' - frequently appears in failed {language} code",
                })

        return recommendations


# Global pattern detector instance
_detector_instance: Optional[MLPatternDetector] = None


def get_pattern_detector() -> MLPatternDetector:
    """Get or create global pattern detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MLPatternDetector()
    return _detector_instance
