"""
Synthesized Tools — dynamically created at runtime by Phase 51.

When the AutonomousLoop determines that a required tool doesn't exist,
the ToolSynthesizer generates it, writes it here, and registers it
so the retry can succeed.

Layout:
    synthesized/
        __init__.py        <- This file (registry)
        generated/         <- Runtime-created tool modules
            __init__.py
            <tool_name>.py <- Each synthesized tool
"""

import importlib
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

SYNTHESIZED_DIR = Path(__file__).resolve().parent / "generated"

_registry: Dict[str, dict] = {}  # tool_name -> {module, func, spec}


def register_tool(name: str, module_path: str, func_name: str, spec: dict) -> None:
    """Register a synthesized tool so it can be discovered."""
    _registry[name] = {
        "module_path": module_path,
        "func_name": func_name,
        "spec": spec,
    }
    logger.info(f"[SynthesizedTools] Registered tool: {name}")


def get_tool(name: str) -> Optional[dict]:
    """Look up a registered synthesized tool."""
    return _registry.get(name)


def list_tools() -> Dict[str, dict]:
    """Return all registered synthesized tools."""
    return dict(_registry)


def load_persisted_tools() -> int:
    """
    Scan generated/ for tool modules with a TOOL_SPEC attribute
    and register them. Called once at startup.
    """
    count = 0
    if not SYNTHESIZED_DIR.exists():
        return 0

    for py_file in SYNTHESIZED_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tool_name = py_file.stem
        try:
            mod = importlib.import_module(
                f"src.tools.synthesized.generated.{tool_name}"
            )
            spec = getattr(mod, "TOOL_SPEC", None)
            if spec and isinstance(spec, dict):
                func_name = spec.get("func_name", "run")
                register_tool(
                    tool_name,
                    f"src.tools.synthesized.generated.{tool_name}",
                    func_name,
                    spec,
                )
                count += 1
        except Exception as e:
            logger.warning(f"[SynthesizedTools] Could not load {py_file.name}: {e}")
    return count
