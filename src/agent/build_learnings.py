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
_CLOUD_FIX_PATH: Optional[Path] = None


def _get_store_path() -> Path:
    global _STORE_PATH
    if _STORE_PATH is None:
        root = Path(__file__).resolve().parents[2]
        _STORE_PATH = root / "growth_data" / "build_learnings.json"
        _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return _STORE_PATH


def _get_cloud_fix_path() -> Path:
    """Path for cloud-fix lessons (Anthropic/OpenAI teaching Ollama)."""
    global _CLOUD_FIX_PATH
    if _CLOUD_FIX_PATH is None:
        root = Path(__file__).resolve().parents[2]
        _CLOUD_FIX_PATH = root / "growth_data" / "cloud_fix_lessons.json"
        _CLOUD_FIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    return _CLOUD_FIX_PATH


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

    # ── Inject cloud-fix lessons (Anthropic/OpenAI teaching Ollama) ──
    cloud_lessons = _build_cloud_fix_lessons()
    if cloud_lessons:
        lines.append("")
        lines.append(cloud_lessons)

    return "\n".join(lines) + "\n"


# ═══════════════════════════════════════════════════════════════════════
# Cloud Fix Lessons — Ollama learns from Anthropic/OpenAI corrections
# ═══════════════════════════════════════════════════════════════════════

def _load_cloud_fix_store() -> List[Dict]:
    path = _get_cloud_fix_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_cloud_fix_store(entries: List[Dict]):
    path = _get_cloud_fix_path()
    entries = entries[-100:]  # Keep last 100 lessons
    try:
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    except OSError as e:
        logger.error(f"Failed to save cloud fix lessons: {e}")


def record_cloud_fix_lesson(
    *,
    ollama_model: str,
    cloud_model: str,
    user_prompt: str,
    error_summary: str,
    ollama_code: Dict[str, str],
    cloud_code: Dict[str, str],
    issues_fixed: List[str],
):
    """
    Record when a cloud LLM (Anthropic/OpenAI) successfully fixes code
    that Ollama couldn't. These lessons are fed back into Ollama's
    system prompt so it learns to avoid the same mistakes.

    Parameters
    ----------
    ollama_model : str       - Which Ollama model produced the buggy code
    cloud_model : str        - Which cloud model fixed it
    user_prompt : str        - What the user originally asked
    error_summary : str      - Verification errors Ollama couldn't fix
    ollama_code : dict       - {path: content} of Ollama's broken files
    cloud_code : dict        - {path: content} of the cloud's fixed files
    issues_fixed : list      - Human-readable list of what was wrong
    """
    # Extract concise patterns from the diffs
    patterns = _extract_fix_patterns(ollama_code, cloud_code, issues_fixed)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ollama_model": ollama_model,
        "cloud_model": cloud_model,
        "prompt_preview": user_prompt[:120],
        "error_summary": error_summary[:500],
        "issues_fixed": issues_fixed[:10],
        "patterns_learned": patterns,
        "files_fixed": list(cloud_code.keys())[:10],
    }

    store = _load_cloud_fix_store()
    store.append(entry)
    _save_cloud_fix_store(store)
    logger.info(
        f"🎓 Cloud fix lesson recorded: {cloud_model} fixed {len(issues_fixed)} issue(s) "
        f"for {ollama_model} — {len(patterns)} pattern(s) learned"
    )


def _extract_fix_patterns(
    ollama_code: Dict[str, str],
    cloud_code: Dict[str, str],
    issues: List[str],
) -> List[str]:
    """
    Distill the difference between Ollama's broken code and the cloud's
    fix into short, actionable rules Ollama can follow next time.
    """
    patterns = []

    # Extract patterns from the issues themselves
    common_patterns = {
        "indent": "Use consistent indentation (4 spaces for Python, 2 for JS/HTML)",
        "import": "Include all required imports at the top of the file",
        "syntax": "Ensure all brackets, parentheses, and quotes are properly closed",
        "undefined": "Define all variables and functions before using them",
        "async": "Use 'await' with all async function calls",
        "return": "Ensure all code paths return the correct type",
        "missing": "Include ALL files the project needs, not just the main file",
        "encoding": "Use UTF-8 encoding and proper string escaping",
        "semicolon": "Add semicolons at end of statements in JavaScript",
        "colon": "Add colons after function/class/if/for/while definitions in Python",
    }

    for issue in issues:
        issue_lower = issue.lower()
        for keyword, rule in common_patterns.items():
            if keyword in issue_lower and rule not in patterns:
                patterns.append(rule)

    # Check for missing files (cloud added files Ollama didn't)
    ollama_files = set(ollama_code.keys())
    cloud_files = set(cloud_code.keys())
    added_files = cloud_files - ollama_files
    if added_files:
        exts = {Path(f).suffix for f in added_files}
        patterns.append(
            f"Include all project files — cloud had to add: {', '.join(sorted(added_files)[:5])}"
        )

    return patterns[:10]  # Cap at 10 patterns per lesson


def get_cloud_fix_lessons(limit: int = 10) -> List[Dict]:
    """Get recent cloud-fix lessons."""
    store = _load_cloud_fix_store()
    return store[-limit:]


def _build_cloud_fix_lessons() -> str:
    """
    Build a concise block of cloud-fix lessons for injection into
    Ollama's system prompt. Deduplicates and prioritizes the most
    common patterns.
    """
    lessons = get_cloud_fix_lessons(limit=20)
    if not lessons:
        return ""

    # Count pattern frequency to surface the most important ones
    pattern_counts: Dict[str, int] = {}
    for lesson in lessons:
        for pattern in lesson.get("patterns_learned", []):
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    if not pattern_counts:
        return ""

    # Sort by frequency (most common patterns = most important lessons)
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])

    lines = [
        "## Lessons from Cloud LLM Corrections (CRITICAL)",
        "A more advanced model fixed these recurring mistakes in YOUR code.",
        "Follow these rules to avoid the same errors:\n",
    ]
    for pattern, count in sorted_patterns[:10]:
        freq = f" (×{count})" if count > 1 else ""
        lines.append(f"- {pattern}{freq}")

    return "\n".join(lines)
