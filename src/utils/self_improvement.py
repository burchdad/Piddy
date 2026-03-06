"""
Self-improvement system for Piddy.

Learns from successful code generation and analysis patterns,
continuously refines recommendations and detection rules.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PatternOccurrence:
    """Record of a pattern being observed."""
    pattern: str
    language: str
    context: Dict[str, Any]
    success: bool
    effectiveness_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GeneratedCode:
    """Track generated code and its outcomes."""
    code: str
    language: str
    tool_used: str
    user_feedback: Optional[str] = None
    success_indicators: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0


class PatternLearner:
    """
    Learn from successful code patterns and improve recommendations.
    """
    
    def __init__(self, memory_file: str = ".piddy_patterns.json"):
        self.memory_file = memory_file
        self.patterns: Dict[str, List[PatternOccurrence]] = defaultdict(list)
        self.code_history: List[GeneratedCode] = []
        self.load_memory()
    
    def load_memory(self) -> None:
        """Load learned patterns from disk."""
        if Path(self.memory_file).exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct pattern occurrences
                    for key, occurrences in data.get("patterns", {}).items():
                        for occ_data in occurrences:
                            occ = PatternOccurrence(
                                pattern=occ_data["pattern"],
                                language=occ_data["language"],
                                context=occ_data["context"],
                                success=occ_data["success"],
                                effectiveness_score=occ_data.get("effectiveness_score", 0.0),
                                timestamp=datetime.fromisoformat(occ_data["timestamp"]),
                            )
                            self.patterns[key].append(occ)
                    
                    logger.info(f"Loaded {len(self.patterns)} learned patterns")
            except Exception as e:
                logger.error(f"Failed to load pattern memory: {e}")
    
    def save_memory(self) -> None:
        """Save learned patterns to disk."""
        try:
            data = {
                "patterns": {
                    key: [
                        {
                            "pattern": occ.pattern,
                            "language": occ.language,
                            "context": occ.context,
                            "success": occ.success,
                            "effectiveness_score": occ.effectiveness_score,
                            "timestamp": occ.timestamp.isoformat(),
                        }
                        for occ in occurrences
                    ]
                    for key, occurrences in self.patterns.items()
                },
                "last_updated": datetime.now().isoformat(),
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save pattern memory: {e}")
    
    def record_pattern(
        self,
        pattern: str,
        language: str,
        context: Dict[str, Any],
        success: bool
    ) -> None:
        """Record a pattern occurrence."""
        occ = PatternOccurrence(
            pattern=pattern,
            language=language,
            context=context,
            success=success,
            effectiveness_score=1.0 if success else 0.0,
        )
        
        key = f"{language}:{pattern}"
        self.patterns[key].append(occ)
        
        if len(self.patterns[key]) > 1000:
            # Keep only recent occurrences
            self.patterns[key] = self.patterns[key][-1000:]
    
    def get_successful_patterns(
        self,
        language: str,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Get patterns that have been successful."""
        successful = []
        
        for key, occurrences in self.patterns.items():
            if not key.startswith(f"{language}:"):
                continue
            
            # Filter recent occurrences
            cutoff = datetime.now() - timedelta(days=30)
            recent = [o for o in occurrences if o.timestamp > cutoff]
            
            if len(recent) < min_occurrences:
                continue
            
            success_count = sum(1 for o in recent if o.success)
            success_rate = success_count / len(recent)
            
            if success_rate > 0.7:  # 70% success rate
                pattern_name = key.split(":")[-1]
                successful.append({
                    "pattern": pattern_name,
                    "success_rate": f"{success_rate*100:.1f}%",
                    "occurrences": len(recent),
                    "effectiveness": success_rate,
                })
        
        return sorted(successful, key=lambda x: x["effectiveness"], reverse=True)
    
    def get_recommendations(self, language: str) -> List[str]:
        """Get improvement recommendations based on learning."""
        patterns = self.get_successful_patterns(language, min_occurrences=2)
        
        recommendations = []
        for pattern in patterns[:5]:  # Top 5
            recommendations.append(
                f"Use pattern '{pattern['pattern']}' (success rate: {pattern['success_rate']})"
            )
        
        return recommendations


class CodeEvolutionTracker:
    """
    Track how generated code evolves and improves over time.
    """
    
    def __init__(self):
        self.evolutions: Dict[str, List[GeneratedCode]] = defaultdict(list)
    
    def record_generation(self, code: GeneratedCode) -> None:
        """Record generated code."""
        self.evolutions[code.language].append(code)
    
    def get_quality_trend(self, language: str) -> Dict[str, Any]:
        """Get quality trend for generated code."""
        codes = self.evolutions[language]
        
        if not codes:
            return {"message": "No code history"}
        
        # Sort by timestamp
        codes.sort(key=lambda x: x.timestamp)
        
        # Calculate trend
        recent_10 = codes[-10:]
        avg_recent = sum(c.quality_score for c in recent_10) / len(recent_10)
        
        old_10 = codes[:10]
        avg_old = sum(c.quality_score for c in old_10) / len(old_10) if old_10 else 0
        
        improvement = avg_recent - avg_old
        
        return {
            "language": language,
            "total_generations": len(codes),
            "recent_avg_quality": f"{avg_recent:.2f}",
            "improvement": f"{improvement:+.2f}",
            "trend": "improving" if improvement > 0 else "declining",
        }
    
    def get_most_used_tools(self) -> Dict[str, int]:
        """Get which tools generate the best code."""
        tool_scores: Dict[str, List[float]] = defaultdict(list)
        
        for codes in self.evolutions.values():
            for code in codes:
                tool_scores[code.tool_used].append(code.quality_score)
        
        tool_avg = {
            tool: sum(scores) / len(scores)
            for tool, scores in tool_scores.items()
        }
        
        return dict(sorted(tool_avg.items(), key=lambda x: x[1], reverse=True))


class FailureAnalyzer:
    """
    Analyze failures to prevent recurrence.
    """
    
    def __init__(self):
        self.failures: List[Dict[str, Any]] = []
        self.failure_patterns: Dict[str, int] = defaultdict(int)
    
    def record_failure(
        self,
        tool: str,
        language: str,
        error: str,
        context: Dict[str, Any]
    ) -> None:
        """Record a failure."""
        failure = {
            "tool": tool,
            "language": language,
            "error": error,
            "context": context,
            "timestamp": datetime.now(),
        }
        
        self.failures.append(failure)
        
        # Extract pattern
        error_pattern = error.split(':')[0]  # First part of error
        self.failure_patterns[f"{tool}:{error_pattern}"] += 1
    
    def get_frequent_failures(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get frequently occurring failures."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_failures = [
            f for f in self.failures
            if f["timestamp"] > cutoff
        ]
        
        # Group by pattern
        patterns: Dict[str, List] = defaultdict(list)
        for failure in recent_failures:
            key = f"{failure['tool']}:{failure['error']}"
            patterns[key].append(failure)
        
        # Sort by frequency
        frequent = sorted(
            [(pattern, len(failures)) for pattern, failures in patterns.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "pattern": pattern,
                "count": count,
                "examples": [f["language"] for f in patterns[pattern][:3]],
            }
            for pattern, count in frequent[:10]
        ]
    
    def get_prevention_advice(self, tool: str) -> Optional[str]:
        """Get advice on preventing failures for a tool."""
        tool_failures = [f for f in self.failures if f["tool"] == tool]
        
        if not tool_failures:
            return None
        
        most_common_error = max(
            set(f["error"] for f in tool_failures),
            key=lambda x: sum(1 for f in tool_failures if f["error"] == x)
        )
        
        return f"Tool '{tool}' frequently fails with: {most_common_error}. Consider adding input validation."


# Global instances
_pattern_learner = PatternLearner()
_code_tracker = CodeEvolutionTracker()
_failure_analyzer = FailureAnalyzer()


def get_pattern_learner() -> PatternLearner:
    """Get global pattern learner."""
    return _pattern_learner


def get_code_evolution_tracker() -> CodeEvolutionTracker:
    """Get global code evolution tracker."""
    return _code_tracker


def get_failure_analyzer() -> FailureAnalyzer:
    """Get global failure analyzer."""
    return _failure_analyzer
