"""
Build Learnings Store — Persistent memory for file-creation outcomes.

Records when file parsing/creation succeeds or fails, and feeds
relevant lessons back into the system prompt so the LLM avoids
repeating mistakes.

Storage: growth_data/build_learnings.json
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_STORE_PATH: Optional[Path] = None


def _get_store_path() -> Path:
    global _STORE_PATH
    if _STORE_PATH is None:
        root = Path(__file__).resolve().parents[2]
        _STORE_PATH = root / "growth_data" / "build_learnings.json"
        _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return _STORE_PATH


def _load_store() -> List[Dict]:
    path = _get_store_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_store(entries: List[Dict]):
    path = _get_store_path()
    # Keep the last 200 entries to avoid unbounded growth
    entries = entries[-200:]
    try:
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    except OSError as e:
        logger.error(f"Failed to save build learnings: {e}")


def record_build_outcome(
    *,
    llm_tier: str,
    llm_model: str,
    user_prompt: str,
    files_expected: int,
    files_created: int,
    errors: List[str],
    parse_method: str,  # "explicit_markers", "file_heading", "fenced_block", "none"
    raw_snippet: str = "",
):
    """Record the outcome of a file-creation attempt."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "llm_tier": llm_tier,
        "llm_model": llm_model,
        "prompt_preview": user_prompt[:120],
        "files_expected": files_expected,
        "files_created": files_created,
        "success": files_created > 0 and not errors,
        "errors": errors[:5],  # cap error list
        "parse_method": parse_method,
        "raw_snippet": raw_snippet[:300],  # first 300 chars of raw reply
    }
    store = _load_store()
    store.append(entry)
    _save_store(store)
    logger.info(
        f"📝 Build learning recorded: {files_created}/{files_expected} files, "
        f"parse={parse_method}, tier={llm_tier}"
    )


def get_recent_failures(limit: int = 5) -> List[Dict]:
    """Get recent build failures for prompt injection."""
    store = _load_store()
    failures = [e for e in store if not e.get("success")]
    return failures[-limit:]


def build_lessons_prompt() -> str:
    """
    Generate a concise lessons-learned block to inject into the system prompt.
    Returns empty string if no relevant lessons exist.
    """
    failures = get_recent_failures(limit=5)
    if not failures:
        return ""

    lines = [
        "\n## Lessons from Previous Builds (IMPORTANT)\n",
        "Previous file-creation attempts had issues. Follow these rules strictly:\n",
    ]

    seen_issues = set()
    for f in failures:
        for err in f.get("errors", []):
            short = err[:120]
            if short not in seen_issues:
                seen_issues.add(short)
                lines.append(f"- PREVIOUS ERROR: {short}")

        if f.get("parse_method") == "none":
            msg = "LLM output was not parseable — use ===FILE: path=== markers"
            if msg not in seen_issues:
                seen_issues.add(msg)
                lines.append(f"- {msg}")

    # Always reinforce the correct format
    lines.append("")
    lines.append(
        "YOU MUST wrap every file in ===FILE: relative/path=== ... ===END_FILE=== markers. "
        "Do NOT use '#### FILE: path' headings — they are unreliable. "
        "Do NOT include the word 'FILE:' in the path itself."
    )

    return "\n".join(lines) + "\n"
