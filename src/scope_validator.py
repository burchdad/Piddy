"""
Scope Validator - Restrict execution to authorized repositories and paths

Enforces:
1. Repository allowlist (only modify approved repos)
2. Path restrictions (prevent modification of system files)
3. Operation limits (max files, lines, runtime)
4. File type restrictions (no .exe, .dll, system files)
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ScopeViolationType(Enum):
    """Type of scope violation"""
    UNAUTHORIZED_REPO = "unauthorized_repo"
    FORBIDDEN_PATH = "forbidden_path"
    FILE_LIMIT_EXCEEDED = "file_limit_exceeded"
    LINE_LIMIT_EXCEEDED = "line_limit_exceeded"
    EXECUTION_TIME_EXCEEDED = "execution_time_exceeded"
    FORBIDDEN_FILE_TYPE = "forbidden_file_type"
    OPERATING_SYSTEM_FILE = "operating_system_file"


class ScopeViolation(Exception):
    """Raised when scope limitation is violated"""
    
    def __init__(self, violation_type: ScopeViolationType, message: str):
        self.violation_type = violation_type
        super().__init__(f"[{violation_type.value}] {message}")


# ========================================================================
# REPOSITORY ALLOWLIST
# ========================================================================

ALLOWED_REPOSITORIES = {
    # Production repositories
    "burchdad/Piddy": {
        "paths": ["src/", "piddy/", "frontend/", "tests/"],
        "excluded_paths": ["node_modules/", "venv/", ".git/"],
        "max_files_per_commit": 50,
        "max_lines_per_commit": 1000,
    },
    
    # Development/test repositories (example)
    "burchdad/Piddy-dev": {
        "paths": ["*"],  # Allow all paths
        "excluded_paths": [".git/", ".env", "secrets/"],
        "max_files_per_commit": 100,
        "max_lines_per_commit": 5000,
    },
}

# Files NEVER modifiable (system safety)
PROTECTED_SYSTEM_FILES = {
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/root/.ssh",
    "/etc/ssh/sshd_config",
    "/.dockerenv",
    "/sys/",
    "/proc/",
    "/dev/",
}

# File types NEVER allowed (malware prevention)
FORBIDDEN_FILE_EXTENSIONS = {
    ".exe",      # Windows executable
    ".dll",      # Windows dynamic library
    ".so",       # Unix shared object (can be managed separately)
    ".bin",      # Binary
    ".elf",      # ELF executable
    ".o",        # Object file
    ".pyc",      # Compiled Python (prevent bytecode injection)
    ".pyo",      # Optimized compiled Python
}

# Maximum concurrent operations
MAX_CONCURRENT_OPERATIONS = 10
MAX_OPERATION_TIME_SECONDS = 600  # 10 minutes


class ScopeValidator:
    """
    Validate that a mission stays within authorized scope
    
    Enforces:
    - Only modify approved repositories
    - Only modify allowed paths within repos
    - Respect rate limits and file counts
    - Prevent modification of system files
    """
    
    def __init__(self):
        self.active_operations: Dict[str, Dict] = {}  # Track running missions
        logger.info(f"✅ ScopeValidator initialized")
        logger.info(f"   Allowed repos: {len(ALLOWED_REPOSITORIES)}")
        logger.info(f"   Protected files: {len(PROTECTED_SYSTEM_FILES)}")
        logger.info(f"   Forbidden extensions: {len(FORBIDDEN_FILE_EXTENSIONS)}")
    
    def validate_repository(self, repo_url: str) -> Optional[Dict]:
        """
        Validate that repository is in allowlist
        
        Args:
            repo_url: Git URL (https://github.com/owner/repo.git or owner/repo)
        
        Returns:
            Repository config if allowed, None if not allowed
        
        Raises:
            ScopeViolation: If repository not in allowlist
        """
        # Extract owner/repo from URL
        repo_key = self._extract_repo_key(repo_url)
        
        if repo_key not in ALLOWED_REPOSITORIES:
            raise ScopeViolation(
                ScopeViolationType.UNAUTHORIZED_REPO,
                f"Repository '{repo_key}' not in allowlist. "
                f"Allowed: {list(ALLOWED_REPOSITORIES.keys())}"
            )
        
        config = ALLOWED_REPOSITORIES[repo_key]
        logger.info(f"✅ Repository authorized: {repo_key}")
        
        return config
    
    def validate_file_paths(self, repo_key: str, files_to_modify: List[str]) -> None:
        """
        Validate that all file paths are allowed
        
        Args:
            repo_key: Repository identifier (owner/repo)
            files_to_modify: List of file paths to modify
        
        Raises:
            ScopeViolation: If any file path is not allowed
        """
        if repo_key not in ALLOWED_REPOSITORIES:
            raise ScopeViolation(
                ScopeViolationType.UNAUTHORIZED_REPO,
                f"Repository '{repo_key}' not in allowlist"
            )
        
        config = ALLOWED_REPOSITORIES[repo_key]
        allowed_paths = config.get("paths", [])
        excluded_paths = config.get("excluded_paths", [])
        
        for file_path in files_to_modify:
            # Check if file is in protected system files
            if self._is_protected_file(file_path):
                raise ScopeViolation(
                    ScopeViolationType.OPERATING_SYSTEM_FILE,
                    f"Cannot modify protected system file: {file_path}"
                )
            
            # Check for forbidden file types
            if self._has_forbidden_extension(file_path):
                raise ScopeViolation(
                    ScopeViolationType.FORBIDDEN_FILE_TYPE,
                    f"Cannot create/modify files with forbidden extension: {file_path}"
                )
            
            # Check if path is excluded
            if self._matches_excluded_paths(file_path, excluded_paths):
                raise ScopeViolation(
                    ScopeViolationType.FORBIDDEN_PATH,
                    f"Path is in excluded list: {file_path}"
                )
            
            # Check if path is in allowed paths (if not wildcard)
            if allowed_paths != ["*"]:
                if not self._matches_allowed_paths(file_path, allowed_paths):
                    raise ScopeViolation(
                        ScopeViolationType.FORBIDDEN_PATH,
                        f"Path '{file_path}' not in allowed paths: {allowed_paths}"
                    )
        
        logger.info(f"✅ All file paths validated: {len(files_to_modify)} files")
    
    def validate_operation_size(self, repo_key: str, operation: Dict) -> None:
        """
        Validate operation size limits
        
        Args:
            repo_key: Repository identifier
            operation: Operation dict with 'files_changed', 'lines_added', 'lines_deleted'
        
        Raises:
            ScopeViolation: If operation exceeds limits
        """
        if repo_key not in ALLOWED_REPOSITORIES:
            raise ScopeViolation(
                ScopeViolationType.UNAUTHORIZED_REPO,
                f"Repository '{repo_key}' not in allowlist"
            )
        
        config = ALLOWED_REPOSITORIES[repo_key]
        max_files = config.get("max_files_per_commit", 50)
        max_lines = config.get("max_lines_per_commit", 1000)
        
        files_changed = len(operation.get("files_changed", []))
        lines_added = operation.get("lines_added", 0)
        lines_deleted = operation.get("lines_deleted", 0)
        net_lines = lines_added + lines_deleted
        
        if files_changed > max_files:
            raise ScopeViolation(
                ScopeViolationType.FILE_LIMIT_EXCEEDED,
                f"Operation changes {files_changed} files, max {max_files} allowed"
            )
        
        if net_lines > max_lines:
            raise ScopeViolation(
                ScopeViolationType.LINE_LIMIT_EXCEEDED,
                f"Operation modifies {net_lines} lines, max {max_lines} allowed"
            )
        
        logger.info(f"✅ Operation size validated: {files_changed} files, {net_lines} lines")
    
    def validate_execution_time(self, mission_id: str, execution_mode: str = "SAFE") -> None:
        """
        Validate that execution time doesn't exceed limits
        
        Args:
            mission_id: Mission identifier to track
            execution_mode: SAFE, AUTO, PR_ONLY, DRY_RUN
        
        Raises:
            ScopeViolation: If execution time exceeded
        """
        if mission_id not in self.active_operations:
            self.active_operations[mission_id] = {
                "mode": execution_mode,
                "start_time": datetime.utcnow(),
            }
            
            # Check current operation count
            active_count = len(self.active_operations)
            if active_count > MAX_CONCURRENT_OPERATIONS:
                raise ScopeViolation(
                    ScopeViolationType.EXECUTION_TIME_EXCEEDED,
                    f"Too many concurrent operations: {active_count} / {MAX_CONCURRENT_OPERATIONS}"
                )
            
            logger.info(f"✅ Operation {mission_id} started ({execution_mode})")
    
    def check_operation_timeout(self, mission_id: str) -> None:
        """
        Check if mission has exceeded execution timeout
        
        Args:
            mission_id: Mission identifier
        
        Raises:
            ScopeViolation: If timeout exceeded
        """
        if mission_id not in self.active_operations:
            return  # Not tracked
        
        from datetime import datetime, timedelta
        
        start = self.active_operations[mission_id]["start_time"]
        elapsed = (datetime.utcnow() - start).total_seconds()
        
        if elapsed > MAX_OPERATION_TIME_SECONDS:
            raise ScopeViolation(
                ScopeViolationType.EXECUTION_TIME_EXCEEDED,
                f"Operation exceeded timeout: {elapsed:.0f}s / {MAX_OPERATION_TIME_SECONDS}s"
            )
    
    def complete_operation(self, mission_id: str) -> None:
        """Mark operation as complete"""
        if mission_id in self.active_operations:
            del self.active_operations[mission_id]
            logger.info(f"✅ Operation {mission_id} completed")
    
    # ====================================================================
    # Helper methods
    # ====================================================================
    
    def _extract_repo_key(self, repo_url: str) -> str:
        """Extract owner/repo from various URL formats"""
        # Format: https://github.com/owner/repo.git
        if "github.com" in repo_url:
            parts = repo_url.rstrip("/").replace(".git", "").split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
        
        # Format: owner/repo
        if "/" in repo_url and not "://" in repo_url:
            return repo_url.rstrip("/")
        
        raise ScopeViolation(
            ScopeViolationType.UNAUTHORIZED_REPO,
            f"Could not parse repository URL: {repo_url}"
        )
    
    def _is_protected_file(self, file_path: str) -> bool:
        """Check if file is in protected system files"""
        file_path_abs = str(Path(file_path).absolute())
        
        for protected in PROTECTED_SYSTEM_FILES:
            if file_path_abs.startswith(protected) or file_path.startswith(protected):
                return True
        
        return False
    
    def _has_forbidden_extension(self, file_path: str) -> bool:
        """Check if file has forbidden extension"""
        path = Path(file_path)
        return path.suffix.lower() in FORBIDDEN_FILE_EXTENSIONS
    
    def _matches_excluded_paths(self, file_path: str, excluded_paths: List[str]) -> bool:
        """Check if file matches excluded path patterns"""
        path = Path(file_path)
        
        for excluded in excluded_paths:
            if "*" in excluded:
                # Glob pattern
                if path.match(excluded):
                    return True
            else:
                # Exact or prefix match
                if str(path).startswith(excluded) or file_path.startswith(excluded):
                    return True
        
        return False
    
    def _matches_allowed_paths(self, file_path: str, allowed_paths: List[str]) -> bool:
        """Check if file matches allowed path patterns"""
        if allowed_paths == ["*"]:
            return True  # Allow all
        
        path = Path(file_path)
        
        for allowed in allowed_paths:
            if "*" in allowed:
                if path.match(allowed):
                    return True
            else:
                if str(path).startswith(allowed) or file_path.startswith(allowed):
                    return True
        
        return False


# Global validator instance
_validator: Optional[ScopeValidator] = None


def get_scope_validator() -> ScopeValidator:
    """Get global scope validator instance"""
    global _validator
    if _validator is None:
        _validator = ScopeValidator()
    return _validator


def validate_mission_scope(
    mission_id: str,
    repo_key: str,
    files_to_modify: List[str],
    operation: Dict,
    execution_mode: str = "SAFE",
) -> None:
    """
    Validate complete mission scope
    
    Args:
        mission_id: Mission identifier
        repo_key: Repository identifier
        files_to_modify: List of files to modify
        operation: Operation metadata
        execution_mode: SAFE, AUTO, PR_ONLY, DRY_RUN
    
    Raises:
        ScopeViolation: If any scope check fails
    """
    validator = get_scope_validator()
    
    try:
        # 1. Validate repository is authorized
        logger.info(f"🔐 Validating scope for mission {mission_id}")
        validator.validate_repository(repo_key)
        
        # 2. Validate all file paths
        validator.validate_file_paths(repo_key, files_to_modify)
        
        # 3. Validate operation size
        validator.validate_operation_size(repo_key, operation)
        
        # 4. Validate execution time limits
        validator.validate_execution_time(mission_id, execution_mode)
        
        logger.info(f"✅ Mission scope validated successfully: {mission_id}")
    
    except ScopeViolation as e:
        logger.error(f"❌ Scope violation: {e}")
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected scope validation error: {e}")
        raise ScopeViolation(
            ScopeViolationType.UNAUTHORIZED_REPO,
            f"Validation error: {str(e)}"
        )


# Import datetime for timeout tracking
from datetime import datetime
