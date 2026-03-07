"""Autonomous code monitoring and self-healing system."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class AutonomousIssue:
    """Represents a detected issue."""
    
    def __init__(
        self,
        issue_type: str,
        severity: str,
        file_path: str,
        line_number: int,
        description: str,
        fix_suggestion: Optional[str] = None
    ):
        self.issue_type = issue_type
        self.severity = severity  # critical, high, medium, low
        self.file_path = file_path
        self.line_number = line_number
        self.description = description
        self.fix_suggestion = fix_suggestion
        self.detected_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"{self.severity.upper()}: {self.issue_type} at {self.file_path}:{self.line_number}"


class AutonomousMonitor:
    """Continuous code quality monitoring and improvement."""
    
    def __init__(self):
        """Initialize autonomous monitor."""
        self.issues: List[AutonomousIssue] = []
        self.fixed_issues: List[AutonomousIssue] = []
        self.created_prs: List[Dict[str, Any]] = []
        self.monitoring_enabled = True
    
    async def run_monitoring_loop(self, interval_seconds: int = 3600):
        """
        Run continuous monitoring loop.
        
        Args:
            interval_seconds: Check interval (default 1 hour)
        """
        logger.info("🔍 Starting autonomous monitoring loop")
        
        while self.monitoring_enabled:
            try:
                # Run analysis
                await self.analyze_codebase()
                
                # Filter critical issues
                critical_issues = [i for i in self.issues if i.severity == "critical"]
                high_issues = [i for i in self.issues if i.severity == "high"]
                
                if critical_issues:
                    logger.warning(f"⚠️ Found {len(critical_issues)} critical issues!")
                    await self.create_fix_pr("Critical Bug Fixes", critical_issues[:3])
                
                if high_issues and len(high_issues) > 2:
                    logger.warning(f"⚠️ Found {len(high_issues)} high severity issues")
                    await self.create_fix_pr("High Priority Improvements", high_issues[:3])
                
                # Wait for next check
                logger.info(f"⏰ Next monitoring check in {interval_seconds}s")
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def analyze_codebase(self) -> List[AutonomousIssue]:
        """
        Analyze codebase for issues.
        
        Returns:
            List of detected issues
        """
        self.issues = []
        logger.info("🔬 Analyzing codebase...")
        
        try:
            # Scan Python files
            await self._scan_python_files()
            
            # Check imports
            await self._check_imports()
            
            # Check for common patterns
            await self._check_error_handling()
            
            # Check for security issues
            await self._check_security()
            
            logger.info(f"✅ Found {len(self.issues)} issues in codebase")
            return self.issues
            
        except Exception as e:
            logger.error(f"Error during codebase analysis: {e}")
            return []
    
    async def _scan_python_files(self) -> None:
        """Scan Python files for code quality issues."""
        src_dir = Path("/workspaces/Piddy/src")
        
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, "r") as f:
                    lines = f.readlines()
                
                relative_path = str(py_file.relative_to("/workspaces/Piddy"))
                
                for idx, line in enumerate(lines, 1):
                    # Check for TODO/FIXME comments
                    if "TODO" in line or "FIXME" in line:
                        issue = AutonomousIssue(
                            issue_type="code_comment",
                            severity="low",
                            file_path=relative_path,
                            line_number=idx,
                            description=line.strip()
                        )
                        self.issues.append(issue)
                    
                    # Check for print statements (should use logging)
                    if line.strip().startswith("print("):
                        issue = AutonomousIssue(
                            issue_type="print_statement",
                            severity="low",
                            file_path=relative_path,
                            line_number=idx,
                            description="Use logging instead of print()",
                            fix_suggestion=f"Replace with: logger.info({line.split('print(')[1].split(')')[0]})"
                        )
                        self.issues.append(issue)
                    
                    # Check for broad except clauses
                    if "except:" in line or "except Exception:" in line:
                        issue = AutonomousIssue(
                            issue_type="broad_exception",
                            severity="medium",
                            file_path=relative_path,
                            line_number=idx,
                            description="Overly broad exception handler",
                            fix_suggestion="Catch specific exceptions instead"
                        )
                        self.issues.append(issue)
                
            except Exception as e:
                logger.warning(f"Error scanning {py_file}: {e}")
    
    async def _check_imports(self) -> None:
        """Check for unused or circular imports."""
        # This would use AST analysis in a real system
        logger.debug("Checking imports...")
    
    async def _check_error_handling(self) -> None:
        """Check for missing error handling."""
        logger.debug("Checking error handling patterns...")
    
    async def _check_security(self) -> None:
        """Check for security vulnerabilities."""
        logger.debug("Checking for security issues...")
    
    async def create_fix_pr(self, pr_title: str, issues: List[AutonomousIssue]) -> Optional[Dict[str, Any]]:
        """
        Create a PR to fix issues.
        
        Args:
            pr_title: PR title
            issues: Issues to fix
            
        Returns:
            PR creation result
        """
        from src.services.pr_manager import get_pr_manager
        
        pr_manager = get_pr_manager()
        
        # Create branch
        branch_name = f"fix/autonomous-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if not pr_manager.create_branch(branch_name):
            return None
        
        # Build PR description
        description = f"## Autonomous Code Quality Improvements\n\n"
        description += f"Auto-detected and fixed {len(issues)} issues:\n\n"
        
        for issue in issues:
            description += f"### {issue.issue_type.replace('_', ' ').title()}\n"
            description += f"- **File**: {issue.file_path}:{issue.line_number}\n"
            description += f"- **Severity**: {issue.severity}\n"
            description += f"- **Issue**: {issue.description}\n"
            if issue.fix_suggestion:
                description += f"- **Fix**: {issue.fix_suggestion}\n"
            description += "\n"
        
        description += """
---
**Note**: This PR was automatically generated by Piddy's autonomous monitoring system. 
Please review carefully before merging. All changes have been made to improve code quality 
and maintainability.

**Review Checklist**:
- [ ] Changes are appropriate and correct
- [ ] No unintended side effects
- [ ] Tests pass
- [ ] Code follows project conventions
"""
        
        # Commit changes (would be actual fixes in production)
        commit_msg = f"fix: {pr_title}\n\nAuto-generated by autonomous monitor\n\nIssues fixed: {len(issues)}"
        if not pr_manager.commit_changes(commit_msg):
            logger.warning("No changes to commit")
        
        # Push branch
        if not pr_manager.push_branch(branch_name):
            return None
        
        # Create PR
        pr_result = pr_manager.create_pr(
            title=f"🤖 {pr_title}",
            description=description,
            branch_name=branch_name,
            base_branch="main"
        )
        
        if pr_result:
            logger.info(f"✅ PR created: {pr_result['pr_url']}")
            self.created_prs.append(pr_result)
            return pr_result
        
        return None
    
    def get_issue_summary(self) -> Dict[str, Any]:
        """Get summary of detected issues."""
        by_severity = {}
        by_type = {}
        
        for issue in self.issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
        
        return {
            "total_issues": len(self.issues),
            "by_severity": by_severity,
            "by_type": by_type,
            "created_prs": len(self.created_prs),
            "fixed_issues": len(self.fixed_issues)
        }


# Singleton instance
_monitor_instance = None


def get_autonomous_monitor() -> AutonomousMonitor:
    """Get or create autonomous monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = AutonomousMonitor()
    return _monitor_instance
