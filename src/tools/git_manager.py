"""
Git integration module for version control operations.

Handles commits, branches, pushes, and repository management.
Works with both the Piddy repository and external project repositories.
"""

import os
import logging
import subprocess
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GitConfig:
    """Git configuration."""
    repo_path: str
    user_name: str = "Piddy Agent"
    user_email: str = "piddy@agent.local"
    remote_url: Optional[str] = None


@dataclass
class CommitInfo:
    """Information about a commit."""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int


class GitManager:
    """
    Manages Git operations for projects.

    Supports:
    - Committing generated code
    - Branch management
    - Push/pull operations
    - Status checking
    - Diff viewing
    """

    def __init__(self, repo_path: str, user_name: str = "Piddy Agent", user_email: str = "piddy@agent.local"):
        """
        Initialize GitManager.

        Args:
            repo_path: Path to the Git repository
            user_name: Git commit author name
            user_email: Git commit author email
        """
        self.repo_path = Path(repo_path)
        self.user_name = user_name
        self.user_email = user_email

        if not self._is_git_repo():
            raise ValueError(f"Directory is not a Git repository: {repo_path}")

        self._configure_git()
        logger.info(f"GitManager initialized for {repo_path}")

    def _is_git_repo(self) -> bool:
        """Check if directory is a Git repository."""
        return (self.repo_path / ".git").exists()

    def _configure_git(self):
        """Configure Git user for commits."""
        try:
            self._run_git("config", "user.name", self.user_name)
            self._run_git("config", "user.email", self.user_email)
        except Exception as e:
            logger.warning(f"Failed to configure Git user: {e}")

    def _run_git(self, *args: str) -> str:
        """
        Run a Git command.

        Args:
            *args: Git command arguments

        Returns:
            Command output

        Raises:
            RuntimeError: If command fails
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout
            raise RuntimeError(f"Git command failed: {error_msg}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Git command timed out")

    def get_status(self) -> Dict[str, Any]:
        """
        Get repository status.

        Returns:
            Dictionary with status information
        """
        try:
            status_output = self._run_git("status", "--porcelain")
            
            # Parse status output
            staged = []
            unstaged = []
            untracked = []

            for line in status_output.split('\n'):
                if not line:
                    continue
                status_code = line[:2]
                filename = line[3:]

                if status_code[0] != ' ':
                    staged.append(filename)
                if status_code[1] != ' ':
                    unstaged.append(filename)
                if status_code == '??':
                    untracked.append(filename)

            current_branch = self._run_git("rev-parse", "--abbrev-ref", "HEAD")

            return {
                "success": True,
                "branch": current_branch,
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "has_changes": bool(staged or unstaged or untracked)
            }
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return {"success": False, "error": str(e)}

    def stage_files(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Stage files for commit.

        Args:
            files: List of file paths to stage. If None, stages all.

        Returns:
            Result dictionary
        """
        try:
            if files is None:
                # Stage all changes including submodules
                self._run_git("add", "-A")
                # Also update submodule references
                self._run_git("add", "--update")
                staged = "all changes"
            else:
                # Stage specific files
                for file in files:
                    self._run_git("add", file)
                staged = f"{len(files)} file(s)"

            logger.info(f"Staged {staged}")
            return {"success": True, "message": f"Staged {staged}"}

        except Exception as e:
            logger.error(f"Error staging files: {e}")
            return {"success": False, "error": str(e)}

    def commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        auto_stage: bool = True
    ) -> Dict[str, Any]:
        """
        Create a commit.

        Args:
            message: Commit message
            files: Optional list of files to include
            auto_stage: Whether to auto-stage files

        Returns:
            Commit result
        """
        try:
            # Stage files if requested
            if auto_stage:
                if files:
                    self.stage_files(files)
                else:
                    self.stage_files()

            # Check for staged changes
            status = self.get_status()
            if not status.get("has_changes", False):
                return {
                    "success": False,
                    "error": "No changes to commit",
                    "status": {
                        "staged": status.get("staged", []),
                        "unstaged": status.get("unstaged", []),
                        "untracked": status.get("untracked", [])
                    }
                }

            # Commit
            self._run_git("commit", "-m", message)

            # Get commit hash
            commit_hash = self._run_git("rev-parse", "HEAD")

            logger.info(f"Commit created: {commit_hash[:8]}")

            return {
                "success": True,
                "commit_hash": commit_hash,
                "short_hash": commit_hash[:8],
                "message": f"✅ Committed: {message}",
                "files": files or "all"
            }

        except RuntimeError as e:
            if "nothing to commit" in str(e):
                return {"success": False, "error": "No changes to commit"}
            logger.error(f"Error creating commit: {e}")
            return {"success": False, "error": str(e)}

    def create_branch(self, branch_name: str, from_branch: str = "main") -> Dict[str, Any]:
        """
        Create a new branch.

        Args:
            branch_name: Name of new branch
            from_branch: Branch to create from

        Returns:
            Branch creation result
        """
        try:
            # Ensure from_branch exists
            self._run_git("checkout", from_branch)
            # Create new branch
            self._run_git("checkout", "-b", branch_name)

            logger.info(f"Branch created: {branch_name}")

            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ Branch created: {branch_name}"
            }

        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            return {"success": False, "error": str(e)}

    def switch_branch(self, branch_name: str) -> Dict[str, Any]:
        """Switch to a different branch."""
        try:
            self._run_git("checkout", branch_name)
            logger.info(f"Switched to branch: {branch_name}")
            return {"success": True, "branch": branch_name}
        except Exception as e:
            logger.error(f"Error switching branch: {e}")
            return {"success": False, "error": str(e)}

    def get_branches(self) -> Dict[str, Any]:
        """Get list of branches."""
        try:
            output = self._run_git("branch", "-a")
            branches = [b.strip().replace("* ", "") for b in output.split('\n') if b.strip()]
            current = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
            return {
                "success": True,
                "current": current,
                "branches": branches
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def push(self, branch: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """
        Push commits to remote.

        Args:
            branch: Branch to push (None = current)
            force: Force push

        Returns:
            Push result
        """
        try:
            if branch is None:
                branch = self._run_git("rev-parse", "--abbrev-ref", "HEAD")

            args = ["push", "-u", "origin", branch]
            if force:
                args.insert(2, "-f")

            self._run_git(*args)
            logger.info(f"Pushed branch: {branch}")
            
            # Verify the push worked by checking if local is ahead of remote
            try:
                ahead_behind = self._run_git("rev-list", "--left-right", "--count", f"{branch}...origin/{branch}")
                ahead_count = int(ahead_behind.strip().split()[0])
                if ahead_count > 0:
                    logger.warning(f"Push verification: Still {ahead_count} commits ahead. Push may have failed.")
                    return {
                        "success": False,
                        "error": f"Push verification failed: {ahead_count} commits still ahead of remote",
                        "branch": branch
                    }
            except Exception as verify_error:
                logger.debug(f"Push verification skipped: {verify_error}")

            return {
                "success": True,
                "branch": branch,
                "message": f"✅ Pushed to origin/{branch}"
            }

        except Exception as e:
            logger.error(f"Error pushing: {e}")
            return {"success": False, "error": str(e)}

    def get_diff(self, file: Optional[str] = None, staged: bool = False) -> Dict[str, Any]:
        """
        Get diff of changes.

        Args:
            file: Specific file (None = all)
            staged: Show staged changes

        Returns:
            Diff output
        """
        try:
            args = ["diff"]
            if staged:
                args.append("--staged")
            if file:
                args.append(file)

            diff_output = self._run_git(*args)

            return {
                "success": True,
                "diff": diff_output[:2000],  # Limit output
                "is_truncated": len(diff_output) > 2000
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_log(self, max_commits: int = 5) -> Dict[str, Any]:
        """
        Get recent commits.

        Args:
            max_commits: Number of commits to retrieve

        Returns:
            List of recent commits
        """
        try:
            format_str = "%H%n%an%n%ai%n%s%n---"
            output = self._run_git("log", f"-{max_commits}", f"--format={format_str}")

            commits = []
            for block in output.split("---\n"):
                lines = block.strip().split('\n')
                if len(lines) >= 4:
                    commits.append({
                        "hash": lines[0][:8],
                        "author": lines[1],
                        "date": lines[2],
                        "message": lines[3]
                    })

            return {"success": True, "commits": commits}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_pull_request_info(self, branch: str, title: str, description: str) -> Dict[str, Any]:
        """
        Generate info for creating a PR (GitHub/GitLab format).

        Args:
            branch: Feature branch name
            title: PR title
            description: PR description

        Returns:
            PR information
        """
        try:
            remote = self._run_git("config", "--get", "remote.origin.url")
            current_branch = self._run_git("rev-parse", "--abbrev-ref", "HEAD")

            return {
                "success": True,
                "from_branch": current_branch,
                "to_branch": "main",
                "title": title,
                "description": description,
                "remote": remote,
                "message": "Use this information to create a PR on GitHub/GitLab"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def get_git_manager(repo_path: Optional[str] = None) -> Optional[GitManager]:
    """
    Get a GitManager instance for the specified or default repository.

    Args:
        repo_path: Repository path (defaults to Piddy root)

    Returns:
        GitManager instance or None if not a git repo
    """
    if repo_path is None:
        repo_path = os.getenv("PIDDY_PROJECT_ROOT", "/workspaces/Piddy")

    try:
        return GitManager(repo_path)
    except ValueError as e:
        logger.warning(f"Could not initialize GitManager: {e}")
        return None
