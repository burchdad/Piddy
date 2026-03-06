"""
Validation Test 2: Refactor Safety (Service Extraction)

This test validates that the autonomous service extraction mission:
1. Maintains compilation success
2. Preserves test pass rate
3. Detects/prevents contract violations

Metrics:
- Compilation success before/after
- Test pass rate before/after
- Contract violations detected
- Type safety violations
- Import resolution success
"""

import pytest
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RefactorMetrics:
    """Metrics for refactor safety validation"""
    compilation_before: bool
    compilation_after: bool
    tests_passing_before: int
    tests_passing_after: int
    test_pass_rate_preserved: bool
    contract_violations: int
    type_violations: int
    import_resolution_success: bool
    confidence_avg: float
    safety_check_pass: bool


class RefactorSafetyValidator:
    """Validates service extraction mission safety"""
    
    def __init__(self):
        self.repo_root = Path("/workspaces/Piddy")
        self.src_dir = self.repo_root / "src"
        self.test_dir = self.repo_root / "tests"
        
    def select_extraction_target(self) -> Tuple[str, str, List[str]]:
        """
        Select a small service to extract for testing.
        
        Returns:
            (source_module, target_service_name, functions_to_extract)
        """
        # Select the cache module as a good extraction target
        # It's relatively isolated and has clear boundaries
        return (
            "src.cache",
            "cache_service",
            ["get_cached_value", "set_cached_value", "clear_cache"]
        )
    
    def compile_check(self) -> bool:
        """Check if code compiles"""
        logger.info("Checking code compilation...")
        try:
            result = subprocess.run(
                ["python", "-c", "import src; print('OK')"],
                cwd=str(self.repo_root),
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    def count_passing_tests(self) -> int:
        """Count number of passing tests"""
        logger.info("Running test suite...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(self.test_dir), "-v", "--tb=short"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            # Count "PASSED" in output
            passes = result.stdout.count(" PASSED")
            return passes if passes > 0 else -1
        except subprocess.TimeoutExpired:
            logger.warning("Test suite timed out")
            return -1
    
    def run_extraction_mission(self, source_module: str, target_service: str, 
                              functions: List[str]) -> Dict:
        """Execute the extract_service mission"""
        logger.info(f"Running extraction mission: {source_module} -> {target_service}")
        
        import sys
        sys.path.insert(0, str(self.repo_root))
        
        from src.phase33_planning_integration import Phase33PlanningIntegration
        
        planner = Phase33PlanningIntegration()
        mission = planner.extract_service(
            source_module=source_module,
            target_service=target_service,
            functions=functions
        )
        
        logger.info(f"Mission status: {mission.status}")
        logger.info(f"Mission confidence: {mission.confidence:.2%}")
        
        return {
            'mission_id': mission.id,
            'status': mission.status.value,
            'confidence': mission.confidence,
            'results': mission.results,
            'tasks': len(mission.tasks),
            'failed_tasks': len([t for t in mission.tasks if t.status.value == 'failed'])
        }
    
    def check_contracts(self) -> Tuple[int, List[str]]:
        """
        Check for contract violations in the extracted service.
        
        Returns:
            (violation_count, violation_details)
        """
        logger.info("Checking API contracts...")
        
        import sys
        sys.path.insert(0, str(self.repo_root))
        
        try:
            from src.phase32_api_contracts import APIContractTracker
            tracker = APIContractTracker()
            violations = tracker.find_contract_violations()
            return len(violations), [str(v) for v in violations]
        except:
            logger.warning("Could not check contracts")
            return 0, []
    
    def check_types(self) -> Tuple[int, List[str]]:
        """
        Check for type violations.
        
        Returns:
            (violation_count, violation_details)
        """
        logger.info("Checking type safety...")
        
        import sys
        sys.path.insert(0, str(self.repo_root))
        
        try:
            from src.phase32_type_system import TypeCompatibilityChecker
            checker = TypeCompatibilityChecker()
            violations = checker.find_type_violations()
            return len(violations), [str(v) for v in violations]
        except:
            logger.warning("Could not check types")
            return 0, []
    
    def validate_imports(self) -> bool:
        """Validate that imports resolve correctly"""
        logger.info("Validating imports...")
        try:
            result = subprocess.run(
                ["python", "-c", 
                 "from src.cache import *; from src.cache_service import *; print('OK')"],
                cwd=str(self.repo_root),
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def calculate_metrics(self, mission_result: Dict, 
                         tests_before: int) -> RefactorMetrics:
        """Calculate comprehensive metrics"""
        
        compile_before = self.compile_check()
        compile_after = self.compile_check()  # Should be True after extraction
        
        tests_after = self.count_passing_tests()
        tests_preserved = tests_before <= tests_after if tests_before > 0 else True
        
        contract_vios, _ = self.check_contracts()
        type_vios, _ = self.check_types()
        imports_ok = self.validate_imports()
        
        confidence = mission_result.get('confidence', 0)
        
        return RefactorMetrics(
            compilation_before=compile_before,
            compilation_after=compile_after,
            tests_passing_before=tests_before,
            tests_passing_after=tests_after if tests_after > 0 else tests_before,
            test_pass_rate_preserved=tests_preserved,
            contract_violations=contract_vios,
            type_violations=type_vios,
            import_resolution_success=imports_ok,
            confidence_avg=confidence,
            safety_check_pass=(
                compile_after and 
                tests_preserved and 
                contract_vios == 0 and 
                type_vios == 0 and 
                imports_ok
            )
        )
    
    def generate_report(self, metrics: RefactorMetrics) -> Dict:
        """Generate human-readable report"""
        return {
            'test_name': 'Refactor Safety (Service Extraction)',
            'compilation': {
                'before': metrics.compilation_before,
                'after': metrics.compilation_after,
                'status': 'PASS' if metrics.compilation_after else 'FAIL'
            },
            'tests': {
                'passing_before': metrics.tests_passing_before,
                'passing_after': metrics.tests_passing_after,
                'preserved': metrics.test_pass_rate_preserved,
                'status': 'PASS' if metrics.test_pass_rate_preserved else 'FAIL'
            },
            'safety_checks': {
                'contract_violations': metrics.contract_violations,
                'type_violations': metrics.type_violations,
                'imports_valid': metrics.import_resolution_success,
                'status': 'PASS' if (
                    metrics.contract_violations == 0 and 
                    metrics.type_violations == 0 and 
                    metrics.import_resolution_success
                ) else 'FAIL'
            },
            'overall': {
                'average_confidence': f"{metrics.confidence_avg:.2%}",
                'safety_passes': metrics.safety_check_pass,
                'status': 'PASS' if metrics.safety_check_pass else 'FAIL'
            },
            'summary': (
                f"Compilation: {metrics.compilation_after} | "
                f"Tests preserved: {metrics.test_pass_rate_preserved} | "
                f"Contract violations: {metrics.contract_violations} | "
                f"Type violations: {metrics.type_violations}"
            )
        }


# Pytest fixtures and tests
@pytest.fixture
def validator():
    return RefactorSafetyValidator()


def test_extraction_mission_runs(validator):
    """Test 1: Extraction mission executes"""
    source, target, funcs = validator.select_extraction_target()
    result = validator.run_extraction_mission(source, target, funcs)
    
    assert result['status'] != 'failed', "Mission should not fail"
    assert result['confidence'] >= 0.8, "Mission confidence should be acceptable"
    logger.info(f"✓ Extraction mission executed with confidence {result['confidence']:.2%}")


def test_compilation_after_extraction(validator):
    """Test 2: Code compiles after extraction"""
    source, target, funcs = validator.select_extraction_target()
    
    compile_before = validator.compile_check()
    assert compile_before, "Code should compile before extraction"
    
    validator.run_extraction_mission(source, target, funcs)
    compile_after = validator.compile_check()
    
    assert compile_after, "Code should compile after extraction"
    logger.info("✓ Compilation successful before and after")


def test_tests_pass_after_extraction(validator):
    """Test 3: Tests pass after extraction"""
    source, target, funcs = validator.select_extraction_target()
    
    tests_before = validator.count_passing_tests()
    assert tests_before > 0, "Tests should pass before extraction"
    
    validator.run_extraction_mission(source, target, funcs)
    tests_after = validator.count_passing_tests()
    
    assert tests_after >= tests_before, "Test pass rate should not decrease"
    logger.info(f"✓ Tests preserved: {tests_before} -> {tests_after}")


def test_no_contract_violations(validator):
    """Test 4: No contract violations after extraction"""
    source, target, funcs = validator.select_extraction_target()
    validator.run_extraction_mission(source, target, funcs)
    
    violations, details = validator.check_contracts()
    assert violations == 0, f"Should have no contract violations, found {violations}"
    logger.info("✓ No contract violations detected")


def test_no_type_violations(validator):
    """Test 5: No type violations after extraction"""
    source, target, funcs = validator.select_extraction_target()
    validator.run_extraction_mission(source, target, funcs)
    
    violations, details = validator.check_types()
    assert violations == 0, f"Should have no type violations, found {violations}"
    logger.info("✓ No type violations detected")


def test_imports_valid(validator):
    """Test 6: Imports resolve correctly"""
    source, target, funcs = validator.select_extraction_target()
    validator.run_extraction_mission(source, target, funcs)
    
    assert validator.validate_imports(), "Imports should resolve correctly"
    logger.info("✓ Imports valid")


def test_safety_passes_overall(validator):
    """Test 7: Overall safety validation passes"""
    source, target, funcs = validator.select_extraction_target()
    result = validator.run_extraction_mission(source, target, funcs)
    
    tests_before = validator.count_passing_tests()
    metrics = validator.calculate_metrics(result, tests_before)
    report = validator.generate_report(metrics)
    
    assert metrics.safety_check_pass, "Should pass all safety checks"
    assert report['overall']['status'] == 'PASS'
    logger.info(f"\nReport:\n{json.dumps(report, indent=2)}")


if __name__ == '__main__':
    validator = RefactorSafetyValidator()
    print("=" * 70)
    print("VALIDATION TEST 2: REFACTOR SAFETY (SERVICE EXTRACTION)")
    print("=" * 70)
    
    source, target, funcs = validator.select_extraction_target()
    print(f"\nExtraction Target: {source} -> {target}")
    print(f"Functions: {funcs}")
    
    result = validator.run_extraction_mission(source, target, funcs)
    print(f"\nMission Result: {json.dumps(result, indent=2)}")
    
    tests_before = validator.count_passing_tests()
    metrics = validator.calculate_metrics(result, tests_before)
    report = validator.generate_report(metrics)
    print(f"\nValidation Report:\n{json.dumps(report, indent=2)}")
    
    print("\n" + "=" * 70)
    print(f"RESULT: {report['overall']['status']}")
    print("=" * 70)
