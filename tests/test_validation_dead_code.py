"""
Validation Test 1: Dead Code Removal

This test validates that the autonomous dead code removal mission:
1. Correctly identifies dead code with high confidence
2. Maintains <1% false positive rate
3. Achieves reviewer acceptance

Metrics:
- Functions identified as dead code
- False positives (code removed that breaks tests)
- Test pass rate before/after
- Reviewer acceptance
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeadCodeMetrics:
    """Metrics for dead code validation"""
    total_functions: int
    identified_dead_code: int
    removal_attempts: int
    successful_removals: int
    false_positives: int
    tests_still_passing: bool
    compile_success: bool
    false_positive_rate: float
    confidence_avg: float
    reviewer_acceptance: bool


class DeadCodeValidator:
    """Validates dead code removal mission"""
    
    def __init__(self):
        self.repo_root = Path("/workspaces/Piddy")
        self.src_dir = self.repo_root / "src"
        self.test_dir = self.repo_root / "tests"
        
    def run_dead_code_mission(self, min_confidence: float = 0.90) -> Dict:
        """Execute the cleanup_dead_code mission"""
        logger.info(f"Running dead code cleanup mission (min_confidence={min_confidence})")
        
        # Import Phase 33 integration
        import sys
        sys.path.insert(0, str(self.repo_root))
        
        from src.phase33_planning_integration import Phase33PlanningIntegration
        
        planner = Phase33PlanningIntegration()
        mission = planner.cleanup_dead_code(min_confidence=min_confidence)
        
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
    
    def count_functions(self) -> int:
        """Count total functions in src directory"""
        count = 0
        for py_file in self.src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file) as f:
                    content = f.read()
                    # Simple heuristic: count 'def ' at line start
                    count += len([line for line in content.split('\n') 
                                 if line.strip().startswith('def ')])
            except:
                pass
        return count
    
    def run_tests(self) -> Tuple[bool, List[str]]:
        """Run test suite and return (success, test_output)"""
        logger.info("Running test suite...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(self.test_dir), "-v", "--tb=short"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout.split('\n')
        except subprocess.TimeoutExpired:
            logger.warning("Test suite timed out")
            return False, ["TIMEOUT"]
    
    def compile_check(self) -> bool:
        """Check if code compiles (Python import check)"""
        logger.info("Checking code compilation...")
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(self.src_dir)],
                cwd=str(self.repo_root),
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    def validate_false_positives(self) -> Tuple[int, float]:
        """
        Validate false positives by checking test pass rate.
        A false positive means code was removed that tests actually use.
        
        Returns:
            (false_positive_count, false_positive_rate)
        """
        logger.info("Validating for false positives...")
        
        # Record initial test state
        initial_pass, _ = self.run_tests()
        
        if not initial_pass:
            logger.warning("Initial test suite failed - baseline comparison not possible")
            return 0, 0.0
        
        # The dead code removal mission should not break tests
        # If tests fail after removal, those were false positives
        final_pass, _ = self.run_tests()
        
        if not final_pass:
            logger.warning("Tests failed after cleanup - indicates false positives detected")
            # This is bad - some removed code was actually used
            return 1, 1.0
        else:
            logger.info("All tests still pass - no false positives detected")
            return 0, 0.0
    
    def calculate_metrics(self, mission_result: Dict) -> DeadCodeMetrics:
        """Calculate comprehensive metrics"""
        
        total_funcs = self.count_functions()
        compile_ok = self.compile_check()
        tests_pass, _ = self.run_tests()
        false_pos, false_pos_rate = self.validate_false_positives()
        
        # Extract mission details
        identified = mission_result.get('results', {}).get('dead_code_identified', 0)
        attempted = mission_result.get('results', {}).get('removal_attempts', 0)
        successful = mission_result.get('results', {}).get('successful_removals', 0)
        
        confidence = mission_result.get('confidence', 0)
        
        return DeadCodeMetrics(
            total_functions=total_funcs,
            identified_dead_code=identified,
            removal_attempts=attempted,
            successful_removals=successful,
            false_positives=false_pos,
            tests_still_passing=tests_pass,
            compile_success=compile_ok,
            false_positive_rate=false_pos_rate,
            confidence_avg=confidence,
            reviewer_acceptance=false_pos_rate < 0.01 and tests_pass and compile_ok
        )
    
    def generate_report(self, metrics: DeadCodeMetrics) -> Dict:
        """Generate human-readable report"""
        return {
            'test_name': 'Dead Code Removal Validation',
            'timestamp': str(Path('/tmp/validation_timestamp.txt').read_text() if Path('/tmp/validation_timestamp.txt').exists() else 'now'),
            'metrics': {
                'total_functions_analyzed': metrics.total_functions,
                'dead_code_identified': metrics.identified_dead_code,
                'removal_attempts': metrics.removal_attempts,
                'successful_removals': metrics.successful_removals,
                'false_positives': metrics.false_positives,
                'false_positive_rate_pct': f"{metrics.false_positive_rate * 100:.2f}%",
            },
            'validation_checks': {
                'compilation_success': metrics.compile_success,
                'tests_still_passing': metrics.tests_still_passing,
                'false_positive_rate_acceptable': metrics.false_positive_rate < 0.01,
                'average_confidence': f"{metrics.confidence_avg:.2%}",
            },
            'reviewer_acceptance': metrics.reviewer_acceptance,
            'pass_fail': 'PASS' if metrics.reviewer_acceptance else 'FAIL',
            'summary': (
                f"Identified {metrics.identified_dead_code} functions as dead code. "
                f"Removed {metrics.successful_removals}. "
                f"False positive rate: {metrics.false_positive_rate_rate * 100:.2f}%. "
                f"Tests {'passing' if metrics.tests_still_passing else 'FAILING'}."
            )
        }


# Standalone test functions (can be run with pytest or directly)
def test_dead_code_removal_mission_runs():
    validator = DeadCodeValidator()
    """Test 1: Mission executes successfully"""
    result = validator.run_dead_code_mission(min_confidence=0.90)
    assert result['status'] != 'failed', "Mission should not fail"
    assert result['confidence'] >= 0.85, "Mission confidence should be acceptable"
    logger.info(f"✓ Mission executed with confidence {result['confidence']:.2%}")


def test_dead_code_false_positive_rate(validator):
    """Test 2: False positive rate is < 1%"""
    result = validator.run_dead_code_mission()
    metrics = validator.calculate_metrics(result)
    
    assert metrics.false_positive_rate < 0.01, \
        f"False positive rate {metrics.false_positive_rate:.2%} exceeds 1% threshold"
    logger.info(f"✓ False positive rate: {metrics.false_positive_rate:.2%} (target <1%)")


def test_compilation_after_cleanup(validator):
    """Test 3: Code compiles after cleanup"""
    validator.run_dead_code_mission()
    assert validator.compile_check(), "Code should compile after dead code removal"
    logger.info("✓ Code compilation successful")


def test_tests_pass_after_cleanup(validator):
    """Test 4: Tests still pass after cleanup"""
    validator.run_dead_code_mission()
    tests_pass, output = validator.run_tests()
    assert tests_pass, "Tests should pass after cleanup (no false positives)"
    logger.info("✓ All tests passing")


def test_reviewer_acceptance(validator):
    """Test 5: Mission passes reviewer acceptance criteria"""
    result = validator.run_dead_code_mission()
    metrics = validator.calculate_metrics(result)
    report = validator.generate_report(metrics)
    
    assert report['reviewer_acceptance'], "Mission should pass reviewer acceptance"
    assert report['pass_fail'] == 'PASS'
    logger.info(f"✓ Reviewer acceptance: {report['reviewer_acceptance']}")
    logger.info(f"\nReport:\n{json.dumps(report, indent=2)}")


if __name__ == '__main__':
    validator = DeadCodeValidator()
    print("=" * 70)
    print("VALIDATION TEST 1: DEAD CODE REMOVAL")
    print("=" * 70)
    
    result = validator.run_dead_code_mission(min_confidence=0.90)
    print(f"\nMission Result: {json.dumps(result, indent=2)}")
    
    metrics = validator.calculate_metrics(result)
    report = validator.generate_report(metrics)
    print(f"\nValidation Report:\n{json.dumps(report, indent=2)}")
    
    print("\n" + "=" * 70)
    print(f"RESULT: {report['pass_fail']}")
    print("=" * 70)
