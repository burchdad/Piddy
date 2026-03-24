"""
Action parser for Piddy agent responses.

Extracts structured file-creation actions from LLM output and executes them.
Supports any LLM tier (Ollama, Claude, GPT) by parsing a simple marker format.

Format expected in LLM output:
    ===FILE: relative/path/to/file.ext===
    <code content>
    ===END_FILE===
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Where user-requested project files get created
def _resolve_projects_root() -> Path:
    """Resolve the projects directory, handling both relative and absolute imports."""
    env = os.getenv("PIDDY_PROJECTS_ROOT", "")
    if env:
        return Path(env)
    # Walk up from this file to workspace root (src/agent/action_parser.py → ../../)
    this_file = Path(__file__).resolve()
    workspace = this_file.parents[2]
    return workspace / "projects"

PROJECTS_ROOT = _resolve_projects_root()

# Regex to extract ===FILE: path=== ... ===END_FILE=== blocks
_FILE_BLOCK_RE = re.compile(
    r"===FILE:\s*(.+?)\s*===\s*\n(.*?)===END_FILE===",
    re.DOTALL,
)

# Fallback 0: ===FILE: path=== + fenced code block, NO ===END_FILE=== required.
# Matches each ===FILE: marker followed by the immediately next fenced code block.
# Handles LLMs that forget the closing marker (very common with Ollama/qwen).
_FILE_OPEN_BLOCK_RE = re.compile(
    r"===FILE:\s*(.+?)\s*===\s*\n"
    r"```\w*\n(.*?)```",
    re.DOTALL,
)

# Fallback 1: #### FILE: path/to/file.ext  (common LLM format)
_FILE_HEADING_RE = re.compile(
    r"(?:^|\n)#+\s*(?:FILE:\s*)([^\n]+\.\w{1,10})\s*\n"
    r"```\w*\n(.*?)```",
    re.DOTALL,
)

# Fallback 2: detect ```lang\n...``` fenced blocks preceded by a filename hint
_FENCED_BLOCK_RE = re.compile(
    r"(?:^|\n)#+\s*[`*]*([^\n`*]+\.\w{1,10})[`*]*\s*\n"  # heading with filename
    r"```\w*\n(.*?)```",
    re.DOTALL,
)


def _safe_path(relative: str) -> Optional[Path]:
    """Resolve a relative path under PROJECTS_ROOT, rejecting traversal."""
    # Normalize separators
    relative = relative.replace("\\", "/").strip().strip("/")
    # Block traversal
    if ".." in relative.split("/"):
        logger.warning(f"Path traversal rejected: {relative}")
        return None
    target = (PROJECTS_ROOT / relative).resolve()
    if not str(target).startswith(str(PROJECTS_ROOT.resolve())):
        logger.warning(f"Path escapes projects root: {target}")
        return None
    return target


def parse_file_actions(text: str) -> List[Dict[str, str]]:
    """
    Parse LLM response text for file-creation blocks.

    Returns a list of dicts: [{"path": "relative/path", "content": "..."}]
    """
    actions: List[Dict[str, str]] = []
    seen_paths: set = set()  # track to avoid duplicates

    def _add(path: str, content: str):
        """Add action if not duplicate."""
        norm = path.replace("\\", "/").strip("/")
        if norm not in seen_paths:
            seen_paths.add(norm)
            actions.append({"path": norm, "content": content.rstrip("\n") + "\n"})

    # ── Stage 1: explicit ===FILE:=== ... ===END_FILE=== markers ──
    for match in _FILE_BLOCK_RE.finditer(text):
        rel_path = match.group(1).strip().strip("`'\"")
        content = match.group(2)
        content = re.sub(r"^```\w*\n", "", content)
        content = re.sub(r"\n```\s*$", "", content)
        _add(rel_path, content)

    # ── Stage 2: ===FILE: path=== + code block WITHOUT ===END_FILE=== ──
    if not actions:
        for match in _FILE_OPEN_BLOCK_RE.finditer(text):
            rel_path = match.group(1).strip().strip("`'\"")
            content = match.group(2)
            if len(rel_path) < 120:
                _add(rel_path, content)

    # ── Stage 3: also pick up heading-based code blocks (templates, CSS, JS) ──
    # These may appear alongside ===FILE: blocks for non-code assets.
    # We always run this, but only add files not already captured.
    if actions:
        # Infer project prefix from already-parsed ===FILE: paths
        project_prefix = _infer_project_prefix(actions)
        # Build a path lookup from the file structure tree in the text
        path_map = _build_path_map_from_tree(text)

        for match in _FENCED_BLOCK_RE.finditer(text):
            filename = match.group(1).strip().strip("`'\"")
            filename = re.sub(r"^(?:FILE|File|file)\s*:\s*", "", filename)
            content = match.group(2)

            if not ("." in filename and len(filename) < 120):
                continue
            # Skip if already captured by ===FILE: stage
            if any(filename in p for p in seen_paths):
                continue

            # Try to resolve full path from the tree
            full_path = path_map.get(filename)
            if not full_path and project_prefix:
                # Guess subdirectory from extension
                full_path = _guess_subdir(project_prefix, filename)

            _add(full_path or filename, content)

    # ── Stage 4: pure heading fallbacks (only when nothing above matched) ──
    if not actions:
        for match in _FILE_HEADING_RE.finditer(text):
            rel_path = match.group(1).strip().strip("`'\"")
            content = match.group(2)
            if "." in rel_path and len(rel_path) < 120:
                _add(rel_path, content)

    if not actions:
        for match in _FENCED_BLOCK_RE.finditer(text):
            filename = match.group(1).strip().strip("`'\"")
            filename = re.sub(r"^(?:FILE|File|file)\s*:\s*", "", filename)
            content = match.group(2)
            if "." in filename and len(filename) < 120:
                _add(filename, content)

    return actions


def _infer_project_prefix(actions: List[Dict[str, str]]) -> str:
    """Extract common project directory prefix from parsed actions."""
    paths = [a["path"] for a in actions if "/" in a["path"]]
    if not paths:
        return ""
    # Find common prefix (first directory component)
    parts = [p.split("/")[0] for p in paths]
    if len(set(parts)) == 1:
        return parts[0]
    return ""


def _build_path_map_from_tree(text: str) -> Dict[str, str]:
    """
    Parse the file structure tree often included in LLM output and build
    a mapping of filename → full relative path.

    Handles trees like:
        weather_dashboard/
        ├── templates/
        │   ├── base.html
    """
    path_map: Dict[str, str] = {}
    # Match tree lines: optional prefix chars (│├└─ spaces) then a filename/dir
    tree_re = re.compile(r"^[│├└─\s]*([^\s│├└─/][^\n/]*\.(\w{1,10}))$", re.MULTILINE)
    # Also extract the root directory from lines like "weather_dashboard/"
    root_re = re.compile(r"^(\w[\w_-]*)/$", re.MULTILINE)

    root = ""
    root_match = root_re.search(text)
    if root_match:
        root = root_match.group(1)

    # Try to parse indentation-based hierarchy
    dir_re = re.compile(r"^([│├└─\s]*?)([^\s│├└─][^\n]*/)$", re.MULTILINE)
    # Build ordered list of (indent_level, name, is_dir)
    line_re = re.compile(
        r"^([│├└─\s]*?)([^\s│├└─/][^\n]*)$", re.MULTILINE
    )

    current_dirs: Dict[int, str] = {}  # indent_level → directory name

    for m in line_re.finditer(text):
        indent = len(m.group(1))
        name = m.group(2).strip()
        if name.endswith("/"):
            # Directory
            current_dirs[indent] = name.rstrip("/")
            # Clear deeper levels
            current_dirs = {k: v for k, v in current_dirs.items() if k <= indent}
        elif "." in name and len(name) < 80:
            # File — build path from current directory stack
            parts = []
            if root and 0 not in current_dirs:
                parts.append(root)
            for level in sorted(k for k in current_dirs if k < indent):
                parts.append(current_dirs[level])
            parts.append(name)
            full = "/".join(parts)
            path_map[name] = full

    return path_map


# Extension → likely subdirectory mapping
_EXT_SUBDIRS = {
    ".html": "templates",
    ".jinja": "templates",
    ".jinja2": "templates",
    ".css": "static/css",
    ".scss": "static/css",
    ".js": "static/js",
    ".ts": "static/js",
    ".png": "static/images",
    ".jpg": "static/images",
    ".svg": "static/images",
}


def _guess_subdir(project_prefix: str, filename: str) -> str:
    """Guess the full path for a bare filename using extension heuristics."""
    ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
    subdir = _EXT_SUBDIRS.get(ext, "")
    if subdir:
        return f"{project_prefix}/{subdir}/{filename}"
    return f"{project_prefix}/{filename}"


def execute_file_actions(actions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Write parsed file actions to disk under PROJECTS_ROOT.

    Returns a list of result dicts with success/error info.
    """
    results: List[Dict[str, Any]] = []
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

    for action in actions:
        rel = action["path"]
        target = _safe_path(rel)
        if target is None:
            results.append({"path": rel, "success": False, "error": "Invalid path"})
            continue

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(action["content"], encoding="utf-8")
            display = str(target.relative_to(PROJECTS_ROOT.resolve())).replace("\\", "/")
            logger.info(f"📄 Created file: projects/{display}")
            results.append({
                "path": f"projects/{display}",
                "success": True,
                "size": len(action["content"]),
            })
        except Exception as e:
            logger.error(f"Failed to write {rel}: {e}")
            results.append({"path": rel, "success": False, "error": str(e)})

    return results


def strip_file_markers(text: str) -> str:
    """Remove ===FILE:=== / ===END_FILE=== markers from the reply shown to the user."""
    cleaned = _FILE_BLOCK_RE.sub("", text)
    # Also strip open-block markers (===FILE: without ===END_FILE===)
    cleaned = _FILE_OPEN_BLOCK_RE.sub("", cleaned)
    # Collapse excessive blank lines left behind
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# ── Agentic system prompt addon ──────────────────────────────────────

AGENTIC_PROMPT_ADDON = """
## File Creation Mode

When the user asks you to create, build, scaffold, or generate files or a project:
1. Plan the file structure first and explain it briefly.
2. Output EACH file using this exact format (the markers are required):

===FILE: relative/path/to/file.ext===
<file content here>
===END_FILE===

3. After all files, summarize what you created.

Rules:
- Use relative paths (e.g. calculator/main.py, not /home/user/calculator/main.py)
- Include ALL necessary files (code, configs, README, etc.)
- Each file must be complete and working
- Include proper imports, error handling, and comments
- If creating a Python project, include requirements.txt if needed
- If creating a Node project, include package.json

Example — if user says "create a hello world Flask app":

===FILE: flask_hello/app.py===
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
===END_FILE===

===FILE: flask_hello/requirements.txt===
flask>=3.0
===END_FILE===

I created a Flask hello-world app with 2 files in the flask_hello/ directory.
"""
