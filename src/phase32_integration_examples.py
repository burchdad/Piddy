"""
Phase 32 Integration: Using Call Graphs in Agent Workflows

Example code showing how the agent uses Phase 32 for decision-making.
"""

from typing import Dict, Any, List, Tuple
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Import Phase 32 components
from phase32_call_graph_engine import (
    CallGraphDB, 
    ImpactAnalyzer,
    PythonCallGraphExtractor
)
from tools.call_graph_tools import (
    get_function_impact,
    check_breaking_change,
    find_safe_extraction_points,
    detect_circular_dependencies,
    estimate_refactoring_risk,
    suggest_safe_refactorings
)


class AgentRefactoringDecisionEngine:
    """
    Demonstrates how an agent uses call graphs to make safe refactoring decisions.
    
    This replaces manual, anxiety-driven code review with automated confidence scoring.
    """

    def __init__(self, call_graph_db_path: str, node_db_path: str):
        self.call_graph_db = CallGraphDB(call_graph_db_path)
        self.node_db = sqlite3.connect(node_db_path)
        self.analyzer = ImpactAnalyzer(self.call_graph_db)

    def should_delete_function(self, func_id: str) -> Tuple[bool, str]:
        """
        Decide if it's safe to delete a function.
        
        BEFORE Phase 32:
            Agent: "I found this unused function, but I can't guarantee nothing calls it
                   hidden in the codebase. Need human review."
            Human: "OK, let me search grep for it... [30 mins]... 
                   yes it's safe to delete."
        
        AFTER Phase 32:
            Agent: "Function has zero callers in call graph. 100% confident deletion is safe."
            Human: Just gets notified about the automated deletion.
        """
        safe, message = self.analyzer.is_safe_to_delete(func_id)
        
        if safe:
            return True, f"✅ SAFE: {message}"
        else:
            return False, f"❌ UNSAFE: {message}"

    def should_add_parameter(
        self, 
        func_id: str, 
        new_param: Dict[str, str]
    ) -> Tuple[bool, str, int]:
        """
        Decide if adding a parameter is safe (backward compatible).
        
        Returns (is_safe, reason, callers_affected)
        """
        callers = self.call_graph_db.get_callers(func_id)
        
        # Adding optional parameters = backward compatible
        # Adding required parameters = breaking change
        
        if new_param.get("required", True):
            return False, (
                f"❌ Required parameter breaks {len(callers)} callers. "
                f"Use optional parameter or update all callers."
            ), len(callers)
        else:
            return True, (
                f"✅ Optional parameter backward compatible. "
                f"Safe to add ({len(callers)} callers unaffected)."
            ), len(callers)

    def should_extract_function(
        self,
        source_func_id: str,
        lines: List[int],
        new_func_name: str
    ) -> Tuple[bool, str, List[str]]:
        """
        Decide if code extraction is safe.
        
        BEFORE: "Extracting feels risky, might break something subtle"
        AFTER: "Extraction is isolated to 1 function, safe to do"
        """
        result = find_safe_extraction_points(
            source_func_id,
            lines,
            self.call_graph_db.db_path
        )
        
        if result.get("can_extract"):
            return True, f"✅ SAFE: Can extract lines {lines[0]}-{lines[-1]}", [new_func_name]
        else:
            return False, (
                f"❌ RISKY: {result.get('recommendation', 'Complex interdependencies')}"
            ), []

    def should_refactor_signature(
        self,
        func_id: str,
        changes: Dict[str, Any]
    ) -> Tuple[bool, str, float]:
        """
        Decide if signature change is safe.
        
        Confidence scale: 0.0 (very risky) to 1.0 (completely safe)
        """
        risk = estimate_refactoring_risk(
            [{"type": "parameter_change", "function": func_id}],
            self.call_graph_db.db_path
        )
        
        confidence = 1.0 - risk["risk_score"]
        
        if confidence > 0.9:
            return True, f"✅ SAFE: {risk['recommendation']}", confidence
        elif confidence > 0.7:
            return True, f"⚠️ MEDIUM RISK: {risk['recommendation']}", confidence
        else:
            return False, f"❌ HIGH RISK: {risk['recommendation']}", confidence

    def propose_safe_refactorings(self, func_id: str) -> List[Dict[str, Any]]:
        """
        Suggest refactorings the agent can confidently do.
        """
        suggestions = suggest_safe_refactorings(func_id, self.call_graph_db.db_path)
        
        return [s for s in suggestions if s.get("confidence", 0) > 0.8]

    def find_critical_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find architectural issues to fix.
        """
        issues = {
            "circular_dependencies": detect_circular_dependencies(self.call_graph_db.db_path),
            "dead_code": []  # Would populate from analyzer
        }
        
        return issues


class AgentDecisionExample:
    """
    Concrete example of agent decision-making with Phase 32.
    Shows before/after scenarios.
    """

    @staticmethod
    def example_1_delete_unused_function():
        """
        User: "Delete function `old_validate_email()` - we're using a new one"
        """
        logger.info("\n=== EXAMPLE 1: Delete Unused Function ===\n")
        
        logger.info("BEFORE Phase 32:")
        logger.info("  Agent: 'I found this function but can't guarantee it's unused.'")
        logger.info("  Human: 25 minutes of manual code review")
        logger.info("  Result: Anxiety, slow feedback loop\n")
        
        logger.info("AFTER Phase 32:")
        logger.info("  Agent: Checking call graph...")
        logger.info("  Agent: 'Function has 0 callers. 100% confident to delete.'")
        logger.info("  Result: Instant automation, high confidence\n")

    @staticmethod
    def example_2_safely_add_logging():
        """
        User: "Add logger parameter to authenticate() function"
        """
        logger.info("\n=== EXAMPLE 2: Add Logger Parameter ===\n")
        
        logger.info("BEFORE Phase 32:")
        logger.info("  Agent: 'I'll add logger parameter...'")
        logger.info("  [Creates PR, 5 tests fail across codebase]")
        logger.info("  Human: 'Wait, you broke authentication in 3 places!'\n")
        
        logger.info("AFTER Phase 32:")
        logger.info("  Agent: 'Making optional parameter - backward compatible'")
        logger.info("  Agent: 'No breaking changes. All callers work unchanged.'")
        logger.info("  Result: All tests pass, zero breaking changes\n")

    @staticmethod
    def example_3_refactor_with_confidence():
        """
        Refactoring: Split large function into helpers
        """
        logger.info("\n=== EXAMPLE 3: Refactor With High Confidence ===\n")
        
        logger.info("User: 'This function is too long (200 lines). Can we split it?'\n")
        
        logger.info("Agent Analysis:")
        logger.info("  ✓ Function called by 3 places (all tested)")
        logger.info("  ✓ Can extract 50-line helper safely")
        logger.info("  ✓ Helper impact: 0 additional functions affected")
        logger.info("  ✓ Risk level: LOW")
        logger.info("  ✓ Test coverage: 92% on all callers\n")
        
        logger.info("Result:")
        logger.info("  Agent: 'Proceeding with refactoring...'")
        logger.info("  [Automatically extracts function]")
        logger.info("  [Runs tests - all pass]")
        logger.info("  [Updates 3 call sites]")
        logger.info("  PR ready in 2 minutes, 99% confidence\n")


class LiveDecisionScene:
    """
    Demonstrates live decision-making in agent workflow.
    """

    @staticmethod
    def authenticate_changes_request():
        """
        Live scenario: Agent receives request to change core authentication module
        """
        logger.info("\n" + "="*70)
        logger.info("LIVE SCENARIO: Autonomous Refactoring Decision")
        logger.info("="*70 + "\n")

        # Agent receives request
        user_request = """
        Refactor authenticate_user() to use dependency injection for the database.
        Current signature: authenticate_user(username, password) -> bool
        New signature: authenticate_user(username, password, db: Database) -> bool
        """

        logger.info("📝 USER REQUEST:")
        logger.info(user_request)

        # Phase 32 Analysis (automatic)
        logger.info("\n🔍 PHASE 32 ANALYSIS:")
        logger.info("-" * 70)

        analysis = {
            "function": "authenticate_user",
            "change_type": "signature_modification",
            "new_parameter": {"name": "db", "type": "Database", "required": True},
            "direct_callers": 12,
            "indirect_callers": 34,
            "risk_level": "HIGH",
            "test_coverage": "88%",
            "affected_services": ["auth_service", "api_gateway", "mobile_backend"],
            "breaking": True
        }

        logger.info(f"  • Direct callers: {analysis['direct_callers']}")
        logger.info(f"  • Indirect callers: {analysis['indirect_callers']}")
        logger.info(f"  • Risk level: {analysis['risk_level']}")
        logger.info(f"  • Affected services: {len(analysis['affected_services'])}")
        logger.info(f"  • Breaking change: {analysis['breaking']}")

        # Agent decision
        logger.info("\n🤖 AGENT DECISION:")
        logger.info("-" * 70)
        
        if analysis["breaking"] and analysis["direct_callers"] > 10:
            decision = "CANNOT EXECUTE - high risk breaking change"
            logger.info(f"  Status: ❌ {decision}")
            logger.info(f"\n  Reasoning:")
            logger.info(f"    - Adding REQUIRED parameter breaks {analysis['direct_callers']} callers")
            logger.info(f"    - Changes would ripple through {analysis['indirect_callers']} functions")
            logger.info(f"    - Affects {len(analysis['affected_services'])} critical services")
            logger.info(f"\n  Suggestions:")
            logger.info(f"    1. Make parameter optional (backward compatible)")
            logger.info(f"    2. Use dependency injection at initialization")
            logger.info(f"    3. Create new function with new signature")
            logger.info(f"    4. Deprecate old function gradually")
        else:
            decision = "SAFE TO EXECUTE"
            logger.info(f"  Status: ✅ {decision}")

        # Human approval flow
        logger.info("\n👤 HUMAN APPROVAL:")
        logger.info("-" * 70)
        logger.info("  1. Agent presents analysis to human")
        logger.info("  2. Human reviews suggestions")
        logger.info("  3. Human chooses approach")
        logger.info("  4. Agent executes with chosen approach")
        logger.info("\n  Result: HIGH CONFIDENCE, LOW RISK\n")


def integration_example_full_workflow():
    """
    Complete workflow example using Phase 32.
    """
    logger.info("\n" + "="*70)
    logger.info("FULL WORKFLOW EXAMPLE: Building Call Graph & Making Decisions")
    logger.info("="*70 + "\n")

    logger.info("Step 1: Initialize Call Graph")
    logger.info("-" * 70)
    logger.info("  # Build call graph from repository")
    logger.info("  builder = CallGraphBuilder(call_db, node_db)")
    logger.info("  stats = builder.build_from_directory('/path/to/repo')")
    logger.info(f"    ✓ Processed 234 Python files")
    logger.info(f"    ✓ Found 1,847 functions")
    logger.info(f"    ✓ Extracted 5,234 call relationships")
    logger.info(f"    ✓ Detected 3 circular dependencies\n")

    logger.info("Step 2: Analyze Architecture")
    logger.info("-" * 70)
    logger.info("  # Get architecture health metrics")
    logger.info("  cycles = analyzer.find_cycles()")
    logger.info("  dead_code = analyzer.find_dead_code()")
    logger.info(f"    ✓ Circular dependencies: 3 (medium priority)")
    logger.info(f"    ✓ Dead code functions: 12 (deletable)")
    logger.info(f"    ✓ Hotspots: 8 functions called >20 times")
    logger.info(f"    ✓ Architecture health: 78/100 (B+)\n")

    logger.info("Step 3: Make Safe Refactoring Decision")
    logger.info("-" * 70)
    logger.info("  # Agent decides on code change")
    logger.info("  safe, reason = engine.should_delete_function('func_id_xyz')")
    logger.info("    → Result: True, 'Safe: No callers found'")
    logger.info("    → Confidence: 99%")
    logger.info("    → Action: Proceed with deletion\n")

    logger.info("Step 4: Execute With High Confidence")
    logger.info("-" * 70)
    logger.info("  # Agent executes change")
    logger.info("  agent.delete_function('func_id_xyz')")
    logger.info("  agent.run_tests()")
    logger.info("  agent.commit_and_push()")
    logger.info("    ✓ Function deleted")
    logger.info("    ✓ All tests pass")
    logger.info("    ✓ Change pushed to main branch")
    logger.info("    ✓ 0 post-merge fixes needed\n")

    logger.info("RESULT: Autonomous, confident, safe refactoring")
    logger.info("        What took 30+ minutes is now 5 minutes\n")


if __name__ == "__main__":
    # Runexample scenarios
    AgentDecisionExample.example_1_delete_unused_function()
    AgentDecisionExample.example_2_safely_add_logging()
    AgentDecisionExample.example_3_refactor_with_confidence()
    
    LiveDecisionScene.authenticate_changes_request()
    
    integration_example_full_workflow()
