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

# Fallback: detect ```lang\n...``` fenced blocks preceded by a filename hint
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

    # Primary: explicit ===FILE:=== markers
    for match in _FILE_BLOCK_RE.finditer(text):
        rel_path = match.group(1).strip().strip("`'\"")
        content = match.group(2)
        # Strip leading/trailing fenced-code markers if the LLM wrapped them
        content = re.sub(r"^```\w*\n", "", content)
        content = re.sub(r"\n```\s*$", "", content)
        actions.append({"path": rel_path, "content": content.rstrip("\n") + "\n"})

    # If no explicit markers, try fenced-block fallback (heading + code block)
    if not actions:
        for match in _FENCED_BLOCK_RE.finditer(text):
            filename = match.group(1).strip().strip("`'\"")
            content = match.group(2)
            # Only accept if it looks like a real filename
            if "." in filename and len(filename) < 120:
                actions.append({"path": filename, "content": content.rstrip("\n") + "\n"})

    return actions


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
