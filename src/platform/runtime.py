"""
Cross-Platform Runtime Resolver

Detects the host OS and resolves paths for embedded Python, Node.js, and Ollama
runtimes on Windows, macOS, and Linux.  Each finder checks platform-specific
embedded paths first, then falls back to the system PATH.
"""

import os
import sys
import shutil
import platform as _platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Platform constants ──────────────────────────────────────────────────────

PLATFORM = sys.platform                         # win32 | darwin | linux
ARCH = "arm64" if _platform.machine() in ("aarch64", "arm64") else "x64"
IS_WINDOWS = PLATFORM == "win32"
IS_MAC = PLATFORM == "darwin"
IS_LINUX = PLATFORM.startswith("linux")
PLATFORM_TAG = f"{'darwin' if IS_MAC else 'linux' if IS_LINUX else 'win32'}-{ARCH}"

# Executable suffix
EXE = ".exe" if IS_WINDOWS else ""


# ── Path helpers ────────────────────────────────────────────────────────────

def _first_existing(*candidates: Path) -> Optional[Path]:
    """Return the first path that exists on disk, or None."""
    for p in candidates:
        if p.exists():
            return p
    return None


def _which(name: str) -> Optional[Path]:
    """Thin wrapper around shutil.which that returns a Path."""
    found = shutil.which(name)
    return Path(found) if found else None


def _run_version(exe: Path, timeout: int = 5) -> Optional[str]:
    """Execute *exe --version* and return the stripped stdout."""
    try:
        r = subprocess.run(
            [str(exe), "--version"],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


# ── Python ──────────────────────────────────────────────────────────────────

def find_python() -> Dict[str, Any]:
    """Resolve the best Python interpreter."""
    rt = PROJECT_ROOT / "runtime"

    candidates = [
        # Windows embedded
        rt / "python" / "python.exe",
        rt / "win32-x64" / "python" / "python.exe",
        # macOS / Linux embedded
        rt / f"{PLATFORM_TAG}" / "python" / "bin" / "python3",
        rt / "python" / "bin" / "python3",
    ]
    embedded = _first_existing(*candidates)
    if embedded:
        return {"path": embedded, "embedded": True, "version": _run_version(embedded)}

    system = _which("python3") or _which("python")
    if system:
        return {"path": system, "embedded": False, "version": _run_version(system)}

    return {"path": Path(sys.executable), "embedded": False, "version": sys.version.split()[0]}


# ── Node.js ─────────────────────────────────────────────────────────────────

def find_node() -> Dict[str, Any]:
    """Resolve the best Node.js binary."""
    rt = PROJECT_ROOT / "runtime"

    candidates = [
        # Windows embedded
        rt / "node" / f"node{EXE}",
        rt / "win32-x64" / "node" / f"node{EXE}",
        # macOS / Linux embedded (bin/ layout)
        rt / f"{PLATFORM_TAG}" / "node" / "bin" / "node",
        rt / "node" / "bin" / "node",
    ]
    embedded = _first_existing(*candidates)
    if embedded:
        return {"path": embedded, "embedded": True, "version": _run_version(embedded)}

    system = _which("node")
    if system:
        return {"path": system, "embedded": False, "version": _run_version(system)}

    return {"path": None, "embedded": False, "version": None}


def find_npm() -> Dict[str, Any]:
    """Resolve npm (or npx) — follows the same Node location."""
    node_info = find_node()
    if node_info["path"] and node_info["embedded"]:
        node_dir = node_info["path"].parent
        # Windows: npx.cmd / npm.cmd sit next to node.exe
        if IS_WINDOWS:
            npm = node_dir / "npm.cmd"
            npx = node_dir / "npx.cmd"
        else:
            npm = node_dir / "npm"
            npx = node_dir / "npx"
        return {"npm": npm if npm.exists() else _which("npm"), "npx": npx if npx.exists() else _which("npx")}

    return {"npm": _which("npm"), "npx": _which("npx")}


# ── Ollama ──────────────────────────────────────────────────────────────────

def find_ollama() -> Dict[str, Any]:
    """Resolve the Ollama binary."""
    rt = PROJECT_ROOT / "runtime"

    candidates = [
        rt / "ollama" / f"ollama{EXE}",
        rt / f"{PLATFORM_TAG}" / "ollama" / f"ollama{EXE}",
    ]
    embedded = _first_existing(*candidates)
    if embedded:
        return {"path": embedded, "embedded": True, "version": _run_version(embedded)}

    system = _which("ollama")
    if system:
        return {"path": system, "embedded": False, "version": _run_version(system)}

    return {"path": None, "embedded": False, "version": None}


# ── Convenience ─────────────────────────────────────────────────────────────

def platform_summary() -> Dict[str, Any]:
    """Return a quick snapshot of the host and detected runtimes."""
    return {
        "os": PLATFORM,
        "arch": ARCH,
        "platform_tag": PLATFORM_TAG,
        "machine": _platform.machine(),
        "hostname": _platform.node(),
        "python": find_python(),
        "node": find_node(),
        "ollama": find_ollama(),
    }
