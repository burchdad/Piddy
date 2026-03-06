"""
GraphQL query analysis for Phase 5.
Analyzes GraphQL schemas and queries for security, performance, and best practices.
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GraphQLIssue:
    """GraphQL analysis issue."""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "security", "performance", "best_practice"
    message: str
    location: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None


class GraphQLAnalyzer:
    """
    Analyzes GraphQL schemas and queries for issues.
    Detects security vulnerabilities, performance problems, and best practice violations.
    """

    def __init__(self):
        """Initialize GraphQL analyzer."""
        self.security_patterns = self._init_security_patterns()
        self.performance_patterns = self._init_performance_patterns()
        logger.info("✅ GraphQL Analyzer initialized")

    def _init_security_patterns(self) -> Dict[str, Dict]:
        """Initialize security issue patterns."""
        return {
            "missing_validation": {
                "pattern": r"input\s+\w+\s*\{[^}]*(?!@[a-zA-Z]+)[^}]*\}",
                "severity": "high",
                "message": "Input type missing validation directives",
                "suggestion": "Add @validate or custom validation directives",
            },
            "unbounded_list": {
                "pattern": r"\[\w+!\](?!\s*@[limit|first|max])",
                "severity": "high",
                "message": "Unbounded list field could cause performance issues",
                "suggestion": "Add @limit or @first directive to paginate results",
            },
            "missing_auth": {
                "pattern": r"type\s+Query\s*\{[^}]*(?!@auth|@authenticated)",
                "severity": "critical",
                "message": "Query type missing authentication directives",
                "suggestion": "Add @auth or @authenticated directives to secure operations",
            },
            "exposed_internals": {
                "pattern": r"field_name:\s*(?:__.*__|private.*)",
                "severity": "medium",
                "message": "Field exposes internal implementation details",
                "suggestion": "Hide internal fields or rename appropriately",
            },
        }

    def _init_performance_patterns(self) -> Dict[str, Dict]:
        """Initialize performance issue patterns."""
        return {
            "n_plus_one": {
                "pattern": r"type\s+\w+\s*\{[^}]*\w+:\s*\[\w+\][^}]*\}",
                "severity": "high",
                "message": "Potential N+1 query problem with nested list fields",
                "suggestion": "Use connection-based pagination or DataLoader",
            },
            "deep_nesting": {
                "severity": "medium",
                "message": "Query has excessive nesting depth",
                "suggestion": "Limit query depth with @cost directive or recursive limits",
            },
            "large_fragment": {
                "severity": "low",
                "message": "Fragment or query is very large",
                "suggestion": "Break into smaller, reusable fragments",
            },
        }

    def analyze_schema(self, schema: str) -> Dict[str, Any]:
        """
        Analyze GraphQL schema for issues.

        Args:
            schema: GraphQL schema definition

        Returns:
            Analysis results with issues and recommendations
        """
        issues: List[GraphQLIssue] = []
        metrics: Dict[str, int] = {
            "type_count": 0,
            "field_count": 0,
            "interface_count": 0,
            "enum_count": 0,
            "directive_count": 0,
        }

        # Count schema elements
        metrics["type_count"] = len(re.findall(r"type\s+\w+", schema))
        metrics["interface_count"] = len(re.findall(r"interface\s+\w+", schema))
        metrics["enum_count"] = len(re.findall(r"enum\s+\w+", schema))
        metrics["directive_count"] = len(re.findall(r"directive\s+@\w+", schema))
        metrics["field_count"] = schema.count(":")

        # Security checks
        has_query = "type Query" in schema
        has_mutation = "type Mutation" in schema
        has_subscription = "type Subscription" in schema

        if not has_query:
            issues.append(GraphQLIssue(
                severity="critical",
                category="security",
                message="Schema missing Query type",
                suggestion="Define type Query with root fields"
            ))

        # Check for authentication
        if "@auth" not in schema and "@authenticated" not in schema:
            issues.append(GraphQLIssue(
                severity="high",
                category="security",
                message="No authentication directives found in schema",
                suggestion="Add @auth or @authenticated directives to protect operations"
            ))

        # Check for input validation
        if "input " in schema and "@validate" not in schema:
            issues.append(GraphQLIssue(
                severity="high",
                category="security",
                message="Input types found but no validation directives",
                suggestion="Add @validate directive or custom validation rules"
            ))

        # Check for rate limiting
        if "@rateLimit" not in schema and "@cost" not in schema:
            issues.append(GraphQLIssue(
                severity="medium",
                category="security",
                message="No rate limiting or cost directives for resource protection",
                suggestion="Add @rateLimit or @cost directives"
            ))

        # Performance checks
        list_field_count = len(re.findall(r":\s*\[", schema))
        if list_field_count > 10:
            issues.append(GraphQLIssue(
                severity="medium",
                category="performance",
                message=f"High number of list fields ({list_field_count}) - watch for N+1 problems",
                suggestion="Use DataLoader pattern and pagination"
            ))

        # Best practices
        has_id_fields = "id: ID!" in schema or "ID!" in schema
        if not has_id_fields:
            issues.append(GraphQLIssue(
                severity="low",
                category="best_practice",
                message="Types should have ID fields for caching",
                suggestion="Add id: ID! field to object types"
            ))

        has_descriptions = '"""' in schema or "# " in schema
        if not has_descriptions:
            issues.append(GraphQLIssue(
                severity="low",
                category="best_practice",
                message="Schema lacks documentation/descriptions",
                suggestion="Add SDL descriptions to types and fields"
            ))

        severity_count = {
            "critical": len([i for i in issues if i.severity == "critical"]),
            "high": len([i for i in issues if i.severity == "high"]),
            "medium": len([i for i in issues if i.severity == "medium"]),
            "low": len([i for i in issues if i.severity == "low"]),
        }

        return {
            "schema_quality_score": self._calculate_quality_score(issues),
            "metrics": metrics,
            "issues": [self._issue_to_dict(i) for i in issues],
            "severity_count": severity_count,
            "recommendations": self._generate_schema_recommendations(issues),
        }

    def analyze_query(self, query: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Analyze GraphQL query for issues.

        Args:
            query: GraphQL query string
            max_depth: Maximum allowed query depth

        Returns:
            Query analysis results
        """
        issues: List[GraphQLIssue] = []

        # Parse query depth
        depth = self._calculate_query_depth(query)
        if depth > max_depth:
            issues.append(GraphQLIssue(
                severity="high",
                category="security",
                message=f"Query depth ({depth}) exceeds maximum ({max_depth})",
                suggestion="Limit query depth to prevent DoS attacks"
            ))

        # Check query size
        query_size = len(query)
        if query_size > 10000:
            issues.append(GraphQLIssue(
                severity="medium",
                category="performance",
                message=f"Large query ({query_size} chars) may impact performance",
                suggestion="Break into smaller queries or use fragments"
            ))

        # Check for aliases (potential performance issue)
        alias_count = query.count(":")
        if alias_count > 20:
            issues.append(GraphQLIssue(
                severity="low",
                category="performance",
                message=f"High number of field aliases ({alias_count}) may impact performance",
                suggestion="Consider if all fields are necessary"
            ))

        # Check for fragments
        has_fragments = fragment_count = query.count("fragment ")
        if alias_count > 10 and fragment_count == 0:
            issues.append(GraphQLIssue(
                severity="low",
                category="best_practice",
                message="Repeated field selections could use fragments",
                suggestion="Extract repeated selections into reusable fragments"
            ))

        # Check for variables (security best practice)
        has_hardcoded_values = re.search(r'(:\s*"[^"]*"|\{\s*[a-zA-Z]+:\s*[0-9]+)', query)
        if has_hardcoded_values and re.search(r"\$\w+", query) is None:
            issues.append(GraphQLIssue(
                severity="medium",
                category="security",
                message="Query uses hardcoded values instead of variables",
                suggestion="Use variables ($variable) for dynamic values"
            ))

        metrics = {
            "depth": depth,
            "size_chars": query_size,
            "fragment_count": fragment_count,
            "alias_count": alias_count,
        }

        severity_count = {
            "critical": len([i for i in issues if i.severity == "critical"]),
            "high": len([i for i in issues if i.severity == "high"]),
            "medium": len([i for i in issues if i.severity == "medium"]),
            "low": len([i for i in issues if i.severity == "low"]),
        }

        return {
            "query_quality_score": self._calculate_quality_score(issues),
            "metrics": metrics,
            "issues": [self._issue_to_dict(i) for i in issues],
            "severity_count": severity_count,
            "recommendations": self._generate_query_recommendations(issues),
        }

    def _calculate_query_depth(self, query: str, current_depth: int = 0) -> int:
        """Calculate maximum depth of a GraphQL query."""
        max_depth = current_depth
        depth = current_depth

        for char in query:
            if char == "{":
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == "}":
                depth -= 1

        return max_depth

    def _calculate_quality_score(self, issues: List[GraphQLIssue]) -> float:
        """Calculate quality score based on issues."""
        if not issues:
            return 100.0

        severity_weights = {
            "critical": 50,
            "high": 25,
            "medium": 10,
            "low": 5,
        }

        total_deduction = sum(severity_weights.get(i.severity, 0) for i in issues)
        return max(0.0, 100.0 - total_deduction)

    def _generate_schema_recommendations(self, issues: List[GraphQLIssue]) -> List[str]:
        """Generate recommendations based on schema issues."""
        recommendations = []

        if any(i.severity == "critical" for i in issues):
            recommendations.append("🔴 Critical issues found - address before deployment")

        if any(i.category == "security" for i in issues):
            recommendations.append("🔒 Add authentication and rate limiting directives")

        if any(i.category == "performance" for i in issues):
            recommendations.append("⚡ Optimize schema for performance with pagination and DataLoader")

        if not recommendations:
            recommendations.append("✅ Schema looks good - consider adding more documentation")

        return recommendations

    def _generate_query_recommendations(self, issues: List[GraphQLIssue]) -> List[str]:
        """Generate recommendations based on query issues."""
        recommendations = []

        if any(i.severity in ["critical", "high"] for i in issues):
            recommendations.append("Consider revising query before sending")

        if any("depth" in i.message.lower() for i in issues):
            recommendations.append("Break query into smaller operations")

        if any("variable" in i.message.lower() for i in issues):
            recommendations.append("Use variables for dynamic values")

        if not recommendations:
            recommendations.append("✅ Query looks good")

        return recommendations

    def _issue_to_dict(self, issue: GraphQLIssue) -> Dict:
        """Convert issue to dictionary."""
        return {
            "severity": issue.severity,
            "category": issue.category,
            "message": issue.message,
            "suggestion": issue.suggestion,
            "location": issue.location,
            "line": issue.line,
        }

    def suggest_schema_improvements(self, schema: str) -> List[str]:
        """Get suggested improvements for schema."""
        suggestions = []

        if "scalar DateTime" not in schema:
            suggestions.append("Consider adding DateTime scalar for timestamps")

        if "scalar JSON" not in schema:
            suggestions.append("Add JSON scalar for flexible data structures")

        if "interface Node" not in schema:
            suggestions.append("Implement Node interface for consistent ID handling")

        if "directive @deprecated" not in schema:
            suggestions.append("Add @deprecated directive for API versioning")

        if "@cost" not in schema:
            suggestions.append("Implement @cost directive for query complexity analysis")

        return suggestions


# Global analyzer instance
_analyzer_instance: Optional[GraphQLAnalyzer] = None


def get_graphql_analyzer() -> GraphQLAnalyzer:
    """Get or create global GraphQL analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GraphQLAnalyzer()
    return _analyzer_instance
