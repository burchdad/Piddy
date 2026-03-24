"""
Piddy Self-Diagnosis System (/api/doctor)

Comprehensive health checks for plug-and-play portability:
- Runtime detection (Python, Node.js)
- API key validation
- Database connectivity
- Ollama local LLM availability
- Port availability
- Dependency verification
- Disk space check
"""

import logging
import os
import sys
import shutil
import socket
import sqlite3
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _check_runtime_python() -> Dict[str, Any]:
    """Check Python runtime."""
    return {
        "name": "Python Runtime",
        "status": "ok",
        "version": sys.version.split()[0],
        "executable": sys.executable,
        "embedded": "runtime" in sys.executable.replace("\\", "/").lower(),
    }


def _check_runtime_node() -> Dict[str, Any]:
    """Check Node.js runtime."""
    import subprocess
    
    # Check platform-specific embedded paths
    node_paths = []
    if sys.platform == "win32":
        node_paths.append(PROJECT_ROOT / "runtime" / "node" / "node.exe")
        node_paths.append(PROJECT_ROOT / "runtime" / "win32-x64" / "node" / "node.exe")
    else:
        import platform as plat
        arch = "arm64" if plat.machine() in ("aarch64", "arm64") else "x64"
        os_name = "darwin" if sys.platform == "darwin" else "linux"
        node_paths.append(PROJECT_ROOT / "runtime" / f"{os_name}-{arch}" / "node" / "bin" / "node")
        node_paths.append(PROJECT_ROOT / "runtime" / "node" / "bin" / "node")
    
    for node_path in node_paths:
        if node_path.exists():
            try:
                result = subprocess.run(
                    [str(node_path), "--version"],
                    capture_output=True, text=True, timeout=5
                )
                return {
                    "name": "Node.js Runtime",
                    "status": "ok",
                    "version": result.stdout.strip(),
                    "path": str(node_path),
                    "embedded": True,
                }
            except Exception:
                pass
    
    # Try system node
    node_cmd = shutil.which("node")
    if node_cmd:
        try:
            result = subprocess.run(
                [node_cmd, "--version"],
                capture_output=True, text=True, timeout=5
            )
            return {
                "name": "Node.js Runtime",
                "status": "warn",
                "version": result.stdout.strip(),
                "path": node_cmd,
                "embedded": False,
                "message": "Using system Node.js (not embedded)",
            }
        except Exception:
            pass
    
    return {
        "name": "Node.js Runtime",
        "status": "warn",
        "message": "Node.js not found — frontend may not work",
    }


def _check_database() -> Dict[str, Any]:
    """Check SQLite database connectivity."""
    db_path = PROJECT_ROOT / "piddy.db"
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        return {
            "name": "Database (SQLite)",
            "status": "ok",
            "version": version,
            "path": str(db_path),
            "exists": db_path.exists(),
        }
    except Exception as e:
        return {
            "name": "Database (SQLite)",
            "status": "error",
            "message": str(e),
        }


def _check_api_keys() -> Dict[str, Any]:
    """Check API key configuration."""
    try:
        from src.config.key_manager import keys_configured, get_config_status
        status = get_config_status()
        configured = status.get("configured_providers", [])
        if not configured:
            # Fallback: derive from keys dict
            configured = [k for k, v in status.get("keys", {}).items() if v]
        return {
            "name": "API Keys",
            "status": "ok" if configured else "warn",
            "configured": configured,
            "message": f"{len(configured)} provider(s) configured" if configured else "No API keys configured — configure in Settings",
        }
    except Exception:
        # Fall back to .env check
        from config.settings import get_settings
        settings = get_settings()
        providers = []
        if settings.anthropic_api_key:
            providers.append("anthropic")
        if settings.openai_api_key:
            providers.append("openai")
        return {
            "name": "API Keys",
            "status": "ok" if providers else "warn",
            "configured": providers,
            "message": f"{len(providers)} provider(s) configured" if providers else "No API keys — set in .env or Settings",
        }


def _check_ollama() -> Dict[str, Any]:
    """Check Ollama local LLM availability."""
    from config.settings import get_settings
    settings = get_settings()
    
    if not settings.ollama_enabled:
        return {
            "name": "Ollama (Local LLM)",
            "status": "skip",
            "message": "Ollama disabled in settings",
        }
    
    try:
        import urllib.request
        url = f"{settings.ollama_base_url}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            import json
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            has_configured = settings.ollama_model in models
            return {
                "name": "Ollama (Local LLM)",
                "status": "ok" if has_configured else "warn",
                "url": settings.ollama_base_url,
                "models_available": models[:10],
                "configured_model": settings.ollama_model,
                "model_ready": has_configured,
                "message": f"Model '{settings.ollama_model}' ready" if has_configured else f"Model '{settings.ollama_model}' not pulled — run: ollama pull {settings.ollama_model}",
            }
    except Exception:
        return {
            "name": "Ollama (Local LLM)",
            "status": "warn",
            "url": settings.ollama_base_url,
            "message": "Ollama not running — install from ollama.com for free local AI",
        }


def _check_env_file() -> Dict[str, Any]:
    """Check .env configuration file."""
    env_path = PROJECT_ROOT / ".env"
    example_path = PROJECT_ROOT / ".env.example"
    return {
        "name": "Environment Config",
        "status": "ok" if env_path.exists() else "warn",
        "env_exists": env_path.exists(),
        "example_exists": example_path.exists(),
        "message": "Configuration loaded" if env_path.exists() else "No .env file — defaults will be used",
    }


def _check_frontend() -> Dict[str, Any]:
    """Check frontend build status."""
    dist_path = PROJECT_ROOT / "frontend" / "dist"
    index_path = dist_path / "index.html"
    if index_path.exists():
        return {
            "name": "Frontend (React)",
            "status": "ok",
            "built": True,
            "path": str(dist_path),
        }
    elif (PROJECT_ROOT / "frontend" / "package.json").exists():
        return {
            "name": "Frontend (React)",
            "status": "warn",
            "built": False,
            "message": "Frontend not built — run: cd frontend && npm run build",
        }
    return {
        "name": "Frontend (React)",
        "status": "error",
        "message": "Frontend directory not found",
    }


def _check_dependencies() -> Dict[str, Any]:
    """Check critical Python dependencies."""
    deps = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "langchain": "langchain",
        "langchain_anthropic": "langchain_anthropic",
        "langchain_openai": "langchain_openai",
        "cryptography": "cryptography",
    }
    
    installed = []
    missing = []
    for name, module in deps.items():
        try:
            importlib.import_module(module)
            installed.append(name)
        except ImportError:
            missing.append(name)
    
    return {
        "name": "Python Dependencies",
        "status": "ok" if not missing else "error",
        "installed": len(installed),
        "missing": missing if missing else None,
        "message": f"{len(installed)} packages OK" if not missing else f"Missing: {', '.join(missing)}",
    }


def _check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    try:
        usage = shutil.disk_usage(str(PROJECT_ROOT))
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        return {
            "name": "Disk Space",
            "status": "ok" if free_gb > 1.0 else ("warn" if free_gb > 0.2 else "error"),
            "free_gb": round(free_gb, 1),
            "total_gb": round(total_gb, 1),
            "message": f"{round(free_gb, 1)} GB free" if free_gb > 1.0 else "Low disk space!",
        }
    except Exception as e:
        return {"name": "Disk Space", "status": "error", "message": str(e)}


def _check_ports() -> Dict[str, Any]:
    """Check if key ports are available."""
    ports_to_check = [8000, 8001, 8080]
    results = {}
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                results[port] = "available"
        except OSError:
            results[port] = "in-use"
    
    all_busy = all(v == "in-use" for v in results.values())
    return {
        "name": "Network Ports",
        "status": "ok" if not all_busy else "warn",
        "ports": results,
        "message": "Auto port detection enabled" if all_busy else None,
    }


def _check_knowledge_base() -> Dict[str, Any]:
    """Check knowledge base population (library/)."""
    lib_root = PROJECT_ROOT / "library"
    if not lib_root.exists():
        return {"name": "Knowledge Base", "status": "warn", "message": "library/ directory not found"}
    categories = {}
    total = 0
    for folder in sorted(lib_root.iterdir()):
        if folder.is_dir():
            count = sum(1 for f in folder.iterdir() if f.is_file())
            categories[folder.name] = count
            total += count
    return {
        "name": "Knowledge Base",
        "status": "ok" if total > 0 else "warn",
        "categories": categories,
        "total_files": total,
        "message": f"{total} KB files across {len(categories)} categories" if total else "Knowledge base is empty",
    }


def _check_agents() -> Dict[str, Any]:
    """Check agent initialization via coordinator."""
    try:
        from src.coordination.agent_coordinator import get_coordinator
        coordinator = get_coordinator()
        agents = coordinator.get_all_agents()
        online = [a for a in agents if getattr(a, "is_available", False)]
        return {
            "name": "Agent System",
            "status": "ok" if len(agents) >= 15 else ("warn" if agents else "error"),
            "total_registered": len(agents),
            "online": len(online),
            "message": f"{len(agents)} agents registered, {len(online)} online",
        }
    except Exception as e:
        return {"name": "Agent System", "status": "warn", "message": f"Could not query agents: {e}"}


def _check_frontend_dev() -> Dict[str, Any]:
    """Check if Vite dev server is reachable (dev mode only)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", 5173))
            return {"name": "Frontend Dev Server", "status": "ok", "port": 5173, "message": "Vite dev server running"}
    except (OSError, socket.timeout):
        return {"name": "Frontend Dev Server", "status": "skip", "message": "Vite dev server not running (production build used)"}


def _check_discord() -> Dict[str, Any]:
    """Check Discord bot configuration and library."""
    try:
        import discord  # type: ignore[import-unresolved]
        lib_ok = True
        lib_ver = discord.__version__
    except ImportError:
        lib_ok = False
        lib_ver = None

    from config.settings import get_settings
    settings = get_settings()
    token_set = bool(settings.discord_bot_token)

    if not lib_ok:
        return {"name": "Discord Bot", "status": "warn", "library": False, "token_configured": token_set,
                "message": "discord.py not installed — pip install discord.py"}
    if not token_set:
        return {"name": "Discord Bot", "status": "skip", "library": True, "library_version": lib_ver,
                "token_configured": False, "message": "No token — set DISCORD_BOT_TOKEN in .env"}
    return {"name": "Discord Bot", "status": "ok", "library": True, "library_version": lib_ver,
            "token_configured": True, "message": "Ready"}


def _check_telegram() -> Dict[str, Any]:
    """Check Telegram bot configuration and library."""
    try:
        import telegram  # type: ignore[import-unresolved]
        lib_ok = True
        lib_ver = telegram.__version__
    except ImportError:
        lib_ok = False
        lib_ver = None

    from config.settings import get_settings
    settings = get_settings()
    token_set = bool(settings.telegram_bot_token)

    if not lib_ok:
        return {"name": "Telegram Bot", "status": "warn", "library": False, "token_configured": token_set,
                "message": "python-telegram-bot not installed — pip install python-telegram-bot"}
    if not token_set:
        return {"name": "Telegram Bot", "status": "skip", "library": True, "library_version": lib_ver,
                "token_configured": False, "message": "No token — set TELEGRAM_BOT_TOKEN in .env"}
    return {"name": "Telegram Bot", "status": "ok", "library": True, "library_version": lib_ver,
            "token_configured": True, "message": "Ready"}


def _check_playwright() -> Dict[str, Any]:
    """Check Playwright browser automation availability."""
    try:
        from playwright.async_api import async_playwright  # type: ignore[import-unresolved]
        lib_ok = True
    except ImportError:
        lib_ok = False

    if not lib_ok:
        return {"name": "Browser Automation", "status": "warn", "library": False,
                "message": "playwright not installed — pip install playwright && playwright install chromium"}

    # Check if chromium is downloaded
    browsers_installed = False
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", "from playwright.sync_api import sync_playwright; b=sync_playwright().start(); br=b.chromium.launch(headless=True); br.close(); b.stop(); print('ok')"],
            capture_output=True, text=True, timeout=15,
        )
        browsers_installed = result.stdout.strip() == "ok"
    except Exception:
        pass

    if not browsers_installed:
        return {"name": "Browser Automation", "status": "warn", "library": True, "browsers_installed": False,
                "message": "Chromium not installed — run: playwright install chromium"}
    return {"name": "Browser Automation", "status": "ok", "library": True, "browsers_installed": True,
            "message": "Playwright + Chromium ready"}


def _check_productivity() -> Dict[str, Any]:
    """Check productivity connector configuration (Calendar, Jira, Notion)."""
    from config.settings import get_settings
    settings = get_settings()

    connectors = {}
    if settings.google_calendar_api_key:
        connectors["google_calendar"] = True
    if settings.jira_base_url and settings.jira_api_token:
        connectors["jira"] = True
    if settings.notion_api_token:
        connectors["notion"] = True

    count = len(connectors)
    if count == 0:
        return {"name": "Productivity Connectors", "status": "skip", "configured": connectors,
                "message": "No connectors configured — set tokens in .env"}
    return {"name": "Productivity Connectors", "status": "ok", "configured": connectors,
            "message": f"{count} connector(s) configured"}


def run_diagnosis() -> Dict[str, Any]:
    """Run full system diagnosis. Returns structured report."""
    checks = [
        _check_runtime_python(),
        _check_runtime_node(),
        _check_database(),
        _check_api_keys(),
        _check_ollama(),
        _check_env_file(),
        _check_frontend(),
        _check_dependencies(),
        _check_disk_space(),
        _check_ports(),
        _check_knowledge_base(),
        _check_agents(),
        _check_frontend_dev(),
        _check_discord(),
        _check_telegram(),
        _check_playwright(),
        _check_productivity(),
    ]
    
    errors = sum(1 for c in checks if c.get("status") == "error")
    warnings = sum(1 for c in checks if c.get("status") == "warn")
    ok = sum(1 for c in checks if c.get("status") == "ok")
    
    if errors > 0:
        overall = "unhealthy"
    elif warnings > 0:
        overall = "degraded"
    else:
        overall = "healthy"
    
    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "platform": sys.platform,
        "checks": checks,
        "summary": {
            "ok": ok,
            "warnings": warnings,
            "errors": errors,
            "total": len(checks),
        },
    }
