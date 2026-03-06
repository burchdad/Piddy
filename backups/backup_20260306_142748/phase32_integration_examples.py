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
        print("\n=== EXAMPLE 1: Delete Unused Function ===\n")
        
        print("BEFORE Phase 32:")
        print("  Agent: 'I found this function but can't guarantee it's unused.'")
        print("  Human: 25 minutes of manual code review")
        print("  Result: Anxiety, slow feedback loop\n")
        
        print("AFTER Phase 32:")
        print("  Agent: Checking call graph...")
        print("  Agent: 'Function has 0 callers. 100% confident to delete.'")
        print("  Result: Instant automation, high confidence\n")

    @staticmethod
    def example_2_safely_add_logging():
        """
        User: "Add logger parameter to authenticate() function"
        """
        print("\n=== EXAMPLE 2: Add Logger Parameter ===\n")
        
        print("BEFORE Phase 32:")
        print("  Agent: 'I'll add logger parameter...'")
        print("  [Creates PR, 5 tests fail across codebase]")
        print("  Human: 'Wait, you broke authentication in 3 places!'\n")
        
        print("AFTER Phase 32:")
        print("  Agent: 'Making optional parameter - backward compatible'")
        print("  Agent: 'No breaking changes. All callers work unchanged.'")
        print("  Result: All tests pass, zero breaking changes\n")

    @staticmethod
    def example_3_refactor_with_confidence():
        """
        Refactoring: Split large function into helpers
        """
        print("\n=== EXAMPLE 3: Refactor With High Confidence ===\n")
        
        print("User: 'This function is too long (200 lines). Can we split it?'\n")
        
        print("Agent Analysis:")
        print("  ✓ Function called by 3 places (all tested)")
        print("  ✓ Can extract 50-line helper safely")
        print("  ✓ Helper impact: 0 additional functions affected")
        print("  ✓ Risk level: LOW")
        print("  ✓ Test coverage: 92% on all callers\n")
        
        print("Result:")
        print("  Agent: 'Proceeding with refactoring...'")
        print("  [Automatically extracts function]")
        print("  [Runs tests - all pass]")
        print("  [Updates 3 call sites]")
        print("  PR ready in 2 minutes, 99% confidence\n")


class LiveDecisionScene:
    """
    Demonstrates live decision-making in agent workflow.
    """

    @staticmethod
    def authenticate_changes_request():
        """
        Live scenario: Agent receives request to change core authentication module
        """
        print("\n" + "="*70)
        print("LIVE SCENARIO: Autonomous Refactoring Decision")
        print("="*70 + "\n")

        # Agent receives request
        user_request = """
        Refactor authenticate_user() to use dependency injection for the database.
        Current signature: authenticate_user(username, password) -> bool
        New signature: authenticate_user(username, password, db: Database) -> bool
        """

        print("📝 USER REQUEST:")
        print(user_request)

        # Phase 32 Analysis (automatic)
        print("\n🔍 PHASE 32 ANALYSIS:")
        print("-" * 70)

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

        print(f"  • Direct callers: {analysis['direct_callers']}")
        print(f"  • Indirect callers: {analysis['indirect_callers']}")
        print(f"  • Risk level: {analysis['risk_level']}")
        print(f"  • Affected services: {len(analysis['affected_services'])}")
        print(f"  • Breaking change: {analysis['breaking']}")

        # Agent decision
        print("\n🤖 AGENT DECISION:")
        print("-" * 70)
        
        if analysis["breaking"] and analysis["direct_callers"] > 10:
            decision = "CANNOT EXECUTE - high risk breaking change"
            print(f"  Status: ❌ {decision}")
            print(f"\n  Reasoning:")
            print(f"    - Adding REQUIRED parameter breaks {analysis['direct_callers']} callers")
            print(f"    - Changes would ripple through {analysis['indirect_callers']} functions")
            print(f"    - Affects {len(analysis['affected_services'])} critical services")
            print(f"\n  Suggestions:")
            print(f"    1. Make parameter optional (backward compatible)")
            print(f"    2. Use dependency injection at initialization")
            print(f"    3. Create new function with new signature")
            print(f"    4. Deprecate old function gradually")
        else:
            decision = "SAFE TO EXECUTE"
            print(f"  Status: ✅ {decision}")

        # Human approval flow
        print("\n👤 HUMAN APPROVAL:")
        print("-" * 70)
        print("  1. Agent presents analysis to human")
        print("  2. Human reviews suggestions")
        print("  3. Human chooses approach")
        print("  4. Agent executes with chosen approach")
        print("\n  Result: HIGH CONFIDENCE, LOW RISK\n")


def integration_example_full_workflow():
    """
    Complete workflow example using Phase 32.
    """
    print("\n" + "="*70)
    print("FULL WORKFLOW EXAMPLE: Building Call Graph & Making Decisions")
    print("="*70 + "\n")

    print("Step 1: Initialize Call Graph")
    print("-" * 70)
    print("  # Build call graph from repository")
    print("  builder = CallGraphBuilder(call_db, node_db)")
    print("  stats = builder.build_from_directory('/path/to/repo')")
    print(f"    ✓ Processed 234 Python files")
    print(f"    ✓ Found 1,847 functions")
    print(f"    ✓ Extracted 5,234 call relationships")
    print(f"    ✓ Detected 3 circular dependencies\n")

    print("Step 2: Analyze Architecture")
    print("-" * 70)
    print("  # Get architecture health metrics")
    print("  cycles = analyzer.find_cycles()")
    print("  dead_code = analyzer.find_dead_code()")
    print(f"    ✓ Circular dependencies: 3 (medium priority)")
    print(f"    ✓ Dead code functions: 12 (deletable)")
    print(f"    ✓ Hotspots: 8 functions called >20 times")
    print(f"    ✓ Architecture health: 78/100 (B+)\n")

    print("Step 3: Make Safe Refactoring Decision")
    print("-" * 70)
    print("  # Agent decides on code change")
    print("  safe, reason = engine.should_delete_function('func_id_xyz')")
    print("    → Result: True, 'Safe: No callers found'")
    print("    → Confidence: 99%")
    print("    → Action: Proceed with deletion\n")

    print("Step 4: Execute With High Confidence")
    print("-" * 70)
    print("  # Agent executes change")
    print("  agent.delete_function('func_id_xyz')")
    print("  agent.run_tests()")
    print("  agent.commit_and_push()")
    print("    ✓ Function deleted")
    print("    ✓ All tests pass")
    print("    ✓ Change pushed to main branch")
    print("    ✓ 0 post-merge fixes needed\n")

    print("RESULT: Autonomous, confident, safe refactoring")
    print("        What took 30+ minutes is now 5 minutes\n")


if __name__ == "__main__":
    # Runexample scenarios
    AgentDecisionExample.example_1_delete_unused_function()
    AgentDecisionExample.example_2_safely_add_logging()
    AgentDecisionExample.example_3_refactor_with_confidence()
    
    LiveDecisionScene.authenticate_changes_request()
    
    integration_example_full_workflow()
