"""Code analysis and review tools."""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)
@dataclass
class CodeIssue:
    """Represents a code issue found during review."""
    severity: str  # critical, warning, info
    type: str  # performance, security, style, logic
    line: int
    message: str
    suggestion: str
    example: str = ""


def analyze_code_quality(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Comprehensive code quality analysis.
    
    Checks for:
    - Performance issues
    - Security vulnerabilities
    - Code style violations
    - Logic errors
    - Best practice violations
    """
    
    issues = []
    metrics = {
        "complexity": 0,
        "maintainability": 80,
        "security_score": 75,
        "performance_score": 70,
    }
    
    if language.lower() == "python":
        issues.extend(_analyze_python(code))
    elif language.lower() in ["javascript", "typescript", "nodejs"]:
        issues.extend(_analyze_javascript(code))
    elif language.lower() == "go":
        issues.extend(_analyze_go(code))
    elif language.lower() == "java":
        issues.extend(_analyze_java(code))
    elif language.lower() == "rust":
        issues.extend(_analyze_rust(code))
    
    # Calculate metrics based on issues
    for issue in issues:
        if issue.severity == "critical":
            metrics["security_score"] -= 15
            metrics["maintainability"] -= 10
        elif issue.severity == "warning":
            metrics["maintainability"] -= 5
    
    return {
        "language": language,
        "issues": [
            {
                "severity": i.severity,
                "type": i.type,
                "message": i.message,
                "suggestion": i.suggestion,
                "example": i.example,
            }
            for i in issues
        ],
        "metrics": metrics,
        "total_issues": len(issues),
        "grade": _calculate_grade(metrics),
    }


def _analyze_python(code: str) -> List[CodeIssue]:
    """Analyze Python code."""
    issues = []
    
    # Check for common issues
    if "import *" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Avoid wildcard imports",
            suggestion="Import specific items instead of using *",
            example="from module import function, class  # instead of from module import *",
        ))
    
    if "exec(" in code or "eval(" in code:
        issues.append(CodeIssue(
            severity="critical",
            type="security",
            line=0,
            message="Avoid eval/exec - security risk",
            suggestion="Use safer alternatives like ast.literal_eval",
            example="data = ast.literal_eval(user_input)  # safer than eval()",
        ))
    
    if "except:" in code or "except Exception as e:" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Broad exception handling",
            suggestion="Catch specific exceptions",
            example="except ValueError: pass  # instead of except:",
        ))
    
    if "logger.info(" in code and "logger" not in code:
        issues.append(CodeIssue(
            severity="info",
            type="style",
            line=0,
            message="Use logging instead of print",
            suggestion="Use logging module for production code",
            example="logger.info('message')  # instead of logger.info()",
        ))
    
    if "TODO" in code or "FIXME" in code or "HACK" in code:
        issues.append(CodeIssue(
            severity="info",
            type="logic",
            line=0,
            message="Incomplete code markers found",
            suggestion="Complete implementation or document why it's incomplete",
            example="# Implement proper error handling here",
        ))
    
    return issues


def _analyze_javascript(code: str) -> List[CodeIssue]:
    """Analyze JavaScript/TypeScript code."""
    issues = []
    
    if "var " in code:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Use const/let instead of var",
            suggestion="Prefer const for immutability, let for mutable values",
            example="const variable = value;  // instead of var",
        ))
    
    if "console.log" in code:
        issues.append(CodeIssue(
            severity="info",
            type="style",
            line=0,
            message="Remove console.log statements",
            suggestion="Use proper logging framework in production",
            example="logger.info('message');  // instead of console.log()",
        ))
    
    if "==" in code and "===" not in code:
        issues.append(CodeIssue(
            severity="warning",
            type="logic",
            line=0,
            message="Use strict equality (===)",
            suggestion="Avoid loose equality that can cause unexpected type coercion",
            example="if (value === expectedValue)  // instead of ==",
        ))
    
    if "any" in code.lower() and "any" not in code[:20]:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Avoid TypeScript 'any' type",
            suggestion="Use proper type annotations",
            example="function process(data: ProcessData): Result  // instead of any",
        ))
    
    return issues


def _analyze_go(code: str) -> List[CodeIssue]:
    """Analyze Go code."""
    issues = []
    
    if "if err != nil" not in code and "error" in code:
        issues.append(CodeIssue(
            severity="critical",
            type="logic",
            line=0,
            message="Missing error handling",
            suggestion="Always check and handle errors",
            example="if err != nil {\n    return err\n}",
        ))
    
    if "panic(" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Use error returns instead of panic",
            suggestion="Return errors for normal failure conditions",
            example="return fmt.Errorf(\\\"error message\\\")  // instead of panic()",
        ))
    
    return issues


def _analyze_java(code: str) -> List[CodeIssue]:
    """Analyze Java code."""
    issues = []
    
    if ".printStackTrace()" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="style",
            line=0,
            message="Use logger instead of printStackTrace",
            suggestion="Use logging framework (SLF4J, Log4j)",
            example="logger.error(\\\"Error occurred\\\", exception);",
        ))
    
    if "synchronized" in code and "concurrent" not in code:
        issues.append(CodeIssue(
            severity="info",
            type="performance",
            line=0,
            message="Consider using concurrent utilities",
            suggestion="Use java.util.concurrent for better performance",
            example="ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>();",
        ))
    
    return issues


def _analyze_rust(code: str) -> List[CodeIssue]:
    """Analyze Rust code."""
    issues = []
    
    if "unwrap()" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="logic",
            line=0,
            message="Using unwrap() can panic",
            suggestion="Handle Result/Option properly",
            example="match result {\n    Ok(v) => { /* use v */ },\n    Err(e) => { /* handle e */ },\n}",
        ))
    
    if "unsafe" in code:
        issues.append(CodeIssue(
            severity="warning",
            type="security",
            line=0,
            message="Unsafe code block detected",
            suggestion="Minimize unsafe code and document why it's needed",
            example="// Document why unsafe is necessary here",
        ))
    
    return issues


def _calculate_grade(metrics: Dict[str, int]) -> str:
    """Calculate overall code quality grade."""
    avg_score = (
        metrics["maintainability"] + 
        metrics["security_score"] + 
        metrics["performance_score"]
    ) / 3
    
    if avg_score >= 90:
        return "A+"
    elif avg_score >= 80:
        return "A"
    elif avg_score >= 70:
        return "B"
    elif avg_score >= 60:
        return "C"
    elif avg_score >= 50:
        return "D"
    else:
        return "F"


def suggest_refactoring(code: str, language: str = "python") -> Dict[str, Any]:
    """Suggest refactoring opportunities."""
    suggestions = {
        "extracted_functions": [],
        "simplified_logic": [],
        "performance_improvements": [],
        "design_patterns": [],
    }
    
    if language.lower() == "python":
        # Check for complex functions
        if len(code.split("\n")) > 50:
            suggestions["extracted_functions"].append({
                "issue": "Function is too long (>50 lines)",
                "suggestion": "Break into smaller functions",
                "benefit": "Improved readability and testability"
            })
        
        # Check for repeated patterns
        if code.count("for ") > 3:
            suggestions["design_patterns"].append({
                "issue": "Multiple loops present",
                "suggestion": "Consider using list comprehensions or functional approaches",
                "benefit": "More Pythonic and concise code"
            })
    
    elif language.lower() in ["javascript", "typescript"]:
        if ".map().filter()" in code or ".filter().map()" in code:
            suggestions["performance_improvements"].append({
                "issue": "Multiple array iterations",
                "suggestion": "Combine map and filter operations",
                "benefit": "Reduced number of passes over data"
            })
    
    return suggestions
