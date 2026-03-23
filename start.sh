#!/usr/bin/env bash
# ============================================
#   PIDDY - AI Assistant
#   Cross-Platform Portable Launcher
#   Works on macOS, Linux, and WSL
# ============================================
set -e

# Resolve the actual directory this script lives in (follows symlinks)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
PIDDY_ROOT="$(cd -P "$(dirname "$SOURCE")" && pwd)"
export PIDDY_ROOT

echo "============================================"
echo "  PIDDY - AI Assistant"
echo "  Portable Runtime ($(uname -s)/$(uname -m))"
echo "============================================"
echo ""

# --- Detect OS and Architecture ---
detect_platform() {
  OS="$(uname -s)"
  ARCH="$(uname -m)"

  case "$OS" in
    Darwin)  PLATFORM="darwin" ;;
    Linux)   PLATFORM="linux" ;;
    MINGW*|MSYS*|CYGWIN*)
      echo "[INFO] Windows detected — use start.bat instead."
      exit 1
      ;;
    *)
      echo "[ERROR] Unsupported OS: $OS"
      exit 1
      ;;
  esac

  case "$ARCH" in
    x86_64|amd64)   ARCH_TAG="x64" ;;
    aarch64|arm64)   ARCH_TAG="arm64" ;;
    *)
      echo "[ERROR] Unsupported architecture: $ARCH"
      exit 1
      ;;
  esac

  export PLATFORM ARCH_TAG
  echo "[OK] Platform: $PLATFORM/$ARCH_TAG"
}

# --- Locate or download embedded Python ---
find_python() {
  # 1. Check platform-specific embedded runtime
  local embedded="$PIDDY_ROOT/runtime/$PLATFORM-$ARCH_TAG/python/bin/python3"
  if [ -x "$embedded" ]; then
    PYTHON="$embedded"
    echo "[OK] Embedded Python: $PYTHON"
    return 0
  fi

  # 2. Check generic runtime path (legacy / single-platform)
  local generic="$PIDDY_ROOT/runtime/python/bin/python3"
  if [ -x "$generic" ]; then
    PYTHON="$generic"
    echo "[OK] Embedded Python (generic): $PYTHON"
    return 0
  fi

  # 3. Fall back to system Python
  if command -v python3 &>/dev/null; then
    PYTHON="$(command -v python3)"
    echo "[WARN] Using system Python: $PYTHON"
    echo "       For full portability, run: ./scripts/tools/bootstrap_runtime.sh"
    return 0
  fi

  echo "[ERROR] Python 3 not found."
  echo "        Install Python 3.11+ or run: ./scripts/tools/bootstrap_runtime.sh"
  exit 1
}

# --- Locate or download embedded Node.js ---
find_node() {
  # 1. Platform-specific embedded runtime
  local embedded="$PIDDY_ROOT/runtime/$PLATFORM-$ARCH_TAG/node/bin/node"
  if [ -x "$embedded" ]; then
    NODE="$embedded"
    NPM="$PIDDY_ROOT/runtime/$PLATFORM-$ARCH_TAG/node/bin/npm"
    echo "[OK] Embedded Node.js: $NODE"
    return 0
  fi

  # 2. Generic runtime path
  local generic="$PIDDY_ROOT/runtime/node/bin/node"
  if [ -x "$generic" ]; then
    NODE="$generic"
    NPM="$PIDDY_ROOT/runtime/node/bin/npm"
    echo "[OK] Embedded Node.js (generic): $NODE"
    return 0
  fi

  # 3. System Node.js
  if command -v node &>/dev/null; then
    NODE="$(command -v node)"
    NPM="$(command -v npm)"
    echo "[WARN] Using system Node.js: $NODE"
    return 0
  fi

  echo "[WARN] Node.js not found — frontend may not work."
  echo "       Run: ./scripts/tools/bootstrap_runtime.sh"
  NODE=""
  NPM=""
}

# --- Ensure PYTHONPATH includes project root ---
setup_env() {
  export PYTHONPATH="$PIDDY_ROOT:${PYTHONPATH:-}"
  export PATH="$(dirname "$PYTHON"):$(dirname "${NODE:-/usr/bin/node}"):$PATH"
}

# --- Check .env ---
check_env() {
  if [ ! -f "$PIDDY_ROOT/.env" ]; then
    echo "[WARN] No .env file found."
    if [ -f "$PIDDY_ROOT/.env.example" ]; then
      echo "       Copying .env.example → .env (edit with your API keys)"
      cp "$PIDDY_ROOT/.env.example" "$PIDDY_ROOT/.env"
    else
      echo "       Create a .env file with your API keys."
    fi
  fi
}

# --- Fix permissions (needed when copied from Windows/FAT32 to Unix) ---
fix_permissions() {
  # Make sure Python and Node binaries are executable
  if [ -n "$PYTHON" ] && [ -f "$PYTHON" ]; then
    chmod +x "$PYTHON" 2>/dev/null || true
  fi
  if [ -n "$NODE" ] && [ -f "$NODE" ]; then
    chmod +x "$NODE" 2>/dev/null || true
  fi
  # Fix all shell scripts
  find "$PIDDY_ROOT" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
}

# --- Main ---
detect_platform
find_python
find_node
setup_env
fix_permissions
check_env

"$PYTHON" --version 2>/dev/null && echo "" || true

# Pass all arguments through to start_piddy.py
echo "Starting Piddy..."
cd "$PIDDY_ROOT"
exec "$PYTHON" "$PIDDY_ROOT/start_piddy.py" "$@"
