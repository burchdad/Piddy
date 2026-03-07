"""GitHub PR management for autonomous fixes."""

import logging
import subprocess
import json
from typing import Optional, Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class PRManager:
    """Manage pull request creation and tracking."""
    
    def __init__(self, github_token: Optional[str] = None, repo_owner: str = "", repo_name: str = ""):
        """Initialize PR manager."""
        self.github_token = github_token or self._get_github_token()
        self.repo_owner = repo_owner or "burchdad"
        self.repo_name = repo_name or "Piddy"
        self.repo_full = f"{self.repo_owner}/{self.repo_name}"
    
    def _get_github_token(self) -> str:
        """Get GitHub token from environment or git config."""
        import os
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            try:
                result = subprocess.run(
                    ["git", "config", "user.github_token"],
                    capture_output=True,
                    text=True
                )
                token = result.stdout.strip()
            except Exception as e:
                logger.warning(f"Could not retrieve GitHub token: {e}")
        return token
    
    def create_pr(
        self,
        title: str,
        description: str,
        branch_name: str,
        base_branch: str = "main"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a pull request on GitHub.
        
        Args:
            title: PR title
            description: PR description (markdown)
            branch_name: Feature branch name
            base_branch: Target branch (default: main)
            
        Returns:
            PR data dict or None if failed
        """
        if not self.github_token:
            logger.error("GitHub token not configured - cannot create PR")
            return None
        
        try:
            # Create PR via GitHub API using gh CLI
            pr_body = json.dumps({
                "title": title,
                "body": description,
                "head": branch_name,
                "base": base_branch,
                "draft": False
            })
            
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", description,
                    "--base", base_branch,
                    "--head", branch_name,
                    "--repo", self.repo_full
                ],
                capture_output=True,
                text=True,
                env={"GH_TOKEN": self.github_token, **subprocess.os.environ}
            )
            
            if result.returncode == 0:
                logger.info(f"✅ PR created: {result.stdout.strip()}")
                return {"pr_url": result.stdout.strip(), "title": title}
            else:
                logger.error(f"Failed to create PR: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Create a new git branch.
        
        Args:
            branch_name: Name of the new branch
            
        Returns:
            True if successful
        """
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True
            )
            logger.info(f"✅ Branch created: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            return False
    
    def commit_changes(self, message: str, files: Optional[list] = None) -> bool:
        """
        Commit changes to current branch.
        
        Args:
            message: Commit message
            files: Specific files to commit (None = all)
            
        Returns:
            True if successful
        """
        try:
            # Stage files
            if files:
                subprocess.run(["git", "add"] + files, check=True, capture_output=True)
            else:
                subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Changes committed: {message}")
                return True
            elif "nothing to commit" in result.stdout.lower():
                logger.info("No changes to commit")
                return True
            else:
                logger.error(f"Commit failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """
        Push branch to remote.
        
        Args:
            branch_name: Branch to push
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Branch pushed: {branch_name}")
                return True
            else:
                logger.error(f"Push failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing branch: {e}")
            return False
    
    def checkout_main(self) -> bool:
        """Checkout main branch."""
        try:
            subprocess.run(
                ["git", "checkout", "main"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                capture_output=True
            )
            logger.info("✅ Checked out main branch")
            return True
        except Exception as e:
            logger.error(f"Error checking out main: {e}")
            return False


def get_pr_manager() -> PRManager:
    """Get PR manager instance."""
    return PRManager()
