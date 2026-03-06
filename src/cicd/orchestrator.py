"""
Advanced CI/CD integration for Phase 4.
Integrates with GitHub Actions, GitLab CI, Jenkins, and other CI/CD platforms.
"""
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hmac
import hashlib

logger = logging.getLogger(__name__)


class CIPlatform(str, Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"
    TRAVIS_CI = "travis_ci"
    AZURE_PIPELINES = "azure_pipelines"


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class PipelineRun:
    """CI/CD pipeline execution record."""
    id: str
    workflow_name: str
    platform: CIPlatform
    branch: str
    commit_sha: str
    status: PipelineStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    jobs: List[Dict[str, Any]] = None
    artifacts: List[Dict[str, Any]] = None
    error_logs: Optional[str] = None

    def __post_init__(self):
        if self.jobs is None:
            self.jobs = []
        if self.artifacts is None:
            self.artifacts = []


@dataclass
class BuildArtifact:
    """Build artifact from CI/CD pipeline."""
    id: str
    name: str
    path: str
    size_bytes: int
    mime_type: str
    created_at: str
    download_url: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestResult:
    """Test execution result."""
    test_id: str
    name: str
    status: TestStatus
    duration_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    logs: Optional[str] = None


class GitHubActionsIntegration:
    """GitHub Actions CI/CD integration."""

    def __init__(self, repo_owner: str, repo_name: str, github_token: str):
        """Initialize GitHub Actions integration."""
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_workflow_runs(
        self,
        workflow_id: str,
        status: str = "all",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get workflow runs for a specific workflow.

        Args:
            workflow_id: Workflow ID or filename
            status: Filter by status (all, completed, action_required, cancelled, failure, neutral, skipped, stale, success, timed_out, in_progress, queued, requested, waiting)
            limit: Number of runs to fetch

        Returns:
            List of workflow runs
        """
        try:
            url = f"{self.base_url}/actions/workflows/{workflow_id}/runs"
            params = {"status": status, "per_page": limit}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            runs = response.json()["workflow_runs"]
            logger.info(f"✅ Retrieved {len(runs)} GitHub Actions workflow runs")
            return runs
        except Exception as e:
            logger.error(f"Failed to get GitHub Actions runs: {e}")
            return []

    def trigger_workflow(
        self,
        workflow_id: str,
        branch: str = "main",
        inputs: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Trigger a GitHub Actions workflow.

        Args:
            workflow_id: Workflow ID or filename
            branch: Branch to run workflow on
            inputs: Workflow inputs

        Returns:
            True if trigger successful
        """
        try:
            url = f"{self.base_url}/actions/workflows/{workflow_id}/dispatches"
            data = {"ref": branch}
            if inputs:
                data["inputs"] = inputs

            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()

            logger.info(f"✅ Triggered GitHub Actions workflow: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to trigger GitHub Actions workflow: {e}")
            return False

    def get_run_logs(self, run_id: int) -> str:
        """Get logs for a specific workflow run."""
        try:
            url = f"{self.base_url}/actions/runs/{run_id}/logs"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            # Logs are returned as zip, decode or save as needed
            return response.content
        except Exception as e:
            logger.error(f"Failed to get run logs: {e}")
            return ""

    def cancel_run(self, run_id: int) -> bool:
        """Cancel a workflow run."""
        try:
            url = f"{self.base_url}/actions/runs/{run_id}/cancel"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()

            logger.info(f"✅ Cancelled GitHub Actions run: {run_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel run: {e}")
            return False


class JenkinsIntegration:
    """Jenkins CI/CD integration."""

    def __init__(self, jenkins_url: str, username: str, api_token: str):
        """Initialize Jenkins integration."""
        self.jenkins_url = jenkins_url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.auth = (username, api_token)

    def get_job_builds(self, job_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get build history for a Jenkins job."""
        try:
            url = f"{self.jenkins_url}/job/{job_name}/api/json"
            response = requests.get(url, auth=self.auth, params={"tree": f"builds[*]{{number,status,timestamp,duration,result}}{{{limit}}}"})
            response.raise_for_status()

            builds = response.json()["builds"]
            logger.info(f"✅ Retrieved {len(builds)} Jenkins builds for {job_name}")
            return builds
        except Exception as e:
            logger.error(f"Failed to get Jenkins builds: {e}")
            return []

    def trigger_build(
        self,
        job_name: str,
        parameters: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Trigger a Jenkins job build.

        Args:
            job_name: Jenkins job name
            parameters: Build parameters

        Returns:
            True if trigger successful
        """
        try:
            if parameters:
                url = f"{self.jenkins_url}/job/{job_name}/buildWithParameters"
                response = requests.post(url, auth=self.auth, data=parameters)
            else:
                url = f"{self.jenkins_url}/job/{job_name}/build"
                response = requests.post(url, auth=self.auth)

            response.raise_for_status()
            logger.info(f"✅ Triggered Jenkins build: {job_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to trigger Jenkins build: {e}")
            return False

    def get_build_log(self, job_name: str, build_number: int) -> str:
        """Get console output for a specific build."""
        try:
            url = f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()

            return response.text
        except Exception as e:
            logger.error(f"Failed to get build log: {e}")
            return ""


class CICDOrchestrator:
    """
    Central orchestrator for multi-platform CI/CD coordination.
    Manages pipelines across different CI/CD providers.
    """

    def __init__(self):
        """Initialize CI/CD orchestrator."""
        self.pipelines: Dict[str, PipelineRun] = {}
        self.integrations: Dict[CIPlatform, Any] = {}
        self.pipeline_history: List[Dict[str, Any]] = []
        logger.info("✅ CI/CD Orchestrator initialized")

    def register_github_actions(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: str,
    ) -> None:
        """Register GitHub Actions integration."""
        integration = GitHubActionsIntegration(repo_owner, repo_name, github_token)
        self.integrations[CIPlatform.GITHUB_ACTIONS] = integration
        logger.info("✅ GitHub Actions integration registered")

    def register_jenkins(
        self,
        jenkins_url: str,
        username: str,
        api_token: str,
    ) -> None:
        """Register Jenkins integration."""
        integration = JenkinsIntegration(jenkins_url, username, api_token)
        self.integrations[CIPlatform.JENKINS] = integration
        logger.info("✅ Jenkins integration registered")

    def trigger_pipeline(
        self,
        platform: CIPlatform,
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Trigger a pipeline on specified platform.

        Args:
            platform: CI/CD platform
            job_name: Job/workflow name
            parameters: Job parameters

        Returns:
            True if trigger successful
        """
        if platform not in self.integrations:
            logger.error(f"Platform not registered: {platform}")
            return False

        integration = self.integrations[platform]

        if platform == CIPlatform.GITHUB_ACTIONS:
            success = integration.trigger_workflow(
                job_name,
                branch="main",
                inputs=parameters,
            )
        elif platform == CIPlatform.JENKINS:
            success = integration.trigger_build(job_name, parameters=parameters)
        else:
            logger.error(f"Trigger not implemented for platform: {platform}")
            return False

        if success:
            logger.info(f"✅ Pipeline triggered on {platform.value}: {job_name}")

        return success

    def get_pipeline_status(
        self,
        platform: CIPlatform,
        pipeline_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific pipeline run.

        Args:
            platform: CI/CD platform
            pipeline_id: Pipeline/run ID

        Returns:
            Pipeline status information
        """
        if pipeline_id in self.pipelines:
            return asdict(self.pipelines[pipeline_id])

        # Could fetch from integration if needed
        return None

    def get_build_metrics(self, platform: CIPlatform = None) -> Dict[str, Any]:
        """
        Get build metrics and statistics.

        Args:
            platform: Specific platform, or None for all

        Returns:
            Build metrics
        """
        if platform is None:
            all_runs = list(self.pipelines.values())
        else:
            all_runs = [p for p in self.pipelines.values() if p.platform == platform]

        if not all_runs:
            return {
                "total_builds": 0,
                "success": 0,
                "failure": 0,
                "success_rate": 0,
            }

        success = len([p for p in all_runs if p.status == PipelineStatus.SUCCESS])
        failure = len([p for p in all_runs if p.status == PipelineStatus.FAILURE])
        total = len(all_runs)

        return {
            "total_builds": total,
            "success": success,
            "failure": failure,
            "cancelled": len([p for p in all_runs if p.status == PipelineStatus.CANCELLED]),
            "success_rate": (success / total * 100) if total > 0 else 0,
            "average_duration_seconds": (
                sum(p.duration_seconds or 0 for p in all_runs) / total if total > 0 else 0
            ),
        }

    def verify_webhook_signature(
        self,
        platform: CIPlatform,
        payload: str,
        signature: str,
        secret: str,
    ) -> bool:
        """
        Verify webhook signature from CI/CD provider.

        Args:
            platform: CI/CD platform
            payload: Request payload
            signature: Provided signature
            secret: Webhook secret

        Returns:
            True if signature is valid
        """
        if platform == CIPlatform.GITHUB_ACTIONS:
            # GitHub uses SHA256
            expected = "sha256=" + hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        elif platform == CIPlatform.GITLAB_CI:
            # GitLab uses SHA256
            expected = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        # Add other platforms as needed

        return False

    def handle_webhook(
        self,
        platform: CIPlatform,
        event_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Handle webhook event from CI/CD provider.

        Args:
            platform: Platform sending webhook
            event_type: Type of event
            payload: Event payload

        Returns:
            True if handled successfully
        """
        try:
            logger.info(f"🔔 Webhook received: {platform.value} - {event_type}")

            # Create pipeline run record
            pipeline_id = payload.get("id", payload.get("build_id", "unknown"))
            if isinstance(pipeline_id, dict):
                pipeline_id = payload.get("workflow_run", {}).get("id", "unknown")

            pipeline_run = PipelineRun(
                id=str(pipeline_id),
                workflow_name=payload.get("workflow", payload.get("name", "unknown")),
                platform=platform,
                branch=payload.get("ref", payload.get("branch", "unknown")).replace("refs/heads/", ""),
                commit_sha=payload.get("head_commit", {}).get("id", payload.get("commit", "unknown")),
                status=self._parse_status(payload.get("status", "pending")),
                created_at=datetime.now().isoformat(),
            )

            self.pipelines[pipeline_run.id] = pipeline_run
            self.pipeline_history.append(asdict(pipeline_run))

            logger.info(f"✅ Pipeline recorded: {pipeline_run.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False

    def _parse_status(self, status_str: str) -> PipelineStatus:
        """Parse status string to PipelineStatus enum."""
        status_map = {
            "completed": PipelineStatus.SUCCESS,
            "success": PipelineStatus.SUCCESS,
            "passed": PipelineStatus.SUCCESS,
            "failed": PipelineStatus.FAILURE,
            "failure": PipelineStatus.FAILURE,
            "running": PipelineStatus.RUNNING,
            "in_progress": PipelineStatus.RUNNING,
            "pending": PipelineStatus.PENDING,
            "cancelled": PipelineStatus.CANCELLED,
            "skipped": PipelineStatus.SKIPPED,
        }
        return status_map.get(status_str.lower(), PipelineStatus.PENDING)

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "registered_platforms": [p.value for p in self.integrations.keys()],
            "total_pipelines": len(self.pipelines),
            "metrics": self.get_build_metrics(),
            "recent_runs": [asdict(p) for p in list(self.pipelines.values())[-5:]],
        }


# Global orchestrator instance
_orchestrator_instance: Optional[CICDOrchestrator] = None


def get_cicd_orchestrator() -> CICDOrchestrator:
    """Get or create global CI/CD orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CICDOrchestrator()
    return _orchestrator_instance
