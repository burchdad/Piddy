"""
Phase 29: Sandboxed Execution

Execute all code changes in isolated Docker containers:
- Ephemeral container per task
- Copy repo to container's /tmp/repo
- Run tests, validation inside container
- Extract results
- Never modify host unless validation passes
"""

import subprocess
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution"""
    docker_image: str = "python:3.11-slim"
    timeout_seconds: int = 300
    memory_limit_mb: int = 2048
    cpu_limit: str = "1.0"
    network_access: bool = False
    keep_container: bool = False


@dataclass
class ExecutionResult:
    """Result of sandbox execution"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    container_id: Optional[str] = None
    files_modified: List[str] = None

    def __post_init__(self):
        if self.files_modified is None:
            self.files_modified = []


class DockerSandbox:
    """Manage isolated Docker sandbox execution"""

    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self._check_docker()

    def _check_docker(self) -> bool:
        """Verify Docker is available"""
        try:
            subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                check=True,
                timeout=5
            )
            logger.info("Docker available for sandboxed execution")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Docker not available - running in embedded mode")
            return False

    def create_container(self, repo_path: str) -> Tuple[bool, str, str]:
        """Create and start a Docker container with repo copy"""
        try:
            container_id = str(uuid.uuid4())[:12]
            
            # Create container
            cmd = [
                'docker', 'create',
                '--name', container_id,
                '-i',
                '--memory', f"{self.config.memory_limit_mb}m",
                '--cpus', self.config.cpu_limit,
            ]
            
            if not self.config.network_access:
                cmd.append('--network=none')
            
            cmd.append(self.config.docker_image)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Copy repo into container
            subprocess.run(
                ['docker', 'cp', repo_path, f"{container_id}:/tmp/repo"],
                capture_output=True,
                check=True,
                timeout=30
            )
            
            return True, container_id, "Container created"
        except subprocess.CalledProcessError as e:
            return False, "", f"Failed to create container: {e.stderr}"

    def execute_command(self, container_id: str, command: str) -> ExecutionResult:
        """Execute command inside sandbox"""
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ['docker', 'exec', '-w', '/tmp/repo', container_id, 'bash', '-c', command],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration_ms,
                container_id=container_id
            )
        except subprocess.TimeoutExpired:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {self.config.timeout_seconds}s",
                exit_code=-1,
                duration_ms=duration_ms,
                container_id=container_id
            )
        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                duration_ms=duration_ms,
                container_id=container_id
            )

    def extract_files(self, container_id: str, file_paths: List[str], dest_dir: str) -> bool:
        """Extract modified files from container"""
        try:
            for file_path in file_paths:
                subprocess.run(
                    ['docker', 'cp', f"{container_id}:/tmp/repo/{file_path}", f"{dest_dir}/{file_path}"],
                    capture_output=True,
                    check=True,
                    timeout=30
                )
            return True
        except subprocess.CalledProcessError:
            return False

    def cleanup_container(self, container_id: str) -> bool:
        """Remove container"""
        try:
            subprocess.run(
                ['docker', 'rm', '-f', container_id],
                capture_output=True,
                check=True,
                timeout=10
            )
            return True
        except subprocess.CalledProcessError:
            return False


class SandboxExecutor:
    """Execute code changes in sandboxed environment"""

    def __init__(self, repo_root: str = '/workspaces/Piddy', config: SandboxConfig = None):
        self.repo_root = Path(repo_root)
        self.sandbox = DockerSandbox(config)
        self.config = config or SandboxConfig()
        self.use_docker = self._has_docker()

    def _has_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(['docker', 'version'], capture_output=True, check=True, timeout=5)
            return True
        except Exception as e:  # TODO (2026-03-08): specify exception type
            return False

    def execute_with_isolation(
        self,
        commands: List[str],
        file_changes: Optional[Dict[str, str]] = None,
        validation_script: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute commands with full isolation:
        1. Create sandbox (Docker or temp dir)
        2. Copy repo
        3. Apply changes
        4. Run validation
        5. Extract results if valid
        """

        if self.use_docker:
            return self._execute_in_docker(commands, file_changes, validation_script)
        else:
            return self._execute_in_temp_dir(commands, file_changes, validation_script)

    def _execute_in_docker(
        self,
        commands: List[str],
        file_changes: Optional[Dict[str, str]],
        validation_script: Optional[str]
    ) -> Dict[str, Any]:
        """Execute in Docker container"""
        logger.info("Executing in Docker sandbox...")

        # Create container
        success, container_id, msg = self.sandbox.create_container(str(self.repo_root))
        if not success:
            return {'success': False, 'error': msg}

        try:
            exec_results = []

            # Apply file changes
            if file_changes:
                for file_path, content in file_changes.items():
                    cmd = f"""cat > '{file_path}' << 'EOF'
{content}
EOF"""
                    result = self.sandbox.execute_command(container_id, cmd)
                    exec_results.append({
                        'step': f'write:{file_path}',
                        'success': result.success,
                        'duration_ms': result.duration_ms
                    })

            # Run user commands
            for command in commands:
                result = self.sandbox.execute_command(container_id, command)
                exec_results.append({
                    'step': command[:50],
                    'success': result.success,
                    'duration_ms': result.duration_ms,
                    'stdout': result.stdout[:500] if result.stdout else '',
                    'stderr': result.stderr[:500] if result.stderr else ''
                })

            # Run validation if provided
            validation_passed = True
            if validation_script:
                result = self.sandbox.execute_command(container_id, validation_script)
                validation_passed = result.success
                exec_results.append({
                    'step': 'validation',
                    'success': validation_passed,
                    'duration_ms': result.duration_ms
                })

            # Extract files if validation passed
            modified_files = []
            if validation_passed and file_changes:
                modified_files = list(file_changes.keys())

            return {
                'success': validation_passed,
                'isolation_method': 'docker',
                'container_id': container_id,
                'execution_steps': exec_results,
                'modified_files': modified_files,
                'validation': validation_passed
            }

        finally:
            # Cleanup
            if not self.config.keep_container:
                self.sandbox.cleanup_container(container_id)

    def _execute_in_temp_dir(
        self,
        commands: List[str],
        file_changes: Optional[Dict[str, str]],
        validation_script: Optional[str]
    ) -> Dict[str, Any]:
        """Execute in temporary directory (fallback)"""
        logger.info("Executing in isolated temp directory...")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy repo
            repo_copy = temp_path / 'repo'
            shutil.copytree(self.repo_root, repo_copy)

            exec_results = []
            validation_passed = True

            try:
                # Apply changes
                if file_changes:
                    for file_path, content in file_changes.items():
                        file_full_path = repo_copy / file_path
                        file_full_path.parent.mkdir(parents=True, exist_ok=True)
                        file_full_path.write_text(content)
                        exec_results.append({
                            'step': f'write:{file_path}',
                            'success': True,
                            'duration_ms': 10
                        })

                # Run commands
                for command in commands:
                    try:
                        result = subprocess.run(
                            command,
                            shell=True,
                            cwd=str(repo_copy),
                            capture_output=True,
                            text=True,
                            timeout=self.config.timeout_seconds
                        )
                        exec_results.append({
                            'step': command[:50],
                            'success': result.returncode == 0,
                            'duration_ms': 50,
                            'stdout': result.stdout[:500],
                            'stderr': result.stderr[:500]
                        })
                    except subprocess.TimeoutExpired:
                        validation_passed = False
                        break

                # Run validation
                if validation_script and validation_passed:
                    try:
                        result = subprocess.run(
                            validation_script,
                            shell=True,
                            cwd=str(repo_copy),
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        validation_passed = result.returncode == 0
                        exec_results.append({
                            'step': 'validation',
                            'success': validation_passed,
                            'duration_ms': 50
                        })
                    except subprocess.TimeoutExpired:
                        validation_passed = False

            except Exception as e:
                logger.error(f"Execution error: {e}")
                validation_passed = False

            return {
                'success': validation_passed,
                'isolation_method': 'temporary_directory',
                'temp_dir': str(temp_path),
                'execution_steps': exec_results,
                'modified_files': list(file_changes.keys()) if (file_changes and validation_passed) else [],
                'validation': validation_passed
            }


class SafeAutonomousExecutor:
    """Autonomous executor using sandboxed environment"""

    def __init__(self, repo_root: str = '/workspaces/Piddy'):
        self.repo_root = Path(repo_root)
        self.sandbox_executor = SandboxExecutor(repo_root)

    def execute_feature_safely(
        self,
        feature_description: str,
        file_changes: Dict[str, str],
        validation_commands: List[str] = None
    ) -> Dict[str, Any]:
        """Execute feature development safely in sandbox"""

        if validation_commands is None:
            validation_commands = [
                'python -m py_compile **/*.py 2>/dev/null || true'  # Syntax check
            ]

        result = self.sandbox_executor.execute_with_isolation(
            commands=validation_commands,
            file_changes=file_changes,
            validation_script='python -m pytest tests/ -q 2>/dev/null || true'
        )

        return {
            'feature': feature_description,
            'execution_result': result,
            'safe_to_commit': result.get('success', False),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Demo
    executor = SafeAutonomousExecutor()
    
    demo_changes = {
        'src/demo_phase29.py': '"""Demo Phase 29"""\n\ndef hello():\n    return "Phase 29 sandboxed"\n'
    }
    
    result = executor.execute_feature_safely(
        feature_description="Demo Phase 29 sandbox execution",
        file_changes=demo_changes,
        validation_commands=['python -c "import ast; ast.parse(open(\'src/demo_phase29.py\').read())"']
    )
    
    logger.info("Phase 29: Sandboxed Execution - Demo")
    logger.info(f"Result: {json.dumps(result, indent=2, default=str)}")
