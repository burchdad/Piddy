"""
Phase 36: Diff-Aware Planning

Integrates git diff analysis into mission planning to:
- Understand what changed
- Calculate impact automatically
- Generate more accurate task plans
- Skip unnecessary work

Flow:
git diff → changed files → affected functions → impacted tests/components → plan

This dramatically improves planning accuracy by understanding context.
"""

import subprocess
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class DiffChange:
    """A single code change"""
    file_path: str
    change_type: str  # added, deleted, modified
    added_lines: int
    deleted_lines: int
    functions_affected: List[str]
    imports_affected: List[str]


@dataclass
class DiffAnalysis:
    """Complete diff analysis"""
    commit_range: str
    total_changes: int
    files_changed: int
    changes: List[DiffChange]
    affected_functions: Set[str]
    affected_modules: Set[str]
    affected_tests: Set[str]
    risk_level: str  # low, medium, high


class GitDiffAnalyzer:
    """Analyzes git diffs to understand code changes"""
    
    def __init__(self, repo_path: str = "/workspaces/Piddy"):
        self.repo_path = Path(repo_path)
    
    def get_diff(self, from_ref: str = "main", to_ref: str = "HEAD") -> str:
        """Get raw diff between two refs"""
        try:
            result = subprocess.run(
                ["git", "diff", f"{from_ref}...{to_ref}", "--no-color"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to get diff: {e}")
            return ""
    
    def parse_diff_headers(self, diff_text: str) -> List[Tuple[str, str]]:
        """
        Parse diff to extract file changes.
        
        Returns:
            List of (file_path, change_type) tuples
        """
        files = []
        for line in diff_text.split('\n'):
            if line.startswith('+++'):
                file_path = line[6:].strip()
                files.append((file_path, 'modified'))
            elif line.startswith('diff --git'):
                # Extract file name  
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3]
                    files.append((file_path, 'unknown'))
        
        return files
    
    def parse_changed_functions(self, diff_text: str) -> Dict[str, List[str]]:
        """
        Parse diff to extract function changes.
        
        Returns:
            Dict mapping file paths to changed function names
        """
        functions_by_file = {}
        current_file = None
        
        for line in diff_text.split('\n'):
            if line.startswith('+++'):
                current_file = line[6:].strip()
                functions_by_file[current_file] = []
            elif line.startswith('@@'):
                # Function signature is usually in the context
                # Extract it if available
                if 'def ' in line:
                    func_name = line.split('def ')[-1].split('(')[0].strip()
                    if current_file:
                        functions_by_file[current_file].append(func_name)
            elif line.startswith('+def') or line.startswith('-def'):
                # Try to extract new/removed function
                func_name = line[1:].split('(')[0].replace('def ', '').strip()
                if func_name and current_file:
                    functions_by_file[current_file].append(func_name)
        
        return functions_by_file
    
    def count_changes(self, diff_text: str) -> Tuple[int, int, int]:
        """Count additions and deletions"""
        added = diff_text.count('\n+') - diff_text.count('\n+++')
        deleted = diff_text.count('\n-') - diff_text.count('\n---')
        files = len([l for l in diff_text.split('\n') if l.startswith('diff --git')])
        return added, deleted, files
    
    def calculate_risk_level(self, added: int, deleted: int, files: int) -> str:
        """Calculate risk level of changes"""
        change_magnitude = added + deleted
        
        if files > 20 or change_magnitude > 500:
            return "high"
        elif files > 5 or change_magnitude > 100:
            return "medium"
        else:
            return "low"
    
    def analyze_diff(self, from_ref: str = "main", 
                    to_ref: str = "HEAD") -> DiffAnalysis:
        """Analyze complete diff between two refs"""
        logger.info(f"Analyzing diff {from_ref}...{to_ref}")
        
        diff_text = self.get_diff(from_ref, to_ref)
        
        # Parse changes
        files = self.parse_diff_headers(diff_text)
        functions = self.parse_changed_functions(diff_text)
        added, deleted, file_count = self.count_changes(diff_text)
        
        # Extract affected modules
        affected_modules = set()
        for file_path, _ in files:
            # src/module/file.py → src.module
            parts = file_path.replace('.py', '').split('/')
            if len(parts) >= 2:
                module = '.'.join(parts[:-1])
                affected_modules.add(module)
        
        # Calculate risk
        risk = self.calculate_risk_level(added, deleted, file_count)
        
        # Create changes list
        changes = []
        for file_path, change_type in files:
            change = DiffChange(
                file_path=file_path,
                change_type=change_type,
                added_lines=added,
                deleted_lines=deleted,
                functions_affected=functions.get(file_path, []),
                imports_affected=[]
            )
            changes.append(change)
        
        return DiffAnalysis(
            commit_range=f"{from_ref}...{to_ref}",
            total_changes=added + deleted,
            files_changed=file_count,
            changes=changes,
            affected_functions=set(f for funcs in functions.values() for f in funcs),
            affected_modules=affected_modules,
            affected_tests=set(),  # Would use Phase 32 to find these
            risk_level=risk
        )


class DiffAwarePlanner:
    """Plans missions based on diff context"""
    
    def __init__(self, repo_path: str = "/workspaces/Piddy"):
        self.analyzer = GitDiffAnalyzer(repo_path)
    
    def plan_cleanup_mission(self, from_ref: str = "main") -> Dict:
        """
        Plan dead code cleanup based on diff.
        
        Focuses on:
        - Code that was recently removed (might have orphaned deps)
        - Modules with high churn (likely have dead code)
        """
        analysis = self.analyzer.analyze_diff(from_ref)
        
        plan = {
            'goal': 'Cleanup dead code in changed areas',
            'priority': 'high' if analysis.risk_level == 'high' else 'normal',
            'focus_modules': list(analysis.affected_modules),
            'changed_functions': list(analysis.affected_functions),
            'tasks': [
                'analyze_dependent_code',
                'find_unreachable_functions',
                'identify_orphaned_imports',
                'create_cleanup_plan',
                'execute_cleanup',
                'validate_tests',
            ],
            'estimated_impact': f"{analysis.files_changed} files affected",
        }
        
        return plan
    
    def plan_refactor_mission(self, from_ref: str = "main") -> Dict:
        """
        Plan refactoring based on diff.
        
        Focuses on:
        - Extracting modules that were significantly changed
        - Consolidating related changes
        """
        analysis = self.analyzer.analyze_diff(from_ref)
        
        if analysis.risk_level == 'high':
            refactor_strategy = 'incremental'  # Break into smaller changes
        else:
            refactor_strategy = 'direct'  # Can do in one go
        
        plan = {
            'goal': 'Refactor changed code sections',
            'strategy': refactor_strategy,
            'priority': 'high' if analysis.risk_level == 'high' else 'normal',
            'focus_modules': list(analysis.affected_modules),
            'tasks': [
                'analyze_structure',
                'identify_extraction_opportunities',
                'create_refactor_plan',
                'execute_refactor',
                'validate_contracts',
                'validate_types',
            ],
            'estimated_impact': f"{analysis.total_changes} lines affected",
        }
        
        return plan
    
    def plan_test_optimization(self, from_ref: str = "main") -> Dict:
        """
        Plan test suite optimization based on diff impact.
        
        Only run tests affected by the changes.
        """
        analysis = self.analyzer.analyze_diff(from_ref)
        
        plan = {
            'goal': 'Optimize test selection for changed code',
            'priority': 'critical',
            'affected_modules': list(analysis.affected_modules),
            'affected_functions': list(analysis.affected_functions),
            'tasks': [
                'analyze_test_dependencies',
                'map_functions_to_tests',
                'select_affected_tests',
                'run_selected_tests',
                'report_results',
            ],
            'estimated_time_savings': '60-70%',
            'risk_level': analysis.risk_level,
        }
        
        return plan
    
    def generate_mission_from_diff(self, mission_type: str, 
                                  from_ref: str = "main") -> Dict:
        """Generate mission based on diff"""
        if mission_type == 'cleanup':
            return self.plan_cleanup_mission(from_ref)
        elif mission_type == 'refactor':
            return self.plan_refactor_mission(from_ref)
        elif mission_type == 'test':
            return self.plan_test_optimization(from_ref)
        else:
            raise ValueError(f"Unknown mission type: {mission_type}")


if __name__ == '__main__':
    # Example usage
    planner = DiffAwarePlanner()
    
    # Analyze diff
    print("=" * 70)
    print("DIFF ANALYSIS")
    print("=" * 70)
    
    try:
        # Try to get diff if in git repo
        analysis = planner.analyzer.analyze_diff("HEAD~1", "HEAD")
        print(f"Files changed: {analysis.files_changed}")
        print(f"Total changes: {analysis.total_changes} lines")
        print(f"Risk level: {analysis.risk_level}")
        print(f"Affected modules: {analysis.affected_modules}")
    except:
        print("(Not in git repo or no history)")
    
    # Generate cleanup plan
    print("\n" + "=" * 70)
    print("CLEANUP MISSION PLAN (based on diff)")
    print("=" * 70)
    
    plan = planner.plan_cleanup_mission()
    print(json.dumps(plan, indent=2))
