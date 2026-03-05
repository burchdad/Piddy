"""
Safe file writing utility for generated code.

Ensures files are written to appropriate locations within the project,
with validation and user feedback.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Types of files that can be generated."""
    MODEL = "models"
    ROUTE = "routes"
    UTILITY = "utils"
    SERVICE = "services"
    SCHEMA = "schemas"
    MIDDLEWARE = "middleware"
    CONFIG = "config"
    TEST = "tests"
    OTHER = "."


# Mapping of file types to their suggested locations
FILE_TYPE_PATHS = {
    FileType.MODEL: "src/models",
    FileType.ROUTE: "src/api/routes",
    FileType.UTILITY: "src/utils",
    FileType.SERVICE: "src/services",
    FileType.SCHEMA: "src/schemas",
    FileType.MIDDLEWARE: "src/middleware",
    FileType.CONFIG: "config",
    FileType.TEST: "tests",
    FileType.OTHER: ".",
}


class FileWriter:
    """
    Safe file writer for generated code with project context awareness.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the file writer.

        Args:
            project_root: Root directory of the project. Defaults to /workspaces/Piddy
        """
        if project_root is None:
            project_root = os.getenv("PIDDY_PROJECT_ROOT", "/workspaces/Piddy")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")
        
        logger.info(f"FileWriter initialized with project root: {self.project_root}")

    def _validate_path(self, file_path: Path) -> bool:
        """
        Validate that a path is within the project root.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve symlinks
            resolved_path = file_path.resolve()
            resolved_root = self.project_root.resolve()
            
            # Check if path is within project root
            resolved_path.relative_to(resolved_root)
            return True
        except ValueError:
            return False

    def suggest_path(
        self,
        filename: str,
        file_type: FileType = FileType.OTHER,
        subdir: Optional[str] = None
    ) -> Path:
        """
        Suggest the appropriate path for a file based on its type.

        Args:
            filename: Name of the file to create
            file_type: Type of file (determines suggested directory)
            subdir: Optional subdirectory within the type path

        Returns:
            Suggested Path object (relative to project root)

        Example:
            >>> writer.suggest_path("user.py", FileType.MODEL)
            PosixPath('src/models/user.py')
            
            >>> writer.suggest_path("auth.py", FileType.ROUTE, "auth")
            PosixPath('src/api/routes/auth/auth.py')
        """
        base_path = self.project_root / FILE_TYPE_PATHS[file_type]
        
        if subdir:
            base_path = base_path / subdir
        
        return base_path / filename

    def write_file(
        self,
        filename: str,
        content: str,
        file_type: FileType = FileType.OTHER,
        subdir: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, any]:
        """
        Write a file to the appropriate location with validation.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
            file_type: Type of file (determines directory)
            subdir: Optional subdirectory within the type path
            overwrite: Whether to overwrite if file exists

        Returns:
            Dictionary with:
                - success: bool - Whether write succeeded
                - path: str - Path where file was written (or would be written)
                - message: str - Human-readable message
                - error: Optional[str] - Error message if failed

        Example:
            >>> result = writer.write_file(
            ...     "user_model.py",
            ...     "class User: pass",
            ...     FileType.MODEL
            ... )
            >>> if result['success']:
            ...     print(f"File written to {result['path']}")
        """
        try:
            # Get suggested path
            file_path = self.suggest_path(filename, file_type, subdir)

            # Validate path is safe
            if not self._validate_path(file_path):
                return {
                    "success": False,
                    "path": str(file_path),
                    "message": f"Path is outside project root: {file_path}",
                    "error": "INVALID_PATH"
                }

            # Check if file exists
            if file_path.exists() and not overwrite:
                return {
                    "success": False,
                    "path": str(file_path),
                    "message": f"File already exists: {file_path}. Set overwrite=True to replace.",
                    "error": "FILE_EXISTS"
                }

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)

            # Calculate relative path for display
            rel_path = file_path.relative_to(self.project_root)

            logger.info(f"File written successfully: {rel_path}")

            return {
                "success": True,
                "path": str(rel_path),
                "message": f"✅ File written to: `{rel_path}`",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error writing file: {str(e)}")
            return {
                "success": False,
                "path": str(file_path) if 'file_path' in locals() else "unknown",
                "message": f"Error writing file: {str(e)}",
                "error": str(type(e).__name__)
            }

    def get_file_preview(self, filename: str, file_type: FileType = FileType.OTHER) -> Dict[str, str]:
        """
        Get a preview of where a file would be written.

        Args:
            filename: Name of the file
            file_type: Type of file

        Returns:
            Dictionary with file info for preview

        Example:
            >>> preview = writer.get_file_preview("auth.py", FileType.ROUTE)
            >>> print(preview['message'])
            📁 Would write to: src/api/routes/auth.py
        """
        file_path = self.suggest_path(filename, file_type)
        rel_path = file_path.relative_to(self.project_root)
        
        return {
            "filename": filename,
            "type": file_type.value,
            "path": str(rel_path),
            "absolute_path": str(file_path),
            "exists": file_path.exists(),
            "message": f"📁 Would write to: `{rel_path}`"
        }

    def list_project_structure(self, max_depth: int = 2) -> str:
        """
        Get a formatted view of the project structure.

        Args:
            max_depth: Maximum directory depth to show

        Returns:
            Formatted project structure string
        """
        def format_tree(path: Path, prefix: str = "", depth: int = 0) -> str:
            if depth > max_depth:
                return ""

            items = []
            try:
                entries = sorted(path.iterdir())
                # Filter out common unimportant dirs
                skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
                entries = [e for e in entries if e.name not in skip_dirs]

                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1
                    current_prefix = "└── " if is_last else "├── "
                    items.append(f"{prefix}{current_prefix}{entry.name}")

                    if entry.is_dir() and depth < max_depth:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        items.append(format_tree(entry, next_prefix, depth + 1))
            except PermissionError:
                pass

            return "\n".join(filter(None, items))

        structure = f"{self.project_root.name}/\n"
        structure += format_tree(self.project_root)
        return structure

    def get_context_info(self) -> Dict[str, str]:
        """
        Get information about the project context for the agent.

        Returns:
            Dictionary with project context information
        """
        return {
            "project_root": str(self.project_root),
            "project_name": self.project_root.name,
            "file_type_paths": {ft.name: path for ft, path in FILE_TYPE_PATHS.items()},
            "structure": self.list_project_structure()
        }


# Global instance
_file_writer: Optional[FileWriter] = None


def get_file_writer() -> FileWriter:
    """Get or create the global FileWriter instance."""
    global _file_writer
    if _file_writer is None:
        _file_writer = FileWriter()
    return _file_writer


def write_generated_file(
    filename: str,
    content: str,
    file_type: FileType = FileType.OTHER,
    subdir: Optional[str] = None
) -> Dict:
    """
    Convenience function to write a generated file.

    Args:
        filename: Name of the file
        content: File content
        file_type: Type of file
        subdir: Optional subdirectory

    Returns:
        Result dictionary from FileWriter.write_file()
    """
    writer = get_file_writer()
    return writer.write_file(filename, content, file_type, subdir)
