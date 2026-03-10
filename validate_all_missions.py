#!/usr/bin/env python3
"""
Master Validation Script: Run All Three Real Tests

This script validates the Piddy autonomous developer system by running
three critical tests:

1. Dead Code Removal - cleanup_dead_code_autonomously mission
2. Refactor Safety - extract_service_autonomously mission  
3. Change-Based Test Selection - impact analysis

Usage:
    python validate_all_missions.py [--verbose]
"""

import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationRunner:
    """Runs all three validation tests"""
    
    def __init__(self):
        self.repo_root = Path("/workspaces/Piddy")
        self.results = {}
        self.timestamp = datetime.now()
    
    def run_test_file(self, test_file: str) -> Dict[str, Any]:
        """
        Run a test file directly as a Python script (for quick validation).
        Also try to run with pytest if available.
        
        Returns:
            Dict with run results
        """
        test_path = self.repo_root / "tests" / test_file
        logger.info(f"\n{'='*70}")
        logger.info(f"Running: {test_file}")
        logger.info(f"{'='*70}")
        
        result = {
            'test_file': test_file,
            'status': 'unknown',
            'output': '',
            'error': '',
            'returncode': -1
        }
        
        try:
            # Try running as Python script first (test harnesses have __main__)
            proc = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            result['returncode'] = proc.returncode
            result['output'] = proc.stdout
            result['error'] = proc.stderr
            result['status'] = 'success' if proc.returncode == 0 else 'failed'
            
            logger.info(f"Return code: {proc.returncode}")
            if proc.stdout:
                logger.info(f"Output:\n{proc.stdout}")
            if proc.stderr:
                logger.warning(f"Stderr:\n{proc.stderr}")
            
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['error'] = 'Test execution timed out after 120 seconds'
            logger.warning("Test timed out")
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Error running test: {e}")
        
        return result
    
    def extract_metrics_from_output(self, output: str, test_name: str) -> Dict:
        """Extract metrics from test output"""
        metrics = {}
        
        # Look for JSON report in output
        try:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'Report:' in line or '{' in line:
                    # Try to parse JSON
                    potential_json = '\n'.join(lines[i:])
                    # Find the first complete JSON object
                    for j, char in enumerate(potential_json):
                        if char == '{':
                            try:
                                json_str = potential_json[j:]
                                # Find matching closing brace
                                depth = 0
                                for k, c in enumerate(json_str):
                                    if c == '{':
                                        depth += 1
                                    elif c == '}':
                                        depth -= 1
                                        if depth == 0:
                                            metrics = json.loads(json_str[:k+1])
                                            return metrics
                            except (ValueError, TypeError, RuntimeError, HTTPError) as e:
                                pass
        except (ValueError, TypeError, RuntimeError, HTTPError) as e:
            pass
        
        return metrics
    
    def run_all_tests(self) -> Dict[str, Dict]:
        """Run all three validation tests"""
        
        tests = [
            'test_validation_dead_code_standalone.py',
            'test_validation_refactor_standalone.py',
            'test_validation_change_selection_standalone.py'
        ]
        
        for test in tests:
            result = self.run_test_file(test)
            metrics = self.extract_metrics_from_output(result['output'], test)
            result['metrics'] = metrics
            self.results[test] = result
        
        return self.results
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        
        report = {
            'timestamp': self.timestamp.isoformat(),
            'validation_run': 'PIDDY_AUTONOMOUS_SYSTEM_VALIDATION',
            'tests_run': len(self.results),
            'test_results': {},
            'overall_status': 'UNKNOWN',
            'critical_metrics': {},
            'recommendations': []
        }
        
        tests_passed = 0
        
        # Process each test result
        for test_name, result in self.results.items():
            report['test_results'][test_name] = {
                'status': result['status'],
                'returncode': result['returncode'],
                'metrics': result.get('metrics', {}),
            }
            
            if result['status'] == 'success':
                tests_passed += 1
            
            # Extract key metrics
            if result.get('metrics'):
                metrics = result['metrics']
                if 'pass_fail' in metrics:
                    report['test_results'][test_name]['outcome'] = metrics['pass_fail']
                if 'summary' in metrics:
                    report['test_results'][test_name]['summary'] = metrics['summary']
                if 'overall' in metrics:
                    report['test_results'][test_name]['overall'] = metrics['overall']
        
        # Determine overall status
        report['overall_status'] = 'PASS' if tests_passed == len(self.results) else 'PARTIAL'
        if tests_passed == 0:
            report['overall_status'] = 'FAIL'
        
        # Critical metrics
        report['critical_metrics'] = {
            'tests_executed': len(self.results),
            'tests_passed': tests_passed,
            'pass_rate': f"{tests_passed/len(self.results)*100:.1f}%" if self.results else "N/A",
            'system_readiness': 'PRODUCTION_READY' if tests_passed == len(self.results) else 'NEEDS_WORK'
        }
        
        # Recommendations
        if tests_passed < len(self.results):
            report['recommendations'].append(
                "Some validation tests failed. Review error logs and address issues."
            )
        else:
            report['recommendations'].append(
                "All validation tests passed. System ready for deployment."
            )
            report['recommendations'].append(
                "Next: Deploy Phase 33 planning loop to production."
            )
            report['recommendations'].append(
                "Monitor mission success rates and confidence calibration."
            )
        
        return report
    
    def save_report(self, report: Dict):
        """Save report to file"""
        report_path = self.repo_root / "VALIDATION_RESULTS.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nReport saved to {report_path}")
    
    def print_summary(self, report: Dict):
        """Print summary to console"""
        logger.info("\n" + "=" * 80)
        logger.info("PIDDY AUTONOMOUS SYSTEM VALIDATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"\nTimestamp: {report['timestamp']}")
        logger.info(f"Tests Run: {report['critical_metrics']['tests_executed']}")
        logger.info(f"Tests Passed: {report['critical_metrics']['tests_passed']}")
        logger.info(f"Pass Rate: {report['critical_metrics']['pass_rate']}")
        logger.info(f"System Readiness: {report['critical_metrics']['system_readiness']}")
        
        logger.info("\n" + "-" * 80)
        logger.info("TEST BREAKDOWN")
        logger.info("-" * 80)
        
        for test_name, result in report['test_results'].items():
            status = result.get('outcome', result['status']).upper()
            logger.info(f"\n{test_name}:")
            logger.info(f"  Status: {status}")
            if result.get('summary'):
                logger.info(f"  Summary: {result['summary']}")
            if result.get('overall'):
                logger.info(f"  Overall: {json.dumps(result['overall'], indent=4)}")
        
        logger.info("\n" + "-" * 80)
        logger.info("RECOMMENDATIONS")
        logger.info("-" * 80)
        for rec in report['recommendations']:
            logger.info(f"• {rec}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"OVERALL STATUS: {report['overall_status']}")
        logger.info("=" * 80)


def main():
    """Run validation"""
    runner = ValidationRunner()
    
    logger.info("\n" + "=" * 80)
    logger.info("STARTING PIDDY AUTONOMOUS SYSTEM VALIDATION")
    logger.info("=" * 80)
    logger.info(f"Timestamp: {runner.timestamp}")
    logger.info(f"Repository: {runner.repo_root}")
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        # Generate report
        report = runner.generate_summary_report()
        
        # Save and display
        runner.save_report(report)
        runner.print_summary(report)
        
        # Exit with appropriate code
        if report['overall_status'] == 'PASS':
            logger.info("\n✓ VALIDATION SUCCESSFUL - SYSTEM READY")
            return 0
        elif report['overall_status'] == 'PARTIAL':
            logger.info("\n⚠ VALIDATION PARTIAL - REVIEW FAILURES")
            return 1
        else:
            logger.info("\n✗ VALIDATION FAILED - SYSTEM NOT READY")
            return 1
    
    except Exception as e:
        logger.error(f"Validation runner failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
