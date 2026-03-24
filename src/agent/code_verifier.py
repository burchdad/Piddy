"""
Code Verifier — Phase 53: Post-generation validation and auto-fix.

After Piddy generates files, this module:
  1. Runs language-specific syntax checks (Python AST, Node --check, etc.)
  2. Detects missing imports
  3. Checks for common async bugs
  4. Validates Docker/config files
  5. Returns structured diagnostics for the UI and auto-fix loop

Each checker returns a list of Issue dicts:
  {"file": str, "line": int|None, "severity": "error"|"warning", "code": str, "message": str}
"""

import ast
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Issue severity levels ────────────────────────────────────────────
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


def verify_files(file_actions: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Run all applicable verifiers on a list of generated file actions.

    Parameters
    ----------
    file_actions : list of {"path": str, "content": str}

    Returns
    -------
    {
        "passed": bool,           # True if zero errors (warnings OK)
        "issues": [...],          # All issues found
        "summary": str,           # Human-readable summary
        "files_checked": int,
        "error_count": int,
        "warning_count": int,
    }
    """
    all_issues: List[Dict[str, Any]] = []

    for fa in file_actions:
        path = fa["path"]
        content = fa["content"]
        ext = _ext(path)

        if ext in (".py",):
            all_issues.extend(_check_python(path, content))
        elif ext in (".js", ".jsx", ".ts", ".tsx"):
            all_issues.extend(_check_javascript(path, content))
        elif ext in (".html", ".htm"):
            all_issues.extend(_check_html(path, content))
        elif ext in (".json",):
            all_issues.extend(_check_json(path, content))
        elif ext in (".yml", ".yaml"):
            all_issues.extend(_check_yaml(path, content))
        elif ext in (".dockerfile",) or Path(path).name.lower() in ("dockerfile",):
            all_issues.extend(_check_dockerfile(path, content))
        # Docker-compose detection
        if "docker-compose" in Path(path).name.lower() and ext in (".yml", ".yaml"):
            all_issues.extend(_check_docker_compose(path, content))

    error_count = sum(1 for i in all_issues if i["severity"] == SEVERITY_ERROR)
    warning_count = sum(1 for i in all_issues if i["severity"] == SEVERITY_WARNING)
    passed = error_count == 0

    if passed and warning_count == 0:
        summary = f"✅ All {len(file_actions)} file(s) passed verification"
    elif passed:
        summary = f"✅ Passed with {warning_count} warning(s) across {len(file_actions)} file(s)"
    else:
        summary = f"❌ {error_count} error(s) and {warning_count} warning(s) across {len(file_actions)} file(s)"

    return {
        "passed": passed,
        "issues": all_issues,
        "summary": summary,
        "files_checked": len(file_actions),
        "error_count": error_count,
        "warning_count": warning_count,
    }


def format_issues_for_llm(verification: Dict[str, Any]) -> str:
    """
    Format verification issues into a prompt snippet for the LLM auto-fix loop.
    """
    if verification["passed"] and verification["warning_count"] == 0:
        return ""

    lines = ["The following issues were found in the generated code:\n"]
    for issue in verification["issues"]:
        loc = f" (line {issue['line']})" if issue.get("line") else ""
        lines.append(f"- [{issue['severity'].upper()}] {issue['file']}{loc}: [{issue['code']}] {issue['message']}")

    lines.append(
        "\nPlease fix ALL of the above issues and regenerate the affected files. "
        "Use the same ===FILE: path=== ... ===END_FILE=== format. "
        "Only output the files that need changes."
    )
    return "\n".join(lines)


# ── Helpers ──────────────────────────────────────────────────────────

def _ext(path: str) -> str:
    return Path(path).suffix.lower()


def _issue(file: str, severity: str, code: str, message: str, line: Optional[int] = None) -> Dict:
    return {"file": file, "line": line, "severity": severity, "code": code, "message": message}


# ── Python Checks ────────────────────────────────────────────────────

# Known standard-library modules (subset covering common ones)
_STDLIB_MODULES = {
    "abc", "argparse", "ast", "asyncio", "base64", "bisect", "builtins",
    "calendar", "cgi", "cmath", "codecs", "collections", "configparser",
    "contextlib", "copy", "csv", "ctypes", "dataclasses", "datetime",
    "decimal", "difflib", "dis", "email", "enum", "errno", "fnmatch",
    "fractions", "ftplib", "functools", "getpass", "glob", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "importlib", "inspect",
    "io", "itertools", "json", "keyword", "linecache", "locale",
    "logging", "lzma", "math", "mimetypes", "multiprocessing", "numbers",
    "operator", "os", "pathlib", "pickle", "platform", "pprint",
    "profile", "pstats", "queue", "random", "re", "readline", "secrets",
    "select", "shelve", "shlex", "shutil", "signal", "site", "smtplib",
    "socket", "sqlite3", "ssl", "stat", "statistics", "string",
    "struct", "subprocess", "sys", "sysconfig", "tempfile", "textwrap",
    "threading", "time", "timeit", "token", "tokenize", "tomllib",
    "traceback", "tracemalloc", "turtle", "types", "typing", "unittest",
    "urllib", "uuid", "venv", "warnings", "weakref", "webbrowser",
    "xml", "xmlrpc", "zipfile", "zipimport", "zlib",
}

# Common third-party modules and what they provide
_KNOWN_THIRD_PARTY = {
    "fastapi": {"FastAPI", "Depends", "HTTPException", "Header", "Request",
                "Response", "APIRouter", "Query", "Path", "Body", "Form",
                "File", "UploadFile", "BackgroundTasks", "status"},
    "fastapi.responses": {"JSONResponse", "HTMLResponse", "RedirectResponse",
                          "StreamingResponse", "FileResponse"},
    "fastapi.middleware.cors": {"CORSMiddleware"},
    "fastapi.security": {"OAuth2PasswordBearer", "OAuth2PasswordRequestForm",
                         "HTTPBearer", "HTTPBasic"},
    "pydantic": {"BaseModel", "Field", "validator", "root_validator"},
    "sqlalchemy": {"create_engine", "Column", "Integer", "String", "Float",
                   "Boolean", "DateTime", "ForeignKey", "Text"},
    "sqlalchemy.ext.asyncio": {"AsyncSession", "create_async_engine"},
    "sqlalchemy.orm": {"sessionmaker", "Session", "relationship",
                       "declarative_base"},
    "flask": {"Flask", "request", "jsonify", "render_template", "redirect",
              "url_for", "abort", "Blueprint", "g", "session"},
    "django": set(),
    "requests": {"get", "post", "put", "delete", "patch", "Session"},
    "httpx": set(),
    "uvicorn": set(),
    "gunicorn": set(),
    "celery": set(),
    "redis": set(),
    "pymongo": set(),
    "pytest": set(),
    "numpy": set(),
    "pandas": set(),
}

# Map names to their typical import source (for missing-import detection)
_NAME_SOURCES: Dict[str, str] = {}
for _mod, _names in _KNOWN_THIRD_PARTY.items():
    for _name in _names:
        _NAME_SOURCES[_name] = _mod


def _check_python(path: str, content: str) -> List[Dict]:
    """Validate Python file: syntax, imports, async correctness."""
    issues: List[Dict] = []

    # ── 1. Syntax check via AST ──
    try:
        tree = ast.parse(content, filename=path)
    except SyntaxError as e:
        issues.append(_issue(path, SEVERITY_ERROR, "E001", f"Syntax error: {e.msg}", e.lineno))
        return issues  # Can't do further analysis if it doesn't parse

    # ── 2. Collect all imports ──
    imported_names: set = set()
    imported_modules: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name)
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imported_modules.add(mod.split(".")[0])
            for alias in (node.names or []):
                imported_names.add(alias.asname or alias.name)

    # ── 3. Check for names used but not imported / not defined ──
    defined_names = _collect_defined_names(tree)
    all_available = imported_names | defined_names | set(dir(__builtins__)) if isinstance(__builtins__, dict) else imported_names | defined_names | set(dir(__builtins__))

    # Add Python builtins explicitly
    all_available |= {
        "print", "len", "range", "int", "str", "float", "list", "dict",
        "set", "tuple", "bool", "type", "isinstance", "issubclass",
        "hasattr", "getattr", "setattr", "delattr", "callable", "super",
        "property", "staticmethod", "classmethod", "enumerate", "zip",
        "map", "filter", "sorted", "reversed", "min", "max", "abs",
        "sum", "any", "all", "round", "open", "input", "id", "hash",
        "repr", "format", "chr", "ord", "hex", "oct", "bin",
        "iter", "next", "slice", "object", "Exception", "ValueError",
        "TypeError", "KeyError", "IndexError", "AttributeError",
        "RuntimeError", "StopIteration", "NotImplementedError",
        "FileNotFoundError", "IOError", "OSError", "ImportError",
        "NameError", "ZeroDivisionError", "OverflowError",
        "True", "False", "None", "__name__", "__file__", "__doc__",
        "breakpoint", "exit", "quit",
    }

    # Scan for top-level name references that look unresolved
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            name = node.id
            if name not in all_available and name in _NAME_SOURCES:
                src = _NAME_SOURCES[name]
                issues.append(_issue(
                    path, SEVERITY_ERROR, "E002",
                    f"'{name}' is used but not imported (typically from '{src}')",
                    node.lineno,
                ))

    # ── 4. Async correctness ──
    issues.extend(_check_async_correctness(path, tree, content))

    # ── 5. Security quick-checks ──
    issues.extend(_check_python_security(path, content))

    return issues


def _collect_defined_names(tree: ast.AST) -> set:
    """Collect all names defined in the module (functions, classes, assigns, etc.)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            # Add parameter names
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                names.add(arg.arg)
            if node.args.vararg:
                names.add(node.args.vararg.arg)
            if node.args.kwarg:
                names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, ast.Global):
            names.update(node.names)
        elif isinstance(node, ast.Nonlocal):
            names.update(node.names)
        elif isinstance(node, ast.For):
            names |= _extract_target_names(node.target)
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars:
                    names |= _extract_target_names(item.optional_vars)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            for gen in node.generators:
                names |= _extract_target_names(gen.target)
    return names


def _extract_target_names(node: ast.AST) -> set:
    """Extract variable names from assignment targets (handles tuple unpacking)."""
    names = set()
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            names |= _extract_target_names(elt)
    elif isinstance(node, ast.Starred):
        names |= _extract_target_names(node.value)
    return names


def _check_async_correctness(path: str, tree: ast.AST, content: str) -> List[Dict]:
    """Detect common async/await bugs."""
    issues: List[Dict] = []

    for node in ast.walk(tree):
        # Check for 'await' inside non-async functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_async = isinstance(node, ast.AsyncFunctionDef)
            for child in ast.walk(node):
                if isinstance(child, ast.Await) and not is_async:
                    issues.append(_issue(
                        path, SEVERITY_ERROR, "E010",
                        f"'await' used inside non-async function '{node.name}()' — "
                        f"change to 'async def {node.name}()'",
                        child.lineno,
                    ))
                    break  # One report per function is enough

    # Check for yield in async generators used as regular generators
    # (common FastAPI Depends pattern)
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Detect: def func(...):  ...yield...  ...await...
        # This is the pattern from the user's bug report
        if stripped.startswith("def ") and "yield" in stripped:
            # Look ahead for await in the function body
            indent = len(line) - len(line.lstrip())
            for j in range(i, min(i + 30, len(lines))):
                body_line = lines[j - 1] if j <= len(lines) else ""
                if body_line.strip() and not body_line.strip().startswith("#"):
                    body_indent = len(body_line) - len(body_line.lstrip())
                    if body_indent <= indent and j > i:
                        break
                    if "await " in body_line and "async def" not in line:
                        func_name = re.search(r"def\s+(\w+)", stripped)
                        name = func_name.group(1) if func_name else "?"
                        issues.append(_issue(
                            path, SEVERITY_ERROR, "E011",
                            f"Function '{name}()' uses 'await' but is not async — "
                            f"add 'async' keyword",
                            i,
                        ))
                        break

    return issues


def _check_python_security(path: str, content: str) -> List[Dict]:
    """Quick security lint for Python files."""
    issues: List[Dict] = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Hardcoded passwords/secrets (common in generated code)
        if re.search(r'(?:password|secret|api_key|token)\s*=\s*["\'][^"\']{4,}["\']', stripped, re.IGNORECASE):
            # Ignore if it looks like an env var read or placeholder
            if "os.getenv" not in stripped and "os.environ" not in stripped and "your-" not in stripped.lower():
                issues.append(_issue(
                    path, SEVERITY_WARNING, "W001",
                    "Possible hardcoded secret — consider using environment variables",
                    i,
                ))

        # eval() usage
        if re.search(r'\beval\s*\(', stripped):
            issues.append(_issue(
                path, SEVERITY_WARNING, "W002",
                "Use of eval() — potential code injection risk",
                i,
            ))

        # SQL string formatting (injection risk)
        if re.search(r'(?:execute|cursor\.execute)\s*\(\s*f["\']', stripped):
            issues.append(_issue(
                path, SEVERITY_WARNING, "W003",
                "SQL query uses f-string — potential SQL injection, use parameterized queries",
                i,
            ))

    return issues


# ── JavaScript/TypeScript Checks ─────────────────────────────────────

def _check_javascript(path: str, content: str) -> List[Dict]:
    """Basic JavaScript/TypeScript validation."""
    issues: List[Dict] = []
    lines = content.split("\n")

    # Check for balanced braces (rough syntax check)
    brace_count = content.count("{") - content.count("}")
    if abs(brace_count) > 0:
        issues.append(_issue(
            path, SEVERITY_ERROR, "E020",
            f"Unbalanced braces: {brace_count:+d} (missing {'}'.join([''] * abs(brace_count)) if brace_count > 0 else 'extra closing braces'})",
        ))

    paren_count = content.count("(") - content.count(")")
    if abs(paren_count) > 0:
        issues.append(_issue(
            path, SEVERITY_ERROR, "E021",
            f"Unbalanced parentheses: {paren_count:+d}",
        ))

    # Check for common issues
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # require() in ES module file
        if "require(" in stripped and any(
            re.search(r'\b(import|export)\b', l) for l in lines[:20]
        ):
            issues.append(_issue(
                path, SEVERITY_WARNING, "W020",
                "Mixing require() with ES module imports",
                i,
            ))
            break

    return issues


# ── HTML Checks ──────────────────────────────────────────────────────

def _check_html(path: str, content: str) -> List[Dict]:
    """Basic HTML validation."""
    issues: List[Dict] = []

    # Check for unclosed tags (very basic)
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}
    open_tags = re.findall(r"<(\w+)[\s>]", content)
    close_tags = re.findall(r"</(\w+)>", content)

    open_counts: Dict[str, int] = {}
    for tag in open_tags:
        tag_lower = tag.lower()
        if tag_lower not in void_tags:
            open_counts[tag_lower] = open_counts.get(tag_lower, 0) + 1
    for tag in close_tags:
        tag_lower = tag.lower()
        open_counts[tag_lower] = open_counts.get(tag_lower, 0) - 1

    for tag, count in open_counts.items():
        if count > 0:
            issues.append(_issue(
                path, SEVERITY_WARNING, "W030",
                f"Tag <{tag}> appears to have {count} unclosed instance(s)",
            ))

    return issues


# ── JSON Checks ──────────────────────────────────────────────────────

def _check_json(path: str, content: str) -> List[Dict]:
    """Validate JSON syntax."""
    import json as _json
    issues: List[Dict] = []
    try:
        _json.loads(content)
    except _json.JSONDecodeError as e:
        issues.append(_issue(
            path, SEVERITY_ERROR, "E040",
            f"Invalid JSON: {e.msg}",
            e.lineno,
        ))
    return issues


# ── YAML Checks ──────────────────────────────────────────────────────

def _check_yaml(path: str, content: str) -> List[Dict]:
    """Validate YAML syntax."""
    issues: List[Dict] = []
    try:
        import yaml
    except ImportError:
        return issues  # yaml not installed, skip
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        line: Optional[int] = None
        mark = getattr(e, "problem_mark", None)
        if mark is not None:
            line = mark.line + 1
        issues.append(_issue(
            path, SEVERITY_ERROR, "E050",
            f"Invalid YAML: {e}",
            line,
        ))
    return issues


# ── Dockerfile Checks ────────────────────────────────────────────────

def _check_dockerfile(path: str, content: str) -> List[Dict]:
    """Basic Dockerfile validation."""
    issues: List[Dict] = []
    lines = content.strip().split("\n")

    if not lines:
        issues.append(_issue(path, SEVERITY_ERROR, "E060", "Empty Dockerfile"))
        return issues

    # Must start with FROM (or ARG before FROM)
    first_instruction = None
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            first_instruction = stripped.split()[0].upper()
            break

    if first_instruction and first_instruction not in ("FROM", "ARG"):
        issues.append(_issue(
            path, SEVERITY_ERROR, "E061",
            f"Dockerfile must start with FROM (found {first_instruction})",
            1,
        ))

    # Check for CMD or ENTRYPOINT
    has_cmd = any(re.match(r"^\s*(CMD|ENTRYPOINT)\s", line, re.IGNORECASE) for line in lines)
    if not has_cmd:
        issues.append(_issue(
            path, SEVERITY_WARNING, "W060",
            "Dockerfile has no CMD or ENTRYPOINT — container won't know what to run",
        ))

    return issues


# ── Docker Compose Checks ────────────────────────────────────────────

def _check_docker_compose(path: str, content: str) -> List[Dict]:
    """Validate docker-compose structure."""
    issues: List[Dict] = []
    try:
        import yaml
        data = yaml.safe_load(content)
    except ImportError:
        return issues
    except Exception:
        return issues  # YAML error already caught by _check_yaml

    if not isinstance(data, dict):
        issues.append(_issue(path, SEVERITY_ERROR, "E070", "docker-compose must be a YAML mapping"))
        return issues

    services = data.get("services", {})
    if not services:
        issues.append(_issue(path, SEVERITY_WARNING, "W070", "No services defined in docker-compose"))

    for svc_name, svc in (services or {}).items():
        if not isinstance(svc, dict):
            continue
        # Service needs either 'image' or 'build'
        if "image" not in svc and "build" not in svc:
            issues.append(_issue(
                path, SEVERITY_ERROR, "E071",
                f"Service '{svc_name}' has neither 'image' nor 'build'",
            ))

        # Check healthcheck reference
        depends = svc.get("depends_on", {})
        if isinstance(depends, dict):
            for dep_name, dep_cfg in depends.items():
                if isinstance(dep_cfg, dict) and dep_cfg.get("condition") == "service_healthy":
                    dep_svc = services.get(dep_name, {})
                    if isinstance(dep_svc, dict) and "healthcheck" not in dep_svc:
                        issues.append(_issue(
                            path, SEVERITY_WARNING, "W071",
                            f"Service '{svc_name}' depends on '{dep_name}' being healthy, "
                            f"but '{dep_name}' has no healthcheck defined",
                        ))

    return issues
