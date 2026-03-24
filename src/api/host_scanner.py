"""
Universal Diagnostics Engine

Scans the HOST machine Piddy is plugged into — not just Piddy itself.
Detects installed software, analyzes repos, and suggests fixes.

Endpoints served via dashboard_api.py:
  GET  /api/scan/host          → host software inventory
  POST /api/scan/repo          → analyze a local repository
  GET  /api/scan/programs       → list installed programs
"""

import os
import sys
import shutil
import subprocess
import platform as _platform
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Host Environment Scanner ────────────────────────────────────────────────

def scan_host() -> Dict[str, Any]:
    """Produce a full snapshot of the machine Piddy is plugged into."""
    from src.platform.runtime import PLATFORM, ARCH, IS_WINDOWS, IS_MAC

    info: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "os": {
            "platform": PLATFORM,
            "arch": ARCH,
            "machine": _platform.machine(),
            "hostname": _platform.node(),
            "version": _platform.version(),
            "release": _platform.release(),
        },
        "hardware": _scan_hardware(),
        "runtimes": _scan_runtimes(),
        "network": _scan_network(),
        "disk": _scan_disks(),
        "installed_tools": _scan_dev_tools(),
    }
    return info


def _scan_hardware() -> Dict[str, Any]:
    try:
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
    except Exception:
        cpu_count = os.cpu_count() or 0

    mem_gb = None
    try:
        if sys.platform == "win32":
            r = subprocess.run(
                ["wmic", "OS", "get", "TotalVisibleMemorySize", "/value"],
                capture_output=True, text=True, timeout=5,
            )
            for line in r.stdout.splitlines():
                if "TotalVisibleMemorySize" in line:
                    mem_gb = round(int(line.split("=")[1].strip()) / (1024 * 1024), 1)
        else:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        mem_gb = round(int(line.split()[1]) / (1024 * 1024), 1)
                        break
    except Exception:
        pass

    return {"cpu_cores": cpu_count, "ram_gb": mem_gb, "processor": _platform.processor()}


def _scan_disks() -> List[Dict[str, Any]]:
    disks = []
    seen_mounts = set()

    # On Windows, enumerate all drive letters
    if sys.platform == "win32":
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            try:
                usage = shutil.disk_usage(drive)
                if usage.total == 0:
                    continue
                disks.append({
                    "mount": drive,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "used_pct": round((usage.used / usage.total) * 100, 1),
                })
                seen_mounts.add(drive)
            except (OSError, PermissionError):
                continue
    else:
        # Unix: check / and the project root's mount
        for path in ["/", str(PROJECT_ROOT)]:
            mount = str(Path(path).anchor)
            if mount in seen_mounts:
                continue
            try:
                usage = shutil.disk_usage(path)
                disks.append({
                    "mount": mount,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "used_pct": round((usage.used / usage.total) * 100, 1),
                })
                seen_mounts.add(mount)
            except Exception:
                continue

    return disks


def _scan_network() -> Dict[str, Any]:
    import socket
    internet = False
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3).close()
        internet = True
    except Exception:
        pass
    return {
        "hostname": socket.gethostname(),
        "internet_available": internet,
    }


def _scan_runtimes() -> Dict[str, Any]:
    """Detect which dev runtimes are installed on the HOST."""
    runtimes: Dict[str, Any] = {}
    tool_list = [
        ("python3", "python"),
        ("node", None),
        ("npm", None),
        ("git", None),
        ("docker", None),
        ("java", None),
        ("javac", None),
        ("go", None),
        ("rustc", None),
        ("cargo", None),
        ("ruby", None),
        ("php", None),
        ("dotnet", None),
        ("gcc", None),
        ("g++", None),
        ("make", None),
        ("cmake", None),
        ("curl", None),
        ("wget", None),
        ("ssh", None),
        ("ollama", None),
    ]
    for primary, fallback in tool_list:
        exe = shutil.which(primary) or (shutil.which(fallback) if fallback else None)
        if exe:
            ver = None
            try:
                r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
                ver = r.stdout.strip().split("\n")[0][:120]
            except Exception:
                pass
            runtimes[primary] = {"path": exe, "version": ver}
    return runtimes


def _scan_dev_tools() -> List[Dict[str, str]]:
    """Quick inventory of key development tools present on the host."""
    tools_found = []
    check = [
        ("git", "Version Control"),
        ("docker", "Containers"),
        ("code", "VS Code"),
        ("cursor", "Cursor Editor"),
        ("vim", "Vim Editor"),
        ("nano", "Nano Editor"),
        ("kubectl", "Kubernetes CLI"),
        ("terraform", "Infrastructure as Code"),
        ("ansible", "Automation"),
        ("pip", "Python Package Manager"),
        ("conda", "Conda Package Manager"),
        ("yarn", "Yarn Package Manager"),
        ("pnpm", "PNPM Package Manager"),
        ("nginx", "Web Server"),
        ("psql", "PostgreSQL Client"),
        ("mysql", "MySQL Client"),
        ("redis-cli", "Redis Client"),
        ("sqlite3", "SQLite CLI"),
        ("ffmpeg", "Media Processing"),
        ("aws", "AWS CLI"),
        ("gcloud", "Google Cloud CLI"),
        ("az", "Azure CLI"),
        ("heroku", "Heroku CLI"),
    ]
    for name, desc in check:
        if shutil.which(name):
            tools_found.append({"name": name, "category": desc})
    return tools_found


# ── Repository Analyzer ─────────────────────────────────────────────────────

def analyze_repo(repo_path: str) -> Dict[str, Any]:
    """
    Analyze any local repository.  Returns language breakdown, dependency
    health, git status, and actionable recommendations.
    """
    rp = Path(repo_path).resolve()
    if not rp.is_dir():
        return {"error": f"Path not found: {repo_path}"}

    result: Dict[str, Any] = {
        "path": str(rp),
        "timestamp": datetime.utcnow().isoformat(),
        "languages": _detect_languages(rp),
        "structure": _scan_structure(rp),
        "git": _scan_git(rp),
        "dependencies": _scan_dependencies(rp),
        "issues": [],
        "recommendations": [],
    }

    # Build recommendations
    _generate_recommendations(result)
    return result


def _detect_languages(rp: Path) -> Dict[str, int]:
    """Count files by extension to determine language breakdown."""
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "React JSX", ".tsx": "React TSX", ".java": "Java",
        ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
        ".cs": "C#", ".cpp": "C++", ".c": "C", ".swift": "Swift",
        ".kt": "Kotlin", ".sh": "Shell", ".sql": "SQL",
        ".html": "HTML", ".css": "CSS", ".json": "JSON",
        ".yml": "YAML", ".yaml": "YAML", ".md": "Markdown",
        ".toml": "TOML", ".xml": "XML",
    }
    counts: Dict[str, int] = {}
    try:
        for f in rp.rglob("*"):
            if f.is_file() and not _is_ignored(f, rp):
                lang = ext_map.get(f.suffix.lower())
                if lang:
                    counts[lang] = counts.get(lang, 0) + 1
    except Exception:
        pass
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def _is_ignored(f: Path, root: Path) -> bool:
    """Skip common directories that bloat counts."""
    parts = f.relative_to(root).parts
    skip = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build", ".tox", "target", "vendor"}
    return bool(skip.intersection(parts))


def _scan_structure(rp: Path) -> Dict[str, Any]:
    """High-level directory structure."""
    top_dirs = sorted([d.name for d in rp.iterdir() if d.is_dir() and not d.name.startswith(".")])[:30]
    top_files = sorted([f.name for f in rp.iterdir() if f.is_file()])[:30]
    total_files = sum(1 for _ in rp.rglob("*") if _.is_file() and not _is_ignored(_, rp))
    return {"directories": top_dirs, "root_files": top_files, "total_files": total_files}


def _scan_git(rp: Path) -> Optional[Dict[str, Any]]:
    """Read git information if available."""
    if not (rp / ".git").exists():
        return None
    info: Dict[str, Any] = {"initialized": True}
    try:
        def _git(*args):
            r = subprocess.run(
                ["git", *args], capture_output=True, text=True,
                cwd=str(rp), timeout=10,
            )
            return r.stdout.strip() if r.returncode == 0 else None

        info["branch"] = _git("rev-parse", "--abbrev-ref", "HEAD")
        info["last_commit"] = _git("log", "-1", "--pretty=format:%h %s")
        info["commit_date"] = _git("log", "-1", "--pretty=format:%ci")

        status = _git("status", "--porcelain")
        if status is not None:
            lines = [l for l in status.split("\n") if l.strip()]
            info["uncommitted_changes"] = len(lines)
            info["clean"] = len(lines) == 0
        else:
            info["uncommitted_changes"] = None

        remote = _git("remote", "get-url", "origin")
        info["remote"] = remote

    except Exception as e:
        info["error"] = str(e)
    return info


def _scan_dependencies(rp: Path) -> Dict[str, Any]:
    """Detect and summarize dependency manifests."""
    deps: Dict[str, Any] = {}

    # Python
    req = rp / "requirements.txt"
    if req.exists():
        lines = [l.strip() for l in req.read_text(errors="replace").splitlines() if l.strip() and not l.startswith("#")]
        deps["python_requirements"] = {"file": "requirements.txt", "count": len(lines), "packages": lines[:20]}
    pyproject = rp / "pyproject.toml"
    if pyproject.exists():
        deps["python_pyproject"] = {"file": "pyproject.toml", "exists": True}
    setup_py = rp / "setup.py"
    if setup_py.exists():
        deps["python_setup"] = {"file": "setup.py", "exists": True}

    # Node
    pkg = rp / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(errors="replace"))
            dev = data.get("devDependencies", {})
            prod = data.get("dependencies", {})
            deps["node"] = {
                "file": "package.json",
                "name": data.get("name"),
                "version": data.get("version"),
                "dependencies": len(prod),
                "devDependencies": len(dev),
            }
            # Check for lock file
            lock = None
            for lf in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
                if (rp / lf).exists():
                    lock = lf
                    break
            deps["node"]["lock_file"] = lock
        except Exception:
            deps["node"] = {"file": "package.json", "error": "parse failed"}

    # Go
    if (rp / "go.mod").exists():
        deps["go"] = {"file": "go.mod", "exists": True}

    # Rust
    if (rp / "Cargo.toml").exists():
        deps["rust"] = {"file": "Cargo.toml", "exists": True}

    # Docker
    if (rp / "Dockerfile").exists():
        deps["docker"] = {"file": "Dockerfile", "exists": True}
    if (rp / "docker-compose.yml").exists():
        deps["docker_compose"] = True

    return deps


def _generate_recommendations(result: Dict[str, Any]):
    """Produce actionable recommendations based on scan results."""
    recs = result["recommendations"]
    issues = result["issues"]

    git = result.get("git")
    if git is None:
        issues.append({"severity": "warn", "msg": "No git repository detected"})
        recs.append("Initialize a git repo: git init")
    elif git.get("uncommitted_changes", 0) > 20:
        issues.append({"severity": "warn", "msg": f"{git['uncommitted_changes']} uncommitted changes"})
        recs.append("Large number of uncommitted changes — consider committing or stashing")
    elif git and not git.get("clean", True):
        recs.append(f"Repository has {git.get('uncommitted_changes', '?')} uncommitted changes")

    deps = result.get("dependencies", {})

    # Node without lock file
    node = deps.get("node")
    if node and not node.get("lock_file"):
        issues.append({"severity": "warn", "msg": "No lock file found (package-lock.json / yarn.lock)"})
        recs.append("Run npm install to generate a lock file for reproducible builds")

    # Python without requirements.txt
    langs = result.get("languages", {})
    if langs.get("Python", 0) > 5 and "python_requirements" not in deps and "python_pyproject" not in deps:
        issues.append({"severity": "warn", "msg": "Python project has no requirements.txt or pyproject.toml"})
        recs.append("Create a requirements.txt: pip freeze > requirements.txt")

    # No README
    struct = result.get("structure", {})
    root_files = [f.lower() for f in struct.get("root_files", [])]
    if not any(f.startswith("readme") for f in root_files):
        issues.append({"severity": "info", "msg": "No README file found"})
        recs.append("Add a README.md to document the project")

    # No .gitignore
    if ".gitignore" not in struct.get("root_files", []):
        recs.append("Add a .gitignore to avoid committing build artifacts")

    # Docker without .dockerignore
    if deps.get("docker") and ".dockerignore" not in struct.get("root_files", []):
        recs.append("Add a .dockerignore to keep Docker images lean")

    # No tests directory
    dirs = struct.get("directories", [])
    if not any(d in ("tests", "test", "__tests__", "spec") for d in dirs):
        issues.append({"severity": "info", "msg": "No tests directory found"})
        recs.append("Consider adding a tests/ directory with unit tests")

    # No CI config
    if not any(d in (".github", ".gitlab-ci.yml", ".circleci") for d in dirs + struct.get("root_files", [])):
        recs.append("Consider adding CI/CD (e.g. .github/workflows/) for automated testing")


# ── Installed Programs Scanner (Windows / macOS / Linux) ────────────────────

def scan_installed_programs() -> List[Dict[str, str]]:
    """Return a list of installed programs on the host OS."""
    if sys.platform == "win32":
        return _scan_programs_windows()
    elif sys.platform == "darwin":
        return _scan_programs_mac()
    else:
        return _scan_programs_linux()


def _scan_programs_windows() -> List[Dict[str, str]]:
    programs = []
    try:
        r = subprocess.run(
            ["powershell", "-Command",
             "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* "
             "| Select-Object DisplayName, DisplayVersion, Publisher "
             "| Where-Object { $_.DisplayName -ne $null } "
             "| ConvertTo-Json -Depth 1"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                programs.append({
                    "name": str(item.get("DisplayName", "")),
                    "version": str(item.get("DisplayVersion", "")),
                    "publisher": str(item.get("Publisher", "")),
                })
    except Exception as e:
        logger.warning("Program scan failed: %s", e)
    return sorted(programs, key=lambda p: p["name"].lower())


def _scan_programs_mac() -> List[Dict[str, str]]:
    programs = []
    apps_dir = Path("/Applications")
    if apps_dir.exists():
        for app in sorted(apps_dir.glob("*.app")):
            plist = app / "Contents" / "Info.plist"
            version = ""
            if plist.exists():
                try:
                    r = subprocess.run(
                        ["defaults", "read", str(plist), "CFBundleShortVersionString"],
                        capture_output=True, text=True, timeout=3,
                    )
                    version = r.stdout.strip() if r.returncode == 0 else ""
                except Exception:
                    pass
            programs.append({"name": app.stem, "version": version, "publisher": ""})
    # Also check Homebrew
    brew = shutil.which("brew")
    if brew:
        try:
            r = subprocess.run([brew, "list", "--versions"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.strip().splitlines():
                parts = line.split()
                if parts:
                    programs.append({"name": parts[0], "version": " ".join(parts[1:]), "publisher": "homebrew"})
        except Exception:
            pass
    return programs


def _scan_programs_linux() -> List[Dict[str, str]]:
    programs = []
    # Try dpkg (Debian/Ubuntu)
    dpkg = shutil.which("dpkg")
    if dpkg:
        try:
            r = subprocess.run(
                [dpkg, "-l"],
                capture_output=True, text=True, timeout=10,
            )
            for line in r.stdout.splitlines():
                if line.startswith("ii"):
                    parts = line.split()
                    if len(parts) >= 3:
                        programs.append({"name": parts[1], "version": parts[2], "publisher": ""})
        except Exception:
            pass
        return sorted(programs, key=lambda p: p["name"])

    # Try rpm (RHEL/Fedora)
    rpm = shutil.which("rpm")
    if rpm:
        try:
            r = subprocess.run(
                [rpm, "-qa", "--queryformat", "%{NAME}|%{VERSION}\\n"],
                capture_output=True, text=True, timeout=10,
            )
            for line in r.stdout.strip().splitlines():
                if "|" in line:
                    name, ver = line.split("|", 1)
                    programs.append({"name": name, "version": ver, "publisher": ""})
        except Exception:
            pass
        return sorted(programs, key=lambda p: p["name"])

    # Fallback: pacman (Arch)
    pacman = shutil.which("pacman")
    if pacman:
        try:
            r = subprocess.run([pacman, "-Q"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    programs.append({"name": parts[0], "version": parts[1], "publisher": ""})
        except Exception:
            pass

    return sorted(programs, key=lambda p: p["name"])
