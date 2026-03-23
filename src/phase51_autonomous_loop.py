"""
Phase 51: Autonomous Loop Engine

The missing intelligence layer that transforms Piddy from a structured pipeline
into a true autonomous dev agent:

    Task -> Try -> Fail -> Diagnose -> Fix -> Retry -> Succeed

Three integrated systems:
1. AutonomousLoop   - Try/fail/retry execution with diagnosis between attempts
2. ToolDecisionLayer - Agents dynamically choose tools based on context
3. FailureMemory     - Persistent record of what failed and why, queried before every attempt

Wires into existing components:
- phase19 (LearningDatabase) for pattern storage
- phase28 (PersistentRepositoryGraph) for knowledge-graph-guided decisions
- phase50 (Phase50Orchestrator) for consensus when strategy changes mid-loop
- nova_coordinator (NovaCoordinator) as the outer execution shell
"""

import logging
import hashlib
import json
import sqlite3
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 2
STRATEGY_POOL = [
    "direct_execution",
    "simplify_and_retry",
    "decompose_subtasks",
    "alternative_tool",
    "rollback_and_patch",
    "synthesize_tool",
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


class AttemptOutcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class FailureRecord:
    """One failed attempt with diagnosis."""
    attempt_number: int
    timestamp: str
    error_type: str
    error_message: str
    strategy_used: str
    diagnosis: str
    suggested_fix: str
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LoopResult:
    """Result of the full autonomous loop."""
    task: str
    status: str  # success | failed | partial
    attempts: int
    total_duration_ms: int
    final_output: Dict[str, Any] = field(default_factory=dict)
    failure_history: List[FailureRecord] = field(default_factory=list)
    strategy_evolution: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "failure_history": [f.to_dict() for f in self.failure_history],
        }


# ===================================================================
# 1. FAILURE MEMORY - persistent store queried BEFORE every attempt
# ===================================================================


class FailureMemory:
    """
    Persistent failure memory backed by SQLite.

    Before attempting a task, query this to learn:
    - Has a similar task failed before?
    - What error did it hit?
    - What fix was attempted?
    - Did the fix work?

    This directly feeds the autonomous loop's strategy selection.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).resolve().parent.parent / "data" / "failure_memory.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS failures (
                failure_id   TEXT PRIMARY KEY,
                task_hash    TEXT NOT NULL,
                task_text    TEXT NOT NULL,
                error_type   TEXT NOT NULL,
                error_msg    TEXT,
                strategy     TEXT,
                diagnosis    TEXT,
                fix_applied  TEXT,
                fix_worked   INTEGER DEFAULT 0,
                attempt_num  INTEGER DEFAULT 1,
                timestamp    TEXT NOT NULL,
                context      TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                strategy_id TEXT PRIMARY KEY,
                task_hash   TEXT NOT NULL,
                strategy    TEXT NOT NULL,
                times_used  INTEGER DEFAULT 1,
                times_worked INTEGER DEFAULT 0,
                avg_latency_ms REAL DEFAULT 0,
                last_used   TEXT
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_task_hash ON failures(task_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_error_type ON failures(error_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strat_task ON strategies(task_hash)")

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_task(task: str) -> str:
        normalized = " ".join(task.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record_failure(self, task: str, record: FailureRecord) -> None:
        """Persist a single failure attempt."""
        task_hash = self._hash_task(task)
        fid = f"f_{task_hash}_{record.attempt_number}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO failures
               (failure_id, task_hash, task_text, error_type, error_msg,
                strategy, diagnosis, fix_applied, attempt_num, timestamp, context)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                fid,
                task_hash,
                task,
                record.error_type,
                record.error_message,
                record.strategy_used,
                record.diagnosis,
                record.suggested_fix,
                record.attempt_number,
                record.timestamp,
                json.dumps(record.context),
            ),
        )
        conn.commit()
        conn.close()

    def record_strategy_outcome(
        self, task: str, strategy: str, worked: bool, latency_ms: float
    ) -> None:
        """Update running stats for a strategy applied to this task class."""
        task_hash = self._hash_task(task)
        sid = f"s_{task_hash}_{hashlib.md5(strategy.encode()).hexdigest()[:8]}"
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT times_used, times_worked, avg_latency_ms FROM strategies WHERE strategy_id = ?", (sid,))
        row = cur.fetchone()
        if row:
            used, won, avg_lat = row
            new_used = used + 1
            new_won = won + (1 if worked else 0)
            new_lat = ((avg_lat * used) + latency_ms) / new_used
            cur.execute(
                "UPDATE strategies SET times_used=?, times_worked=?, avg_latency_ms=?, last_used=? WHERE strategy_id=?",
                (new_used, new_won, new_lat, datetime.utcnow().isoformat(), sid),
            )
        else:
            cur.execute(
                "INSERT INTO strategies (strategy_id, task_hash, strategy, times_used, times_worked, avg_latency_ms, last_used) VALUES (?,?,?,1,?,?,?)",
                (sid, task_hash, strategy, 1 if worked else 0, latency_ms, datetime.utcnow().isoformat()),
            )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Read / Query
    # ------------------------------------------------------------------

    def get_past_failures(self, task: str, limit: int = 10) -> List[Dict]:
        """Get failures for a similar task (exact hash match)."""
        task_hash = self._hash_task(task)
        conn = self._conn()
        cur = conn.execute(
            "SELECT * FROM failures WHERE task_hash = ? ORDER BY timestamp DESC LIMIT ?",
            (task_hash, limit),
        )
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_all_failures_by_error(self, error_type: str, limit: int = 20) -> List[Dict]:
        """Get failures across all tasks for the same error type."""
        conn = self._conn()
        cur = conn.execute(
            "SELECT * FROM failures WHERE error_type = ? ORDER BY timestamp DESC LIMIT ?",
            (error_type, limit),
        )
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_strategy_stats(self, task: str) -> List[Dict]:
        """Get strategy success rates for a task class."""
        task_hash = self._hash_task(task)
        conn = self._conn()
        cur = conn.execute(
            "SELECT strategy, times_used, times_worked, avg_latency_ms FROM strategies WHERE task_hash = ? ORDER BY times_worked DESC",
            (task_hash,),
        )
        rows = [
            {
                "strategy": r[0],
                "times_used": r[1],
                "times_worked": r[2],
                "success_rate": r[2] / r[1] if r[1] > 0 else 0,
                "avg_latency_ms": r[3],
            }
            for r in cur.fetchall()
        ]
        conn.close()
        return rows

    def suggest_strategy(self, task: str, already_tried: List[str]) -> str:
        """
        Pick the best next strategy based on past data.

        Priority:
        1. Strategies that worked before for this task (highest success rate)
        2. Strategies NOT yet tried
        3. Fallback to decompose_subtasks
        """
        stats = self.get_strategy_stats(task)

        # 1. Prefer strategies with proven success, not yet tried this run
        for s in stats:
            if s["strategy"] not in already_tried and s["success_rate"] > 0.3:
                return s["strategy"]

        # 2. Try any strategy not yet attempted
        for strategy in STRATEGY_POOL:
            if strategy not in already_tried:
                return strategy

        # 3. Absolute fallback
        return "decompose_subtasks"

    def get_failure_summary(self) -> Dict:
        """Overall stats for the dashboard."""
        conn = self._conn()
        cur = conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM failures").fetchone()[0]
        by_type = cur.execute(
            "SELECT error_type, COUNT(*) FROM failures GROUP BY error_type ORDER BY COUNT(*) DESC LIMIT 10"
        ).fetchall()
        fixed = cur.execute("SELECT COUNT(*) FROM failures WHERE fix_worked = 1").fetchone()[0]
        conn.close()
        return {
            "total_failures": total,
            "fixed": fixed,
            "fix_rate": fixed / total if total > 0 else 0,
            "top_error_types": [{"error_type": r[0], "count": r[1]} for r in by_type],
        }


# ===================================================================
# 2. TOOL DECISION LAYER - agents pick tools/strategies dynamically
# ===================================================================


class ToolDecisionLayer:
    """
    Instead of phases dictating tools, agents reason about WHICH tool to use.

    Each strategy maps to a concrete execution approach:
    - direct_execution:   Run the task as-is via Nova executor
    - simplify_and_retry: Strip task to minimal form, re-execute
    - decompose_subtasks: Break into smaller independent tasks
    - alternative_tool:   Swap tool (e.g., different LLM, different test runner)
    - rollback_and_patch: Undo last change, apply targeted patch
    - synthesize_tool:    Create the missing tool on-the-fly, then retry

    The layer also consults the knowledge graph (phase28) to check
    whether similar code has been modified before and what happened.
    """

    def __init__(self, failure_memory: FailureMemory):
        self.failure_memory = failure_memory
        self._graph = None
        self._learner = None
        self._synthesizer = None

    @property
    def synthesizer(self):
        if self._synthesizer is None:
            try:
                from src.tools.synthesized.synthesizer import ToolSynthesizer
                self._synthesizer = ToolSynthesizer()
            except Exception:
                pass
        return self._synthesizer

    @property
    def graph(self):
        if self._graph is None:
            try:
                from src.phase28_persistent_graph import PersistentRepositoryGraph
                self._graph = PersistentRepositoryGraph()
            except Exception:
                pass
        return self._graph

    @property
    def learner(self):
        if self._learner is None:
            try:
                from src.phase19_self_improving_agent import LearningDatabase
                self._learner = LearningDatabase()
            except Exception:
                pass
        return self._learner

    def choose_strategy(
        self,
        task: str,
        attempt: int,
        last_error: Optional[str],
        last_strategy: Optional[str],
        already_tried: List[str],
    ) -> Tuple[str, str]:
        """
        Returns (strategy_name, reasoning).

        Decision process:
        1. If attempt == 1: check failure memory for known issues
        2. If last_error contains known pattern: pick targeted fix
        3. Consult knowledge graph for impact radius
        4. Fall back to failure_memory.suggest_strategy()
        """
        reasoning_parts = []

        # --- First attempt: consult memory & graph ---
        if attempt == 1:
            past = self.failure_memory.get_past_failures(task, limit=5)
            if past:
                last_strat = past[0].get("strategy", "")
                last_fix = past[0].get("fix_applied", "")
                reasoning_parts.append(
                    f"Similar task failed before with strategy '{last_strat}'. "
                    f"Fix attempted: '{last_fix}'. Avoiding that strategy."
                )
                if last_strat and last_strat not in already_tried:
                    already_tried.append(last_strat)

            # Check graph for high-impact nodes
            if self.graph:
                try:
                    patterns = self.graph.find_similar_patterns(task[:200])
                    if patterns:
                        reasoning_parts.append(
                            f"Knowledge graph found {len(patterns)} similar patterns (best match: {patterns[0][1]:.0%})."
                        )
                except Exception:
                    pass

        # --- Missing-tool detection (takes priority) ---
        if last_error and self.synthesizer:
            spec = self.synthesizer.diagnose_missing_tool(
                last_error, task, {"attempt": attempt}
            )
            if spec and "synthesize_tool" not in already_tried:
                reasoning_parts.append(
                    f"Missing tool detected: '{spec['tool_name']}'. "
                    f"Will synthesize it before retrying."
                )
                return "synthesize_tool", " ".join(reasoning_parts)

        # --- Error-specific strategy selection ---
        if last_error:
            err_lower = last_error.lower()
            if "import" in err_lower or "module" in err_lower:
                # If we already tried synthesize_tool, fall through to alternative_tool
                strategy = "alternative_tool"
                reasoning_parts.append("Import/module error -- switching tool chain.")
                return strategy, " ".join(reasoning_parts)
            if "syntax" in err_lower or "parse" in err_lower:
                strategy = "rollback_and_patch"
                reasoning_parts.append("Syntax error -- rolling back and patching.")
                return strategy, " ".join(reasoning_parts)
            if "timeout" in err_lower or "timed out" in err_lower:
                strategy = "simplify_and_retry"
                reasoning_parts.append("Timeout -- simplifying task scope.")
                return strategy, " ".join(reasoning_parts)
            if "test" in err_lower or "assert" in err_lower:
                strategy = "rollback_and_patch"
                reasoning_parts.append("Test failure -- rolling back and patching.")
                return strategy, " ".join(reasoning_parts)

        # --- Default: ask failure memory for best strategy ---
        strategy = self.failure_memory.suggest_strategy(task, already_tried)
        reasoning_parts.append(f"Failure memory suggests '{strategy}'.")
        return strategy, " ".join(reasoning_parts)

    def diagnose_failure(self, task: str, error: str, execution_context: Dict) -> Dict:
        """
        Analyze WHY something failed. Returns structured diagnosis.

        Checks:
        1. Error classification (import, syntax, runtime, test, timeout)
        2. Past similar failures
        3. Knowledge graph: was the affected code recently changed?
        4. Learning DB: any known bad patterns?
        """
        error_lower = error.lower()

        # Classify error
        if "import" in error_lower or "no module" in error_lower:
            error_type = "import_error"
        elif "syntax" in error_lower:
            error_type = "syntax_error"
        elif "timeout" in error_lower or "timed out" in error_lower:
            error_type = "timeout"
        elif "test" in error_lower or "assert" in error_lower:
            error_type = "test_failure"
        elif "permission" in error_lower or "access" in error_lower:
            error_type = "permission_error"
        else:
            error_type = "runtime_error"

        # Check past failures with same error type
        similar = self.failure_memory.get_all_failures_by_error(error_type, limit=5)
        past_fixes = [f.get("fix_applied", "") for f in similar if f.get("fix_worked")]

        # Check graph for recent changes to affected area
        graph_context = {}
        if self.graph:
            try:
                affected = execution_context.get("affected_files", [])
                for fpath in affected[:3]:
                    node_id = hashlib.md5(fpath.encode()).hexdigest()[:12]
                    deps = self.graph.get_dependencies(node_id)
                    if deps:
                        graph_context[fpath] = {
                            "dependency_count": len(deps),
                            "dependencies": [d[0] for d in deps[:5]],
                        }
            except Exception:
                pass

        # Check learning DB for known bad patterns
        learned_warnings = []
        if self.learner:
            try:
                events = self.learner.get_events(limit=20)
                for ev in events:
                    if ev.get("outcome") == "failure" and ev.get("pattern_detected"):
                        learned_warnings.append(ev["pattern_detected"])
            except Exception:
                pass

        # Check if a tool can be synthesized
        synthesizable = False
        if error_type in ("import_error", "runtime_error"):
            try:
                from src.tools.synthesized.synthesizer import ToolSynthesizer
                synth = ToolSynthesizer()
                spec = synth.diagnose_missing_tool(error, task, {})
                if spec:
                    synthesizable = True
            except Exception:
                pass

        # Build suggested fix
        if synthesizable:
            suggested_fix = f"Missing tool detected — synthesize_tool strategy can create it"
        elif past_fixes:
            suggested_fix = f"Past fix that worked: {past_fixes[0]}"
        elif error_type == "import_error":
            suggested_fix = "Install missing dependency or fix import path"
        elif error_type == "syntax_error":
            suggested_fix = "Revert last change and regenerate with stricter validation"
        elif error_type == "test_failure":
            suggested_fix = "Analyze failing test, adjust implementation to match contract"
        elif error_type == "timeout":
            suggested_fix = "Reduce task scope or increase timeout"
        else:
            suggested_fix = "Decompose into smaller subtasks and retry incrementally"

        return {
            "error_type": error_type,
            "error_message": error[:500],
            "similar_past_failures": len(similar),
            "past_fixes_that_worked": past_fixes[:3],
            "graph_context": graph_context,
            "learned_warnings": learned_warnings[:5],
            "suggested_fix": suggested_fix,
        }


# ===================================================================
# 3. AUTONOMOUS LOOP ENGINE - the core try/fail/retry cycle
# ===================================================================


class AutonomousLoop:
    """
    Wraps any execution callable in a try -> diagnose -> fix -> retry loop.

    Usage:
        loop = AutonomousLoop()
        result = await loop.run("refactor auth module", execute_fn)

    Where execute_fn(task, strategy, context) -> Dict with "status" key.

    The loop:
    1. Asks FailureMemory: has this failed before?
    2. Asks ToolDecisionLayer: which strategy to use?
    3. Calls execute_fn with chosen strategy
    4. If failure: diagnoses why, records it, picks new strategy, retries
    5. After MAX_RETRIES: returns best partial result or final failure
    """

    def __init__(
        self,
        max_retries: int = MAX_RETRIES,
        failure_memory: Optional[FailureMemory] = None,
        tool_layer: Optional[ToolDecisionLayer] = None,
    ):
        self.max_retries = max_retries
        self.memory = failure_memory or FailureMemory()
        self.tools = tool_layer or ToolDecisionLayer(self.memory)

    async def run(
        self,
        task: str,
        execute_fn,
        initial_context: Optional[Dict] = None,
    ) -> LoopResult:
        """
        Execute task with autonomous retry loop.

        Args:
            task: Human-readable task description
            execute_fn: async callable(task, strategy, context) -> Dict
                        Must return {"status": "success"|"failed", ...}
            initial_context: Extra context passed to execute_fn

        Returns:
            LoopResult with full history
        """
        context = initial_context or {}
        failures: List[FailureRecord] = []
        strategies_used: List[str] = []
        start_time = datetime.utcnow()

        # Pre-flight: check failure memory for warnings
        past_failures = self.memory.get_past_failures(task, limit=5)
        if past_failures:
            logger.info(
                f"[AutonomousLoop] Found {len(past_failures)} past failures for similar task. "
                f"Last error: {past_failures[0].get('error_type', 'unknown')}"
            )
            context["past_failures"] = past_failures

        for attempt in range(1, self.max_retries + 1):
            # --- Pick strategy ---
            last_error = failures[-1].error_message if failures else None
            last_strategy = strategies_used[-1] if strategies_used else None
            strategy, reasoning = self.tools.choose_strategy(
                task, attempt, last_error, last_strategy, list(strategies_used)
            )
            strategies_used.append(strategy)

            logger.info(
                f"[AutonomousLoop] Attempt {attempt}/{self.max_retries} | "
                f"Strategy: {strategy} | Reason: {reasoning}"
            )

            # --- Synthesize tool if strategy says so ---
            if strategy == "synthesize_tool":
                synth_result = self._try_synthesize_tool(task, last_error, context)
                if synth_result and synth_result.get("success"):
                    context["synthesized_tool"] = synth_result["tool_name"]
                    logger.info(
                        f"[AutonomousLoop] Synthesized new tool: {synth_result['tool_name']} "
                        f"-> {synth_result['file_path']}"
                    )
                else:
                    logger.warning(
                        f"[AutonomousLoop] Tool synthesis failed: "
                        f"{synth_result.get('error', 'unknown') if synth_result else 'no spec'}"
                    )

            # --- Execute ---
            attempt_start = datetime.utcnow()
            try:
                result = await execute_fn(task, strategy, context)
            except Exception as exc:
                result = {"status": "failed", "error": str(exc)}

            elapsed_ms = int((datetime.utcnow() - attempt_start).total_seconds() * 1000)

            # --- Evaluate outcome ---
            status = result.get("status", "failed")

            if status == "success":
                # Record that this strategy worked
                self.memory.record_strategy_outcome(task, strategy, worked=True, latency_ms=elapsed_ms)

                # Cross-post to phase19 learning DB
                self._record_to_learning_db(task, strategy, True, reasoning)

                total_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                return LoopResult(
                    task=task,
                    status="success",
                    attempts=attempt,
                    total_duration_ms=total_ms,
                    final_output=result,
                    failure_history=failures,
                    strategy_evolution=strategies_used,
                )

            # --- Failure: diagnose ---
            error_str = result.get("error", "Unknown error")
            diagnosis = self.tools.diagnose_failure(task, error_str, {**context, **result})

            record = FailureRecord(
                attempt_number=attempt,
                timestamp=datetime.utcnow().isoformat(),
                error_type=diagnosis["error_type"],
                error_message=error_str[:1000],
                strategy_used=strategy,
                diagnosis=diagnosis["suggested_fix"],
                suggested_fix=diagnosis["suggested_fix"],
                context={"reasoning": reasoning, "elapsed_ms": elapsed_ms},
            )
            failures.append(record)

            # Persist to failure memory
            self.memory.record_failure(task, record)
            self.memory.record_strategy_outcome(task, strategy, worked=False, latency_ms=elapsed_ms)

            logger.warning(
                f"[AutonomousLoop] Attempt {attempt} FAILED | "
                f"Error: {diagnosis['error_type']} | "
                f"Diagnosis: {diagnosis['suggested_fix']}"
            )

            # Feed diagnosis back into context for next attempt
            context["last_diagnosis"] = diagnosis
            context["attempt"] = attempt
            context["failures_so_far"] = [f.to_dict() for f in failures]

            # Backoff between retries
            if attempt < self.max_retries:
                wait = BACKOFF_BASE_SECONDS ** attempt
                logger.info(f"[AutonomousLoop] Waiting {wait}s before retry...")
                await asyncio.sleep(wait)

        # --- All retries exhausted ---
        total_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Record to learning DB as failure
        self._record_to_learning_db(task, strategies_used[-1] if strategies_used else "none", False, "all retries exhausted")

        return LoopResult(
            task=task,
            status="failed",
            attempts=self.max_retries,
            total_duration_ms=total_ms,
            final_output={"error": "All retries exhausted", "last_diagnosis": failures[-1].to_dict() if failures else {}},
            failure_history=failures,
            strategy_evolution=strategies_used,
        )

    def _record_to_learning_db(self, task: str, strategy: str, success: bool, reasoning: str):
        """Cross-post outcome to phase19 learning database."""
        try:
            if self.tools.learner:
                from src.phase19_self_improving_agent import LearningEvent, OutcomeType, ChangeCategory
                event = LearningEvent(
                    event_id=f"loop_{hashlib.md5(f'{task}{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}",
                    timestamp=datetime.utcnow(),
                    file_path="autonomous_loop",
                    change_type=ChangeCategory.FEATURE,
                    description=f"Autonomous loop: {task[:200]}",
                    outcome=OutcomeType.SUCCESS if success else OutcomeType.FAILURE,
                    success_score=1.0 if success else 0.0,
                    pattern_detected=strategy,
                    decision_reasoning=reasoning[:500],
                )
                self.tools.learner.add_event(event)
        except Exception as e:
            logger.debug(f"Could not record to learning DB: {e}")

    def _try_synthesize_tool(
        self, task: str, last_error: Optional[str], context: Dict
    ) -> Optional[Dict]:
        """
        Attempt to synthesize a missing tool based on the last error.

        Returns the synthesizer result dict on success, or None.
        """
        if not last_error:
            return None
        try:
            from src.tools.synthesized.synthesizer import ToolSynthesizer
            synth = ToolSynthesizer()
            spec = synth.diagnose_missing_tool(last_error, task, context)
            if not spec:
                logger.debug("[AutonomousLoop] Synthesizer found no missing-tool pattern")
                return None

            result = synth.synthesize(spec)
            if result.get("success"):
                # Record to learning DB
                self._record_to_learning_db(
                    task,
                    "synthesize_tool",
                    True,
                    f"Created tool '{result['tool_name']}' to resolve: {last_error[:200]}",
                )
            return result
        except Exception as e:
            logger.warning(f"[AutonomousLoop] Tool synthesis error: {e}")
            return None


# ===================================================================
# Convenience: wrap the NovaCoordinator execution stage
# ===================================================================


async def execute_with_autonomous_loop(
    coordinator,
    task: str,
    requester: str = "system",
    consensus_type: str = "UNANIMOUS",
    max_retries: int = MAX_RETRIES,
) -> Dict:
    """
    Drop-in replacement for coordinator.execute_with_consensus() that wraps
    the execution stage in an autonomous retry loop.

    The planning, voting, and approval stages run once.
    Only the execution stage retries on failure with diagnosis.
    """
    loop = AutonomousLoop(max_retries=max_retries)

    async def _execute_with_strategy(task_text: str, strategy: str, context: Dict) -> Dict:
        """Adapter: calls coordinator's execution stage with strategy awareness."""
        # The strategy influences how we call the executor
        mission_id = f"auto_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        audit_trail = context.get("audit_trail", [])

        if strategy == "simplify_and_retry":
            # Strip task to core action
            task_text = task_text.split(".")[0] if "." in task_text else task_text

        if strategy == "decompose_subtasks":
            # Execute as a sequence of smaller steps
            # For now, just flag it for the executor
            pass

        try:
            result = await coordinator._run_execution_stage(
                task_text, mission_id, "nova_executor", audit_trail
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # --- Run the planning + voting stages once ---
    mission_id = f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(task)}"
    audit_trail = []

    logger.info(f"[Phase51] Starting autonomous execution: {task}")

    # Stage 1: Planning
    planning = await coordinator._run_planning_stage(task, mission_id, audit_trail)
    if planning.get("status") == "failed":
        return {"mission_id": mission_id, "status": "failed", "reason": "planning_failed", "planning": planning}

    # Stage 2: Voting
    voting = await coordinator._run_voting_stage(task, planning, mission_id, consensus_type, audit_trail)
    if voting.get("status") != "approved":
        return {"mission_id": mission_id, "status": "rejected", "reason": "consensus_not_reached", "voting": voting}

    # Stage 3: Autonomous execution loop (the new part)
    logger.info(f"[Phase51] Entering autonomous retry loop (max {max_retries} attempts)...")
    loop_result = await loop.run(
        task,
        _execute_with_strategy,
        initial_context={"audit_trail": audit_trail, "planning": planning, "voting": voting},
    )

    # --- Build final result ---
    result = {
        "mission_id": mission_id,
        "status": loop_result.status,
        "task": task,
        "requester": requester,
        "autonomous_loop": {
            "attempts": loop_result.attempts,
            "total_duration_ms": loop_result.total_duration_ms,
            "strategy_evolution": loop_result.strategy_evolution,
            "failure_count": len(loop_result.failure_history),
            "failures": [f.to_dict() for f in loop_result.failure_history],
        },
        "stages": {
            "planning": planning,
            "voting": voting,
            "execution": loop_result.final_output,
        },
        "audit_trail": audit_trail,
    }

    if loop_result.status == "success":
        logger.info(
            f"[Phase51] Mission succeeded after {loop_result.attempts} attempt(s) "
            f"({loop_result.total_duration_ms}ms)"
        )
    else:
        logger.error(
            f"[Phase51] Mission FAILED after {loop_result.attempts} attempts. "
            f"Strategies tried: {loop_result.strategy_evolution}"
        )

    return result
