"""
Infrastructure as Code (IaC) validation for Phase 5.
Validates Terraform, CloudFormation, Docker, and Kubernetes configurations.
"""
import logging
import re
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IaCIssue:
    """Issue found in IaC configuration."""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "security", "performance", "cost", "best_practice", "compliance"
    message: str
    resource: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None


class IaCValidator:
    """
    Validates Infrastructure as Code configurations.
    Supports Terraform, CloudFormation, Docker, Kubernetes, and other IaC formats.
    """

    def __init__(self):
        """Initialize IaC validator."""
        self.security_rules = self._init_security_rules()
        self.cost_rules = self._init_cost_rules()
        logger.info("✅ IaC Validator initialized")

    def _init_security_rules(self) -> Dict[str, Dict]:
        """Initialize security validation rules."""
        return {
            "exposed_credentials": {
                "patterns": [
                    r'password\s*=\s*["\']?[^"\s]+["\']?',
                    r'api_key\s*=\s*["\']?[^"\s]+["\']?',
                    r'secret\s*=\s*["\']?[^"\s]+["\']?',
                    r'token\s*=\s*["\']?[^"\s]+["\']?',
                ],
                "severity": "critical",
                "message": "Hardcoded credentials found",
                "suggestion": "Use secrets management (AWS Secrets Manager, Vault, etc.)",
            },
            "open_security_group": {
                "patterns": [
                    r'cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\]',
                    r'SecurityGroupIngress.*0.0.0.0/0',
                ],
                "severity": "critical",
                "message": "Security group/firewall rule open to world",
                "suggestion": "Restrict to specific IP ranges",
            },
            "unencrypted_data": {
                "patterns": [
                    r'encrypted\s*=\s*false',
                    r'EnableEncryption\s*=\s*false',
                    r'storage_encrypted\s*=\s*false',
                ],
                "severity": "high",
                "message": "Data storage not encrypted",
                "suggestion": "Enable encryption at rest",
            },
            "no_backup": {
                "patterns": [
                    r'backup_retention_days\s*=\s*0',
                    r'BackupRetentionPeriod\s*=\s*0',
                ],
                "severity": "high",
                "message": "Backup disabled for data store",
                "suggestion": "Enable backups with retention policy",
            },
            "missing_ssh_key": {
                "patterns": [
                    r'(instance\s*=.*password)',
                    r'without.*key.*pair',
                ],
                "severity": "high",
                "message": "SSH key not configured",
                "suggestion": "Use SSH keys instead of passwords",
            },
        }

    def _init_cost_rules(self) -> Dict[str, Dict]:
        """Initialize cost optimization rules."""
        return {
            "oversized_instance": {
                "patterns": [
                    r'instance_type\s*=\s*"(m5\.24xlarge|c5\.24xlarge|r5\.24xlarge)"',
                ],
                "severity": "medium",
                "message": "Using very expensive instance type",
                "suggestion": "Consider smaller instance size or reserved instances",
            },
            "no_autoscaling": {
                "patterns": [
                    r'(?!.*autoscaling_group).*instance.*{',
                ],
                "severity": "medium",
                "message": "Resources not using autoscaling",
                "suggestion": "Use autoscaling groups for cost optimization",
            },
            "public_ip_allocated": {
                "patterns": [
                    r'associate_public_ip_address\s*=\s*true',
                    r'PublicIpOnLaunch\s*=\s*true',
                ],
                "severity": "low",
                "message": "Public IPs allocated but may not be needed",
                "suggestion": "Use NAT gateway instead if not needed",
            },
        }

    def validate_terraform(self, config: str) -> Dict[str, Any]:
        """
        Validate Terraform configuration.

        Args:
            config: Terraform HCL configuration

        Returns:
            Validation results
        """
        issues: List[IaCIssue] = []

        # Security checks
        for rule_name, rule in self.security_rules.items():
            for pattern in rule["patterns"]:
                matches = re.findall(pattern, config, re.IGNORECASE)
                if matches:
                    issues.append(IaCIssue(
                        severity=rule["severity"],
                        category="security",
                        message=rule["message"],
                        suggestion=rule["suggestion"],
                        resource=rule_name,
                    ))

        # Cost checks
        for rule_name, rule in self.cost_rules.items():
            for pattern in rule["patterns"]:
                matches = re.findall(pattern, config, re.IGNORECASE)
                if matches:
                    issues.append(IaCIssue(
                        severity=rule["severity"],
                        category="cost",
                        message=rule["message"],
                        suggestion=rule["suggestion"],
                        resource=rule_name,
                    ))

        # Best practices
        if "tags" not in config.lower():
            issues.append(IaCIssue(
                severity="low",
                category="best_practice",
                message="Resources missing tags",
                suggestion="Add tags for resource tracking and cost allocation",
                resource="tags"
            ))

        if "depends_on" not in config and "{" in config:
            issues.append(IaCIssue(
                severity="low",
                category="best_practice",
                message="No explicit dependencies defined",
                suggestion="Use depends_on for resource ordering",
                resource="dependencies"
            ))

        severity_count = self._count_severities(issues)

        return {
            "format": "terraform",
            "quality_score": self._calculate_quality_score(issues),
            "issues": [self._issue_to_dict(i) for i in issues],
            "severity_count": severity_count,
            "resource_count": len(re.findall(r"resource\s+", config)),
            "variable_count": len(re.findall(r"variable\s+", config)),
            "output_count": len(re.findall(r"output\s+", config)),
            "recommendations": self._generate_iac_recommendations(issues),
        }

    def validate_dockerfile(self, dockerfile: str) -> Dict[str, Any]:
        """
        Validate Dockerfile for best practices and security.

        Args:
            dockerfile: Dockerfile content

        Returns:
            Validation results
        """
        issues: List[IaCIssue] = []
        lines = dockerfile.split("\n")

        # Security checks
        if "FROM" in dockerfile and "scratch" not in dockerfile.lower():
            # Check for base image from docker.io (could be malicious)
            if "FROM scratch" not in dockerfile:
                issues.append(IaCIssue(
                    severity="low",
                    category="security",
                    message="Consider using minimal base images",
                    suggestion="Use alpine, distroless, or scratch images",
                    resource="FROM"
                ))

        if "RUN apt-get install" in dockerfile and "--no-install-recommends" not in dockerfile:
            issues.append(IaCIssue(
                severity="medium",
                category="best_practice",
                message="apt-get install should use --no-install-recommends",
                suggestion="Add --no-install-recommends to reduce image size",
                resource="RUN"
            ))

        if "USER" not in dockerfile:
            issues.append(IaCIssue(
                severity="high",
                category="security",
                message="Container runs as root",
                suggestion="Add USER directive to run as non-root",
                resource="USER"
            ))

        if "EXPOSE" not in dockerfile:
            issues.append(IaCIssue(
                severity="low",
                category="best_practice",
                message="No EXPOSE directive",
                suggestion="Document exposed ports with EXPOSE",
                resource="EXPOSE"
            ))

        # Multi-stage builds check
        if "FROM" in dockerfile:
            from_count = dockerfile.count("FROM ")
            if from_count < 2 and ("COPY" in dockerfile and "build" in dockerfile.lower()):
                issues.append(IaCIssue(
                    severity="medium",
                    category="best_practice",
                    message="Consider using multi-stage build",
                    suggestion="Use multiple FROM stages to reduce final image size",
                    resource="Build"
                ))

        if ".git" not in dockerfile and ".git" in str(lines):
            issues.append(IaCIssue(
                severity="medium",
                category="best_practice",
                message="No .dockerignore excludes",
                suggestion="Create .dockerignore to exclude unnecessary files",
                resource=".dockerignore"
            ))

        severity_count = self._count_severities(issues)

        return {
            "format": "dockerfile",
            "quality_score": self._calculate_quality_score(issues),
            "issues": [self._issue_to_dict(i) for i in issues],
            "severity_count": severity_count,
            "line_count": len(lines),
            "recommendations": self._generate_iac_recommendations(issues),
        }

    def validate_kubernetes(self, manifest: str) -> Dict[str, Any]:
        """
        Validate Kubernetes manifest YAML.

        Args:
            manifest: Kubernetes manifest

        Returns:
            Validation results
        """
        issues: List[IaCIssue] = []

        try:
            # Try to parse YAML
            config = yaml.safe_load(manifest)
            if not config:
                config = {}
        except Exception as e:  # TODO (2026-03-08): specify exception type
            config = {}

        # Security checks
        if "securityContext" not in str(config):
            issues.append(IaCIssue(
                severity="high",
                category="security",
                message="No securityContext defined",
                suggestion="Add securityContext with runAsNonRoot: true",
                resource="securityContext"
            ))

        if "resources" not in str(config) or "limits" not in str(config):
            issues.append(IaCIssue(
                severity="high",
                category="best_practice",
                message="No resource limits defined",
                suggestion="Define CPU and memory requests/limits",
                resource="resources"
            ))

        if "livenessProbe" not in str(config):
            issues.append(IaCIssue(
                severity="medium",
                category="best_practice",
                message="No liveness probe defined",
                suggestion="Add livenessProbe for pod health checks",
                resource="livenessProbe"
            ))

        if "readinessProbe" not in str(config):
            issues.append(IaCIssue(
                severity="medium",
                category="best_practice",
                message="No readiness probe defined",
                suggestion="Add readinessProbe for traffic control",
                resource="readinessProbe"
            ))

        severity_count = self._count_severities(issues)

        return {
            "format": "kubernetes",
            "quality_score": self._calculate_quality_score(issues),
            "issues": [self._issue_to_dict(i) for i in issues],
            "severity_count": severity_count,
            "recommendations": self._generate_iac_recommendations(issues),
        }

    def _count_severities(self, issues: List[IaCIssue]) -> Dict[str, int]:
        """Count issues by severity."""
        return {
            "critical": len([i for i in issues if i.severity == "critical"]),
            "high": len([i for i in issues if i.severity == "high"]),
            "medium": len([i for i in issues if i.severity == "medium"]),
            "low": len([i for i in issues if i.severity == "low"]),
        }

    def _calculate_quality_score(self, issues: List[IaCIssue]) -> float:
        """Calculate quality score based on issues."""
        if not issues:
            return 100.0

        severity_weights = {"critical": 50, "high": 25, "medium": 10, "low": 5}
        total_deduction = sum(severity_weights.get(i.severity, 0) for i in issues)
        return max(0.0, 100.0 - total_deduction)

    def _generate_iac_recommendations(self, issues: List[IaCIssue]) -> List[str]:
        """Generate recommendations."""
        recommendations = []

        if any(i.severity == "critical" for i in issues):
            recommendations.append("🔴 Critical issues found - address before deployment")

        if any(i.category == "security" for i in issues):
            recommendations.append("🔒 Review security configurations")

        if any(i.category == "cost" for i in issues):
            recommendations.append("💰 Optimize costs with suggested changes")

        if not recommendations:
            recommendations.append("✅ Configuration looks good")

        return recommendations

    def _issue_to_dict(self, issue: IaCIssue) -> Dict:
        """Convert issue to dictionary."""
        return {
            "severity": issue.severity,
            "category": issue.category,
            "message": issue.message,
            "suggestion": issue.suggestion,
            "resource": issue.resource,
        }


# Global validator instance
_validator_instance: Optional[IaCValidator] = None


def get_iac_validator() -> IaCValidator:
    """Get or create global IaC validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = IaCValidator()
    return _validator_instance
