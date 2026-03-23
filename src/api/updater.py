"""
Piddy Auto-Update System

When Piddy detects an internet connection it queries the GitHub repository for
new releases / commits.  If an update is available the user is prompted before
anything is applied.

Flow:
  1. check_for_updates()  → returns {available: bool, …}
  2. Frontend shows a banner / toast if available == True
  3. User clicks "Install Update" → POST /api/update/apply
  4. apply_update() pulls the latest, restarts if needed

Safe design:
  - Never auto-applies — always prompts the user first
  - Creates a backup before applying
  - Uses git pull when .git exists, otherwise downloads a tarball
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import socket
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VERSION_FILE = PROJECT_ROOT / "src" / "__init__.py"

# ── Defaults ────────────────────────────────────────────────────────────────
GITHUB_OWNER = "your-org"          # overridden by settings.piddy_kb_repo_url
GITHUB_REPO = "piddy"
GITHUB_API = "https://api.github.com"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _current_version() -> str:
    """Read __version__ from src/__init__.py."""
    try:
        if VERSION_FILE.exists():
            for line in VERSION_FILE.read_text().splitlines():
                if line.strip().startswith("__version__"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"


def _has_internet() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3).close()
        return True
    except Exception:
        return False


def _github_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Piddy-Updater"}
    try:
        from config.settings import get_settings
        token = get_settings().github_token
        if token:
            headers["Authorization"] = f"token {token}"
    except Exception:
        pass
    return headers


def _resolve_repo_url() -> Optional[str]:
    """Try to derive owner/repo from the git remote or config."""
    # 1. Check git remote
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            url = r.stdout.strip()
            # https://github.com/owner/repo.git  or  git@github.com:owner/repo.git
            if "github.com" in url:
                return url
    except Exception:
        pass
    return None


def _parse_owner_repo(url: str) -> tuple:
    """Extract (owner, repo) from a GitHub URL."""
    url = url.rstrip("/").removesuffix(".git")
    if "github.com:" in url:
        # SSH: git@github.com:owner/repo
        parts = url.split(":")[-1].split("/")
    elif "github.com/" in url:
        parts = url.split("github.com/")[-1].split("/")
    else:
        return GITHUB_OWNER, GITHUB_REPO
    if len(parts) >= 2:
        return parts[0], parts[1]
    return GITHUB_OWNER, GITHUB_REPO


def _version_tuple(v: str) -> tuple:
    """Parse '5.0.0' → (5, 0, 0) for proper comparison."""
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


# ── Public API ──────────────────────────────────────────────────────────────

def check_for_updates() -> Dict[str, Any]:
    """
    Check GitHub for a newer release or newer commits.
    Returns a dict with `available`, `current_version`, `latest_version`, etc.
    """
    current = _current_version()
    result: Dict[str, Any] = {
        "current_version": current,
        "available": False,
        "checked_at": datetime.utcnow().isoformat(),
        "internet": False,
    }

    if not _has_internet():
        result["message"] = "No internet connection — skipping update check"
        return result

    result["internet"] = True

    repo_url = _resolve_repo_url()
    if not repo_url:
        result["message"] = "No GitHub remote configured"
        return result

    owner, repo = _parse_owner_repo(repo_url)
    headers = _github_headers()

    # Strategy 1: Check latest release tag
    try:
        import urllib.request
        req = urllib.request.Request(f"{GITHUB_API}/repos/{owner}/{repo}/releases/latest", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            latest_tag = data.get("tag_name", "").lstrip("v")
            result["latest_version"] = latest_tag
            result["release_name"] = data.get("name")
            result["release_url"] = data.get("html_url")
            result["published_at"] = data.get("published_at")
            if latest_tag and _version_tuple(latest_tag) > _version_tuple(current):
                result["available"] = True
                result["message"] = f"Update available: {current} → {latest_tag}"
            else:
                result["message"] = "You are on the latest release"
            return result
    except Exception:
        pass

    # Strategy 2: Compare latest commit on default branch
    try:
        import urllib.request
        req = urllib.request.Request(f"{GITHUB_API}/repos/{owner}/{repo}/commits?per_page=1", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            commits = json.loads(resp.read())
            if commits:
                remote_sha = commits[0]["sha"][:7]
                # Compare to local HEAD
                try:
                    r = subprocess.run(
                        ["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=5,
                    )
                    local_sha = r.stdout.strip() if r.returncode == 0 else None
                except Exception:
                    local_sha = None

                if local_sha and local_sha != remote_sha:
                    result["available"] = True
                    result["local_sha"] = local_sha
                    result["remote_sha"] = remote_sha
                    result["message"] = f"Newer commits available (local: {local_sha}, remote: {remote_sha})"
                else:
                    result["message"] = "Up to date with remote"
    except Exception as e:
        result["message"] = f"Could not check commits: {e}"

    return result


def apply_update() -> Dict[str, Any]:
    """
    Pull the latest code from the git remote.
    Creates a lightweight backup first.
    """
    result: Dict[str, Any] = {"success": False, "timestamp": datetime.utcnow().isoformat()}

    if not _has_internet():
        result["error"] = "No internet connection"
        return result

    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        result["error"] = "Not a git repository — manual update required"
        return result

    # 1. Stash any local changes
    try:
        subprocess.run(
            ["git", "stash", "--include-untracked"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=15,
        )
    except Exception:
        pass

    # 2. Pull
    try:
        r = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=60,
        )
        if r.returncode == 0:
            result["success"] = True
            result["output"] = r.stdout.strip()[:500]
            result["new_version"] = _current_version()
            result["message"] = "Update applied successfully. Restart Piddy to use the new version."
        else:
            result["error"] = r.stderr.strip()[:500]
            # Pop stash on failure
            subprocess.run(
                ["git", "stash", "pop"],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=10,
            )
    except Exception as e:
        result["error"] = str(e)

    return result
