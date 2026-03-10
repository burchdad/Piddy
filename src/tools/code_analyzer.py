"""
Advanced code analysis and review tool.

Performs comprehensive code quality checks including:
- Security vulnerabilities
- Performance issues
- Best practices violations
- Code style and standards
- Type safety checks
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Issue severity levels."""
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🔵 LOW"
    INFO = "⚪ INFO"


class IssueCategory(Enum):
    """Categories of code issues."""
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    BEST_PRACTICE = "Best Practice"
    STYLE = "Code Style"
    MAINTAINABILITY = "Maintainability"
    ERROR_HANDLING = "Error Handling"
    TYPE_SAFETY = "Type Safety"


@dataclass
class CodeIssue:
    """Represents a code quality issue."""
    category: IssueCategory
    severity: SeverityLevel
    line: Optional[int]
    message: str
    suggestion: str
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "line": self.line,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet
        }

    def format_for_slack(self) -> str:
        """Format issue for Slack message."""
        return f"{self.severity.value} | {self.category.value}\n_{self.message}_\n💡 {self.suggestion}"


class CodeAnalyzer:
    """
    Advanced code analyzer for detecting issues and providing improvements.
    """

    # Security patterns to detect
    SECURITY_PATTERNS = {
        r"exec\s*\(": ("exec() call detected", "Use safer alternatives like ast.literal_eval()"),
        r"eval\s*\(": ("eval() call detected", "Avoid eval(); use safer parsing methods"),
        r"pickle\.loads\s*\(": ("Unsafe pickle.loads()", "Use json or other safe serialization"),
        r"subprocess\.call\s*\(['\"]": ("Shell injection risk in subprocess", "Use subprocess with shell=False"),
        r"os\.system\s*\(": ("os.system() is unsafe", "Use subprocess.run() instead"),
        r"password\s*=\s*['\"]": ("Hardcoded password detected", "Use environment variables"),
        r"secret\s*=\s*['\"]": ("Hardcoded secret detected", "Use environment variables or secrets manager"),
        r"sql\s+['\"].*where": ("Potential SQL injection", "Use parameterized queries"),
    }

    # Performance patterns
    PERFORMANCE_PATTERNS = {
        r"for\s+\w+\s+in\s+.*:\s*\n.*\.query\(": ("N+1 query pattern", "Use JOIN or batch queries"),
        r"\.encode\(\)\.decode\(\)": ("Unnecessary encode/decode", "Use string directly"),
        r"re\.compile\s*\(.*\)\s*(outside.*loop)?": ("Regex compiled in loop", "Move re.compile() outside loop"),
        r"\[.*for.*in.*\]\[0\]": ("Creating list just to get first item", "Use next(iter(...)) instead"),
    }

    # Best practices patterns
    BEST_PRACTICE_PATTERNS = {
        r"except\s*:\s*$": ("Bare except clause", "Catch specific exceptions"),
        r"except\s*Exception\s*:\s*$": ("Catching broad Exception", "Catch specific exceptions"),
        r"except.*pass\s*$": ("Silent exception catch", "Log or handle the exception properly"),
        r"is\s+True": ("Using 'is' for True comparison", "Use 'if condition:' instead"),
        r"is\s+False": ("Using 'is' for False comparison", "Use 'if not condition:' instead"),
        r"if\s+len\(.*\)\s*[!=]" : ("Length check inefficient", "Use truthiness instead: if list:"),
    }

    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code and return issues found.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Dictionary with analysis results:
                - issues: List of CodeIssue objects
                - summary: Summary statistics
                - score: Overall quality score (0-100)
                - recommendations: List of actionable recommendations
        """
        if language.lower() != "python":
            return {
                "issues": [],
                "summary": {"total": 0},
                "score": 100,
                "recommendations": ["Full analysis only available for Python"],
                "language_support": f"Extended analysis for {language} coming soon"
            }

        issues: List[CodeIssue] = []
        lines = code.split('\n')

        # Run all analysis passes
        issues.extend(self._check_security(code, lines))
        issues.extend(self._check_performance(code, lines))
        issues.extend(self._check_best_practices(code, lines))
        issues.extend(self._check_error_handling(code, lines))
        issues.extend(self._check_type_safety(code, lines))

        # Remove duplicates
        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.line, issue.message)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        # Calculate score
        score = self._calculate_quality_score(unique_issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(unique_issues)

        # Summary
        summary = self._generate_summary(unique_issues)

        return {
            "issues": unique_issues,
            "summary": summary,
            "score": score,
            "recommendations": recommendations
        }

    def _check_security(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check for security vulnerabilities."""
        issues = []
        for line_num, line in enumerate(lines, 1):
            for pattern, (message, suggestion) in self.SECURITY_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        line=line_num,
                        message=message,
                        suggestion=suggestion,
                        code_snippet=line.strip()
                    ))
        return issues

    def _check_performance(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check for performance issues."""
        issues = []
        for line_num, line in enumerate(lines, 1):
            for pattern, (message, suggestion) in self.PERFORMANCE_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.PERFORMANCE,
                        severity=SeverityLevel.HIGH,
                        line=line_num,
                        message=message,
                        suggestion=suggestion,
                        code_snippet=line.strip()
                    ))
        return issues

    def _check_best_practices(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check for best practice violations."""
        issues = []
        for line_num, line in enumerate(lines, 1):
            for pattern, (message, suggestion) in self.BEST_PRACTICE_PATTERNS.items():
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        category=IssueCategory.BEST_PRACTICE,
                        severity=SeverityLevel.MEDIUM,
                        line=line_num,
                        message=message,
                        suggestion=suggestion,
                        code_snippet=line.strip()
                    ))
        return issues

    def _check_error_handling(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check error handling practices."""
        issues = []

        # Check for unhandled external calls
        external_calls = re.findall(r"\.get\(|\.post\(|\.request\(|\.query\(", code)
        if external_calls and "try:" not in code:
            issues.append(CodeIssue(
                category=IssueCategory.ERROR_HANDLING,
                severity=SeverityLevel.HIGH,
                line=None,
                message="External calls without try-except handling",
                suggestion="Wrap external API calls in try-except blocks"
            ))

        # Check for missing None checks
        if re.search(r"\.\w+\(\)", code) and "is not None" not in code:
            for line_num, line in enumerate(lines, 1):
                if re.search(r"return\s+\w+\.\w+", line):
                    issues.append(CodeIssue(
                        category=IssueCategory.ERROR_HANDLING,
                        severity=SeverityLevel.MEDIUM,
                        line=line_num,
                        message="Potential AttributeError on None",
                        suggestion="Add None check before accessing attributes"
                    ))

        return issues

    def _check_type_safety(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check type safety."""
        issues = []

        # Check for missing type hints in functions
        func_pattern = r"def\s+\w+\s*\([^)]*\)\s*:"
        for line_num, line in enumerate(lines, 1):
            if re.search(func_pattern, line):
                if "->" not in line and "def test_" not in line:
                    issues.append(CodeIssue(
                        category=IssueCategory.TYPE_SAFETY,
                        severity=SeverityLevel.LOW,
                        line=line_num,
                        message="Missing return type hint",
                        suggestion="Add return type annotation: -> ReturnType",
                        code_snippet=line.strip()
                    ))

        return issues

    def _calculate_quality_score(self, issues: List[CodeIssue]) -> int:
        """Calculate overall quality score."""
        if not issues:
            return 100

        severity_weights = {
            SeverityLevel.CRITICAL: 20,
            SeverityLevel.HIGH: 10,
            SeverityLevel.MEDIUM: 5,
            SeverityLevel.LOW: 2,
            SeverityLevel.INFO: 1
        }

        total_penalty = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        score = max(0, 100 - total_penalty)
        return score

    def _generate_summary(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Generate summary statistics."""
        summary = {
            "total": len(issues),
            "critical": len([i for i in issues if i.severity == SeverityLevel.CRITICAL]),
            "high": len([i for i in issues if i.severity == SeverityLevel.HIGH]),
            "medium": len([i for i in issues if i.severity == SeverityLevel.MEDIUM]),
            "low": len([i for i in issues if i.severity == SeverityLevel.LOW]),
        }
        return summary

    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Based on categories found
        categories = set(issue.category for issue in issues)

        if IssueCategory.SECURITY in categories:
            recommendations.append("🔒 **Security**: Audit all external inputs and use parameterized queries")

        if IssueCategory.PERFORMANCE in categories:
            recommendations.append("⚡ **Performance**: Consider caching, batch operations, and database optimization")

        if IssueCategory.ERROR_HANDLING in categories:
            recommendations.append("🛡️ **Error Handling**: Add comprehensive try-except blocks and logging")

        if IssueCategory.TYPE_SAFETY in categories:
            recommendations.append("📝 **Type Safety**: Add type hints throughout for better IDE support and fewer runtime errors")

        if not recommendations:
            recommendations.append("✅ Code looks good! Consider adding tests and documentation.")

        return recommendations

    def review_for_slack(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Get code review formatted for Slack display.

        Args:
            code: Code to review
            language: Programming language

        Returns:
            Slack-formatted review with issues
        """
        analysis = self.analyze(code, language)

        slack_blocks = {
            "summary": f"📊 Code Quality: {analysis['score']}/100",
            "issues_by_severity": {}
        }

        # Group issues by severity
        for severity in SeverityLevel:
            severity_issues = [i for i in analysis["issues"] if i.severity == severity]
            if severity_issues:
                slack_blocks["issues_by_severity"][severity.value] = [
                    i.format_for_slack() for i in severity_issues[:5]  # Top 5 per severity
                ]

        slack_blocks["recommendations"] = analysis["recommendations"]

        return slack_blocks


def get_code_analyzer() -> CodeAnalyzer:
    """Get code analyzer instance."""
    return CodeAnalyzer()
