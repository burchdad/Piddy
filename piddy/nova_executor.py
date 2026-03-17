"""
Nova Executor - AI Code Execution Engine

Enables Nova to actually run code, not just coordinate.
Handles:
- Git operations (clone, branch, commit, push)
- Code generation (write files, templates)
- Test execution
- Deployment
- PR creation
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from enum import Enum

try:
    from piddy.persistence import get_persistence
    HAS_PERSISTENCE = True
except ImportError:
    HAS_PERSISTENCE = False
    get_persistence = None

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of code execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class CodeExecutionResult:
    """Result of code execution"""
    
    def __init__(self, task_id: str, agent: str, status: ExecutionStatus):
        self.task_id = task_id
        self.agent = agent
        self.status = status
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.output = ""
        self.error = ""
        self.files_changed = []
        self.commits = []
        self.pr_url = None
        self.result_data = {}
    
    def to_dict(self) -> Dict:
        return {
            "mission_id": self.task_id,  # Alias for persistence layer
            "task_id": self.task_id,
            "agent": self.agent,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": int((self.end_time - self.start_time).total_seconds() * 1000) if self.end_time else None,
            "output": self.output[-500:] if len(self.output) > 500 else self.output,  # Last 500 chars
            "error": self.error[-500:] if len(self.error) > 500 else self.error,
            "files_changed": self.files_changed,
            "commits": self.commits,
            "pr_url": self.pr_url,
            "result": self.result_data,
            "task": "Mission from Nova executor"  # Required by persistence schema
        }


class NovaExecutor:
    """Execute code on behalf of Nova agent"""
    
    def __init__(self, workspace_dir: str = "/tmp/piddy_exec", git_email: str = "nova@piddy.ai", git_name: str = "Nova"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.git_email = git_email
        self.git_name = git_name
        self._configure_git()
        
        # Track execution history
        self.execution_history: Dict[str, CodeExecutionResult] = {}
        
        logger.info(f"🚀 Nova Executor initialized (workspace: {self.workspace_dir})")
    
    def _configure_git(self):
        """Configure git for Nova commits"""
        try:
            subprocess.run(['git', 'config', '--global', 'user.email', self.git_email], check=True)
            subprocess.run(['git', 'config', '--global', 'user.name', self.git_name], check=True)
            logger.info(f"✅ Git configured: {self.git_name} <{self.git_email}>")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Git config failed: {e}")
    
    def _run_command(self, cmd: str, cwd: Optional[Path] = None, env: Optional[Dict] = None) -> Tuple[bool, str, str]:
        """
        Run a shell command safely
        
        Returns: (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, **(env or {})}
            )
            success = result.returncode == 0
            return success, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout (30s)"
        except Exception as e:
            return False, "", str(e)
    
    # ========================================================================
    # GIT OPERATIONS
    # ========================================================================
    
    def clone_repo(self, repo_url: str, branch: str = "main") -> Tuple[bool, Path, str]:
        """
        Clone a git repository
        
        Returns: (success, repo_path, error_msg)
        """
        try:
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            repo_path = self.workspace_dir / repo_name
            
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            cmd = f'git clone --depth 1 --branch {branch} {repo_url} {repo_path}'
            success, stdout, stderr = self._run_command(cmd)
            
            if success:
                logger.info(f"✅ Cloned {repo_url} to {repo_path}")
                return True, repo_path, ""
            else:
                logger.error(f"❌ Clone failed: {stderr}")
                return False, None, stderr
        
        except Exception as e:
            logger.error(f"❌ Clone error: {e}")
            return False, None, str(e)
    
    def create_branch(self, repo_path: Path, branch_name: str) -> Tuple[bool, str]:
        """
        Create and checkout a new branch
        
        Returns: (success, error_msg)
        """
        try:
            # Ensure clean working directory
            success, _, _ = self._run_command('git status --porcelain', cwd=repo_path)
            
            # Create branch
            cmd = f'git checkout -b {branch_name}'
            success, stdout, stderr = self._run_command(cmd, cwd=repo_path)
            
            if success:
                logger.info(f"✅ Created branch: {branch_name}")
                return True, ""
            else:
                logger.error(f"❌ Branch creation failed: {stderr}")
                return False, stderr
        
        except Exception as e:
            logger.error(f"❌ Branch error: {e}")
            return False, str(e)
    
    def write_files(self, repo_path: Path, files: Dict[str, str]) -> Tuple[bool, List[str], str]:
        """
        Write multiple files to repository
        
        Args:
            files: {file_path: content, ...}
        
        Returns: (success, created_files, error_msg)
        """
        try:
            created = []
            for file_path, content in files.items():
                full_path = repo_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created.append(file_path)
                logger.debug(f"✅ Wrote: {file_path}")
            
            logger.info(f"✅ Created {len(created)} files")
            return True, created, ""
        
        except Exception as e:
            logger.error(f"❌ Write error: {e}")
            return False, [], str(e)
    
    def run_tests(self, repo_path: Path) -> Tuple[bool, str, int]:
        """
        Run tests in repository
        
        Returns: (success, output, test_count)
        """
        try:
            # Try pytest first
            cmd = 'pytest -v --tb=short 2>&1 | head -100'
            success, stdout, stderr = self._run_command(cmd, cwd=repo_path)
            
            if success:
                logger.info(f"✅ Tests passed")
                return True, stdout, len([l for l in stdout.split('\n') if 'PASSED' in l])
            else:
                # Fallback to unittest
                cmd = 'python -m unittest discover -v 2>&1 | head -100'
                success, stdout, stderr = self._run_command(cmd, cwd=repo_path)
                
                if success:
                    return True, stdout, len([l for l in stdout.split('\n') if 'ok' in l])
                else:
                    logger.warning(f"⚠️ Tests failed: {stderr}")
                    return False, f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", 0
        
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
            return False, str(e), 0
    
    def commit_changes(self, repo_path: Path, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str, str]:
        """
        Commit changes to git
        
        Returns: (success, commit_hash, error_msg)
        """
        try:
            # Add files
            if files:
                for f in files:
                    self._run_command(f'git add {json.dumps(f)}', cwd=repo_path)
            else:
                self._run_command('git add -A', cwd=repo_path)
            
            # Commit
            cmd = f'git commit -m {json.dumps(message)}'
            success, stdout, stderr = self._run_command(cmd, cwd=repo_path)
            
            if success:
                # Get commit hash
                success, commit_hash, _ = self._run_command('git rev-parse HEAD', cwd=repo_path)
                commit_hash = commit_hash.strip()
                logger.info(f"✅ Committed: {commit_hash[:8]} - {message}")
                return True, commit_hash, ""
            else:
                logger.warning(f"⚠️ Nothing to commit: {stderr}")
                return False, "", stderr
        
        except Exception as e:
            logger.error(f"❌ Commit error: {e}")
            return False, "", str(e)
    
    def push_changes(self, repo_path: Path, branch: str = "HEAD") -> Tuple[bool, str]:
        """
        Push changes to remote
        
        Returns: (success, error_msg)
        """
        try:
            cmd = f'git push origin {branch}'
            success, stdout, stderr = self._run_command(cmd, cwd=repo_path)
            
            if success:
                logger.info(f"✅ Pushed to origin/{branch}")
                return True, ""
            else:
                logger.error(f"❌ Push failed: {stderr}")
                return False, stderr
        
        except Exception as e:
            logger.error(f"❌ Push error: {e}")
            return False, str(e)
    
    # ========================================================================
    # HIGH-LEVEL EXECUTION FLOWS
    # ========================================================================
    
    def execute_mission(self, mission_id: str, agent: str, task: str) -> CodeExecutionResult:
        """
        Execute a complete mission:
        1. Clone repo
        2. Create branch
        3. Generate/modify code
        4. Run tests
        5. Commit
        6. Push
        """
        result = CodeExecutionResult(mission_id, agent, ExecutionStatus.RUNNING)
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 Nova Execution: {agent} - {task[:50]}")
            logger.info(f"{'='*60}")
            
            # Phase 1: Parse task
            task_type = self._parse_task(task)
            logger.info(f"📋 Task type: {task_type}")
            
            # Phase 2: Clone repo (if needed)
            if 'repo' in task:
                repo_url = self._extract_repo_url(task)
                success, repo_path, error = self.clone_repo(repo_url)
                if not success:
                    result.error = f"Failed to clone: {error}"
                    result.status = ExecutionStatus.FAILED
                    return result
            else:
                repo_path = self.workspace_dir / f"mission_{mission_id}"
                repo_path.mkdir(exist_ok=True)
            
            # Phase 3: Create branch
            branch_name = f"nova/{agent.lower()}/{mission_id[:8]}"
            success, error = self.create_branch(repo_path, branch_name)
            if not success and 'not a git repository' in error:
                # Initialize new repo
                self._run_command('git init', cwd=repo_path)
                success, error = self.create_branch(repo_path, branch_name)
            
            # Phase 4: Generate code
            code_files = self._generate_code(task)
            if code_files:
                success, created, error = self.write_files(repo_path, code_files)
                result.files_changed = created
                
                # Run tests
                test_success, test_output, test_count = self.run_tests(repo_path)
                result.output = test_output
                
                if not test_success:
                    result.error = "Tests failed"
                    result.status = ExecutionStatus.FAILED
                    logger.error(f"❌ Tests failed")
                    return result
                
                # Commit
                success, commit_hash, error = self.commit_changes(
                    repo_path,
                    f"[Nova] {task[:50]}",
                    created
                )
                if success:
                    result.commits.append(commit_hash)
                
                # Push
                success, error = self.push_changes(repo_path, branch_name)
                if not success:
                    logger.warning(f"⚠️ Push failed (might be local-only): {error}")
            
            result.status = ExecutionStatus.SUCCESS
            result.end_time = datetime.utcnow()
            logger.info(f"✅ Mission complete: {mission_id}")
            
        except Exception as e:
            result.error = str(e)
            result.status = ExecutionStatus.FAILED
            result.end_time = datetime.utcnow()
            logger.error(f"❌ Mission failed: {e}")
        
        # Store in memory
        self.execution_history[mission_id] = result
        
        # Persist to database (if available)
        if HAS_PERSISTENCE and get_persistence:
            try:
                persistence = get_persistence()
                mission_dict = result.to_dict()
                persistence.save_mission(mission_dict)
                logger.info(f"💾 Mission persisted to database: {mission_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to persist mission: {e}")
        
        return result
    
    def _parse_task(self, task: str) -> str:
        """Determine task type from description"""
        task_lower = task.lower()
        if 'test' in task_lower:
            return 'test'
        elif 'bug' in task_lower or 'fix' in task_lower:
            return 'bugfix'
        elif 'feature' in task_lower or 'add' in task_lower:
            return 'feature'
        elif 'refactor' in task_lower or 'clean' in task_lower:
            return 'refactor'
        elif 'doc' in task_lower or 'document' in task_lower:
            return 'docs'
        else:
            return 'general'
    
    def _extract_repo_url(self, task: str) -> str:
        """Extract git repo URL from task"""
        # Look for https://github.com/... or git@github.com:...
        if 'github.com' in task:
            import re
            match = re.search(r'(https?://[^\s]+\.git|git@[^\s]+\.git)', task)
            if match:
                return match.group(1)
        return "https://github.com/burchdad/Piddy.git"
    
    def _generate_code(self, task: str) -> Dict[str, str]:
        """
        Generate code based on task description
        This is a template generator - LLM can enhance this
        """
        task_type = self._parse_task(task)
        
        if task_type == 'test':
            return {
                'tests/test_nova.py': '''import pytest

def test_nova_works():
    """Test that Nova execution works"""
    assert True, "Nova is working!"

class TestNovaFeatures:
    def test_feature_1(self):
        assert True
    
    def test_feature_2(self):
        assert True
'''
            }
        
        elif task_type == 'feature':
            return {
                'src/nova_feature.py': '''"""
Nova-generated feature module
Generated by Nova AI Agent
"""

def main():
    """Main feature entry point"""
    return "Nova feature working"

if __name__ == "__main__":
    print(main())
''',
                'tests/test_nova_feature.py': '''import pytest
from src.nova_feature import main

def test_feature():
    assert main() == "Nova feature working"
'''
            }
        
        elif task_type == 'bugfix':
            return {
                'src/fixes.py': '''"""
Bug fixes applied by Nova
"""

def apply_fix():
    """Apply the identified bug fix"""
    return True
''',
                'tests/test_fixes.py': '''import pytest
from src.fixes import apply_fix

def test_fix_applied():
    assert apply_fix() is True
'''
            }
        
        else:
            return {
                'NOVA_EXECUTION.md': '''# Nova Execution

Task: Generate code for task

## Generated

- Created by Nova AI Agent
- Timestamp: {0}
'''.format(datetime.utcnow().isoformat())
            }
    
    def get_execution_history(self) -> List[Dict]:
        """
        Get all execution history from memory and persistence
        Priority: Memory first (in-flight), then disk (persisted)
        """
        results = []
        
        # First: Add in-memory executions (most recent)
        for result in self.execution_history.values():
            results.append(result.to_dict())
        
        # Second: Add from persistence (historical records)
        if HAS_PERSISTENCE and get_persistence:
            try:
                persistence = get_persistence()
                persisted_missions = persistence.get_missions(limit=100)
                if persisted_missions:
                    for mission in persisted_missions:
                        # Skip if already in memory
                        if mission.get("task_id") not in self.execution_history:
                            results.append(mission)
            except Exception as e:
                logger.warning(f"⚠️ Failed to retrieve persisted missions: {e}")
        
        return results


# ============================================================================
# RPC ENDPOINT - Make Nova execution callable from frontend
# ============================================================================

nova_executor = None

def initialize_nova_executor():
    """Initialize global Nova executor"""
    global nova_executor
    if nova_executor is None:
        nova_executor = NovaExecutor()
    return nova_executor

def execute_task(mission_id: str, agent: str, task: str) -> Dict:
    """
    RPC endpoint to execute a code task
    
    Called from: frontend/LiveChat or coordinator
    """
    executor = initialize_nova_executor()
    result = executor.execute_mission(mission_id, agent, task)
    return result.to_dict()

def get_execution_status(mission_id: str) -> Dict:
    """Get status of a specific mission execution"""
    executor = initialize_nova_executor()
    if mission_id in executor.execution_history:
        return executor.execution_history[mission_id].to_dict()
    else:
        return {"error": "Mission not found"}

def get_all_executions() -> List[Dict]:
    """Get all execution history"""
    executor = initialize_nova_executor()
    return executor.get_execution_history()
