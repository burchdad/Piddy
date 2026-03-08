"""
logger = logging.getLogger(__name__)
Phase 19: Self-Improving Agent with Continuous Learning

Transform Piddy from static AI developer to continuously learning, self-improving system:
- Learn from code changes and outcomes
- Track success/failure patterns
- Adapt decision-making based on historical performance
- Continuous pattern refinement
- Autonomous capability improvement
- Performance-based strategy evolution
- Feedback loop integration with git history
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import hashlib
from collections import defaultdict
import statistics
import logging


class OutcomeType(Enum):
    """Outcome of an action"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ChangeCategory(Enum):
    """Category of code change"""
    REFACTORING = "refactoring"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    OPTIMIZATION = "optimization"
    CLEANUP = "cleanup"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    TESTING = "testing"


@dataclass
class LearningEvent:
    """A learning event - code change with outcome"""
    event_id: str
    timestamp: datetime
    file_path: str
    change_type: ChangeCategory
    description: str
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    outcome: OutcomeType = OutcomeType.UNKNOWN
    success_score: float = 0.0  # 0.0-1.0
    performance_delta: float = 0.0  # relative improvement
    pattern_detected: Optional[str] = None
    decision_reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'file_path': self.file_path,
            'change_type': self.change_type.value,
            'description': self.description,
            'outcome': self.outcome.value,
            'success_score': self.success_score,
            'performance_delta': self.performance_delta,
            'pattern_detected': self.pattern_detected,
            'decision_reasoning': self.decision_reasoning,
            'metadata': self.metadata
        }


@dataclass
class LearnedPattern:
    """A pattern learned by the system"""
    pattern_id: str
    pattern_name: str
    description: str
    contexts: List[str] = field(default_factory=list)  # where it applies
    success_rate: float = 0.0  # 0.0-1.0
    avg_performance_gain: float = 0.0
    occurrences: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0  # 0.0-1.0
    recommended: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'pattern_name': self.pattern_name,
            'description': self.description,
            'success_rate': self.success_rate,
            'avg_performance_gain': self.avg_performance_gain,
            'occurrences': self.occurrences,
            'confidence': self.confidence,
            'recommended': self.recommended
        }


class LearningDatabase:
    """Persistent learning database - SQLite-backed"""

    def __init__(self, db_path: str = '/workspaces/Piddy/.piddy_learning.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()

        # Learning events table
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_events (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            file_path TEXT NOT NULL,
            change_type TEXT NOT NULL,
            description TEXT,
            outcome TEXT,
            success_score REAL,
            performance_delta REAL,
            pattern_detected TEXT,
            decision_reasoning TEXT,
            metadata TEXT
        )''')

        # Learned patterns table
        cursor.execute('''CREATE TABLE IF NOT EXISTS learned_patterns (
            pattern_id TEXT PRIMARY KEY,
            pattern_name TEXT NOT NULL,
            description TEXT,
            success_rate REAL,
            avg_performance_gain REAL,
            occurrences INTEGER,
            last_updated TEXT,
            confidence REAL,
            recommended BOOLEAN
        )''')

        # Statistics table
        cursor.execute('''CREATE TABLE IF NOT EXISTS statistics (
            stat_key TEXT PRIMARY KEY,
            stat_value REAL,
            updated TEXT
        )''')

        self.conn.commit()

    def add_event(self, event: LearningEvent) -> bool:
        """Add a learning event"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO learning_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (
                             event.event_id,
                             event.timestamp.isoformat(),
                             event.file_path,
                             event.change_type.value,
                             event.description,
                             event.outcome.value,
                             event.success_score,
                             event.performance_delta,
                             event.pattern_detected,
                             event.decision_reasoning,
                             json.dumps(event.metadata)
                         ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.info(f"Error adding event: {e}")
            return False

    def get_events(self, file_path: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get events, optionally filtered by file"""
        cursor = self.conn.cursor()
        if file_path:
            cursor.execute('SELECT * FROM learning_events WHERE file_path = ? ORDER BY timestamp DESC LIMIT ?',
                         (file_path, limit))
        else:
            cursor.execute('SELECT * FROM learning_events ORDER BY timestamp DESC LIMIT ?', (limit,))
        
        columns = ['event_id', 'timestamp', 'file_path', 'change_type', 'description',
                   'outcome', 'success_score', 'performance_delta', 'pattern_detected',
                   'decision_reasoning', 'metadata']
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def add_pattern(self, pattern: LearnedPattern) -> bool:
        """Add a learned pattern"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO learned_patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (
                             pattern.pattern_id,
                             pattern.pattern_name,
                             pattern.description,
                             pattern.success_rate,
                             pattern.avg_performance_gain,
                             pattern.occurrences,
                             pattern.last_updated.isoformat(),
                             pattern.confidence,
                             pattern.recommended
                         ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.info(f"Error adding pattern: {e}")
            return False

    def get_pattern(self, pattern_id: str) -> Optional[Dict]:
        """Get a specific pattern"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM learned_patterns WHERE pattern_id = ?', (pattern_id,))
        row = cursor.fetchone()
        if row:
            columns = ['pattern_id', 'pattern_name', 'description', 'success_rate',
                      'avg_performance_gain', 'occurrences', 'last_updated', 'confidence', 'recommended']
            return dict(zip(columns, row))
        return None

    def get_recommended_patterns(self) -> List[Dict]:
        """Get recommended patterns"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM learned_patterns WHERE recommended = 1 ORDER BY success_rate DESC')
        columns = ['pattern_id', 'pattern_name', 'description', 'success_rate',
                   'avg_performance_gain', 'occurrences', 'last_updated', 'confidence', 'recommended']
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def update_statistic(self, key: str, value: float):
        """Update a statistic"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO statistics VALUES (?, ?, ?)',
                      (key, value, datetime.now().isoformat()))
        self.conn.commit()

    def get_statistic(self, key: str, default: float = 0.0) -> float:
        """Get a statistic"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT stat_value FROM statistics WHERE stat_key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class PatternLearner:
    """Learn patterns from code changes"""

    def __init__(self, repo_root: str = '/workspaces/Piddy'):
        self.repo_root = repo_root
        self.patterns: Dict[str, LearnedPattern] = {}
        self.recent_events: List[LearningEvent] = []

    def extract_patterns_from_event(self, event: LearningEvent) -> List[str]:
        """Extract patterns from a learning event"""
        patterns = []

        # Size-based pattern
        if event.code_before and event.code_after:
            lines_before = len(event.code_before.splitlines())
            lines_after = len(event.code_after.splitlines())
            if lines_after < lines_before * 0.8:
                patterns.append('code_simplification')
            elif lines_after > lines_before * 1.2:
                patterns.append('code_expansion')

        # Outcome-based pattern
        if event.outcome == OutcomeType.SUCCESS:
            patterns.append(f'successful_{event.change_type.value}')

        # Performance-based pattern
        if event.performance_delta > 0.1:
            patterns.append('performance_improvement')
        elif event.performance_delta < -0.1:
            patterns.append('performance_regression')

        return patterns

    def update_pattern(self, pattern_name: str, event: LearningEvent):
        """Update a pattern based on event"""
        pattern_id = hashlib.md5(pattern_name.encode()).hexdigest()[:8]

        if pattern_id not in self.patterns:
            self.patterns[pattern_id] = LearnedPattern(
                pattern_id=pattern_id,
                pattern_name=pattern_name,
                description=f"Pattern: {pattern_name}"
            )

        pattern = self.patterns[pattern_id]
        
        # Update success rate
        old_success = pattern.success_rate * pattern.occurrences
        new_success = old_success + (1.0 if event.outcome == OutcomeType.SUCCESS else 0.0)
        pattern.occurrences += 1
        pattern.success_rate = new_success / pattern.occurrences

        # Update performance gain
        old_gain = pattern.avg_performance_gain * (pattern.occurrences - 1)
        new_gain = old_gain + event.performance_delta
        pattern.avg_performance_gain = new_gain / pattern.occurrences

        # Update confidence
        if pattern.occurrences >= 3:
            pattern.confidence = min(0.95, pattern.success_rate * 0.95)

        # Mark as recommended if meets criteria
        if pattern.success_rate > 0.7 and pattern.occurrences >= 3:
            pattern.recommended = True

        pattern.last_updated = datetime.now()

    def get_pattern_recommendations(self) -> List[LearnedPattern]:
        """Get recommended patterns"""
        return sorted(
            [p for p in self.patterns.values() if p.recommended],
            key=lambda p: (p.success_rate, p.confidence),
            reverse=True
        )


class PerformanceTracker:
    """Track performance metrics and improvements"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.baseline: Dict[str, float] = {}

    def record_metric(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.baseline:
            self.baseline[metric_name] = value
        self.metrics[metric_name].append(value)

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}

        values = self.metrics[metric_name]
        return {
            'current': values[-1],
            'baseline': self.baseline.get(metric_name, 0.0),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'improvement': 1 - (values[-1] / self.baseline.get(metric_name, 1.0))
        }

    def get_all_metrics_summary(self) -> Dict[str, Dict]:
        """Get summary of all metrics"""
        return {name: self.get_metric_stats(name) for name in self.metrics.keys()}


class DecisionAdapter:
    """Adapt decisions based on learning history"""

    def __init__(self, learning_db: LearningDatabase, pattern_learner: PatternLearner):
        self.db = learning_db
        self.learner = pattern_learner
        self.decision_history: List[Dict] = []

    def make_adaptive_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on learned patterns"""
        file_path = context.get('file_path', '')
        change_type = context.get('change_type', 'feature')

        # Get historical events for this file
        events = self.db.get_events(file_path, limit=10)
        
        # Analyze success patterns
        successful_changes = [e for e in events if e.get('outcome') == 'success']
        success_rate = len(successful_changes) / len(events) if events else 0.5

        # Get recommended patterns
        recommended = self.learner.get_pattern_recommendations()

        # Build decision
        decision = {
            'timestamp': datetime.now().isoformat(),
            'recommended_patterns': [p.pattern_name for p in recommended[:3]],
            'success_probability': success_rate,
            'confidence': 0.7 if success_rate > 0.5 else 0.5,
            'historical_performance': {
                'total_changes': len(events),
                'successful': len(successful_changes),
                'avg_performance_delta': statistics.mean([e.get('performance_delta', 0) for e in events]) if events else 0
            },
            'context': context
        }

        self.decision_history.append(decision)
        return decision

    def get_decision_history(self) -> List[Dict]:
        """Get decision history"""
        return self.decision_history


class SelfImprovingAgent:
    """Complete Self-Improving Agent - Phase 19"""

    def __init__(self, repo_root: str = '/workspaces/Piddy'):
        self.repo_root = repo_root
        self.db = LearningDatabase()
        self.pattern_learner = PatternLearner(repo_root)
        self.performance_tracker = PerformanceTracker()
        self.decision_adapter = DecisionAdapter(self.db, self.pattern_learner)
        self.autonomy_level = 0.88  # Inherited from Phase 18
        self.learning_rate = 0.1  # How quickly to adapt

    def record_code_change(self, file_path: str, change_type: str, description: str,
                          code_before: Optional[str] = None, code_after: Optional[str] = None,
                          outcome: str = 'unknown', success_score: float = 0.0,
                          performance_delta: float = 0.0) -> str:
        """Record a code change for learning"""
        
        # Create event
        event_id = hashlib.md5(
            f"{file_path}{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        event = LearningEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            file_path=file_path,
            change_type=ChangeCategory[change_type.upper()] if change_type.upper() in ChangeCategory.__members__ else ChangeCategory.FEATURE,
            description=description,
            code_before=code_before,
            code_after=code_after,
            outcome=OutcomeType[outcome.upper()] if outcome.upper() in OutcomeType.__members__ else OutcomeType.UNKNOWN,
            success_score=success_score,
            performance_delta=performance_delta
        )

        # Store in database
        self.db.add_event(event)
        self.pattern_learner.recent_events.append(event)

        # Extract and learn patterns
        patterns = self.pattern_learner.extract_patterns_from_event(event)
        for pattern_name in patterns:
            self.pattern_learner.update_pattern(pattern_name, event)

        # Update database with patterns
        for pattern in self.pattern_learner.patterns.values():
            self.db.add_pattern(pattern)

        return event_id

    def get_adaptation_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get adaptive decision based on learning"""
        decision = self.decision_adapter.make_adaptive_decision(context)
        
        # Boost autonomy if success rate is high
        successful_rate = decision['success_probability']
        self.autonomy_level = min(0.98, 0.88 + successful_rate * 0.1)

        return decision

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'phase': 19,
            'status': 'SELF-IMPROVING AGENT ACTIVE',
            'autonomy_level': self.autonomy_level * 100,
            'learning_rate': self.learning_rate * 100,
            'total_events_recorded': len(self.pattern_learner.recent_events),
            'patterns_discovered': len(self.pattern_learner.patterns),
            'recommended_patterns': len([p for p in self.pattern_learner.patterns.values() if p.recommended]),
            'performance_metrics': self.performance_tracker.get_all_metrics_summary(),
            'decisions_made': len(self.decision_adapter.decision_history),
            'capabilities': [
                'Learn from code changes',
                'Identify patterns in decision outcomes',
                'Adapt strategy based on success rates',
                'Track performance improvements',
                'Make data-driven decisions',
                'Continuously improve autonomy level'
            ]
        }

    def get_improvement_report(self) -> Dict[str, Any]:
        """Get detailed improvement report"""
        events = self.db.get_events(limit=100)
        
        if not events:
            return {'message': 'No learning events recorded yet'}

        # Calculate metrics
        successful = len([e for e in events if e.get('outcome') == 'success'])
        failed = len([e for e in events if e.get('outcome') == 'failure'])
        partial = len([e for e in events if e.get('outcome') == 'partial'])
        
        success_rate = successful / len(events) if events else 0
        avg_performance = statistics.mean([e.get('performance_delta', 0) for e in events])
        
        # Get top patterns
        top_patterns = sorted(
            [p.to_dict() for p in self.pattern_learner.patterns.values()],
            key=lambda p: (p['success_rate'], p['confidence']),
            reverse=True
        )[:5]

        return {
            'timestamp': datetime.now().isoformat(),
            'total_events': len(events),
            'success_rate': success_rate * 100,
            'outcomes': {
                'successful': successful,
                'failed': failed,
                'partial': partial,
                'unknown': len(events) - successful - failed - partial
            },
            'avg_performance_delta': avg_performance,
            'patterns_learned': len(self.pattern_learner.patterns),
            'recommended_patterns': len([p for p in self.pattern_learner.patterns.values() if p.recommended]),
            'top_patterns': top_patterns,
            'autonomy_evolution': f"{0.88} -> {self.autonomy_level:.2f}"
        }

    def close(self):
        """Clean up resources"""
        self.db.close()


# Export
__all__ = [
    'SelfImprovingAgent',
    'LearningEvent',
    'LearnedPattern',
    'LearningDatabase',
    'PatternLearner',
    'PerformanceTracker',
    'DecisionAdapter',
    'OutcomeType',
    'ChangeCategory'
]
