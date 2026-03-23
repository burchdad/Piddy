#!/usr/bin/env bash
# ============================================
#   Piddy Runtime Bootstrapper
#   Downloads embedded Python + Node.js
#   for the current OS/architecture
# ============================================
set -e

PYTHON_VERSION="3.11.9"
NODE_VERSION="20.19.0"

# Resolve Piddy root (two levels up from scripts/tools/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDDY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "============================================"
echo "  Piddy Runtime Bootstrapper"
echo "  Python $PYTHON_VERSION + Node.js $NODE_VERSION"
echo "============================================"
echo ""

# --- Detect platform ---
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin)  PLATFORM="darwin" ;;
  Linux)   PLATFORM="linux" ;;
  *)       echo "[ERROR] Unsupported OS: $OS"; exit 1 ;;
esac

case "$ARCH" in
  x86_64|amd64)   ARCH_TAG="x64" ;;
  aarch64|arm64)   ARCH_TAG="arm64" ;;
  *)               echo "[ERROR] Unsupported arch: $ARCH"; exit 1 ;;
esac

RUNTIME_DIR="$PIDDY_ROOT/runtime/$PLATFORM-$ARCH_TAG"
echo "[INFO] Target: $RUNTIME_DIR"
echo "[INFO] Platform: $PLATFORM/$ARCH_TAG"
echo ""

mkdir -p "$RUNTIME_DIR"

# --- Helper: download with curl or wget ---
download() {
  local url="$1" dest="$2"
  echo "[DOWNLOAD] $url"
  if command -v curl &>/dev/null; then
    curl -fSL --progress-bar -o "$dest" "$url"
  elif command -v wget &>/dev/null; then
    wget -q --show-progress -O "$dest" "$url"
  else
    echo "[ERROR] Neither curl nor wget found. Install one and retry."
    exit 1
  fi
}

# ============================================
#   PYTHON
# ============================================
install_python() {
  local py_dir="$RUNTIME_DIR/python"
  if [ -x "$py_dir/bin/python3" ]; then
    echo "[OK] Python already installed at $py_dir"
    return 0
  fi

  echo ""
  echo "--- Installing Python $PYTHON_VERSION ---"
  local tmp_dir="$(mktemp -d)"

  if [ "$PLATFORM" = "darwin" ]; then
    # Use python.org standalone builds (framework build)
    # For macOS, use the standalone Python builds from Gregory Szorc
    local py_tag="${PYTHON_VERSION}"
    local build_tag="20240814"
    local cpu_arch
    if [ "$ARCH_TAG" = "arm64" ]; then
      cpu_arch="aarch64"
    else
      cpu_arch="x86_64"
    fi
    local url="https://github.com/indygreg/python-build-standalone/releases/download/${build_tag}/cpython-${py_tag}+${build_tag}-${cpu_arch}-apple-darwin-install_only_stripped.tar.gz"
    download "$url" "$tmp_dir/python.tar.gz"
    mkdir -p "$py_dir"
    tar -xzf "$tmp_dir/python.tar.gz" -C "$py_dir" --strip-components=1
  elif [ "$PLATFORM" = "linux" ]; then
    local py_tag="${PYTHON_VERSION}"
    local build_tag="20240814"
    local cpu_arch
    if [ "$ARCH_TAG" = "arm64" ]; then
      cpu_arch="aarch64"
    else
      cpu_arch="x86_64_v3"
    fi
    local url="https://github.com/indygreg/python-build-standalone/releases/download/${build_tag}/cpython-${py_tag}+${build_tag}-${cpu_arch}-unknown-linux-gnu-install_only_stripped.tar.gz"
    download "$url" "$tmp_dir/python.tar.gz"
    mkdir -p "$py_dir"
    tar -xzf "$tmp_dir/python.tar.gz" -C "$py_dir" --strip-components=1
  fi

  rm -rf "$tmp_dir"

  if [ -x "$py_dir/bin/python3" ]; then
    echo "[OK] Python $PYTHON_VERSION installed"
    "$py_dir/bin/python3" --version
  else
    echo "[ERROR] Python installation failed"
    exit 1
  fi
}

# ============================================
#   PIP + DEPENDENCIES
# ============================================
install_pip_deps() {
  local py="$RUNTIME_DIR/python/bin/python3"
  local pip="$RUNTIME_DIR/python/bin/pip3"

  # Ensure pip exists
  if [ ! -x "$pip" ]; then
    echo "[INFO] Installing pip..."
    "$py" -m ensurepip --upgrade 2>/dev/null || "$py" -m ensurepip 2>/dev/null || true
  fi

  # Install requirements
  local req="$PIDDY_ROOT/requirements.txt"
  if [ -f "$req" ]; then
    echo ""
    echo "--- Installing Python dependencies ---"
    "$py" -m pip install --upgrade pip 2>/dev/null || true
    "$py" -m pip install -r "$req" --quiet
    echo "[OK] Python dependencies installed"
  else
    echo "[WARN] No requirements.txt found — skipping pip install"
  fi
}

# ============================================
#   NODE.JS
# ============================================
install_node() {
  local node_dir="$RUNTIME_DIR/node"
  if [ -x "$node_dir/bin/node" ]; then
    echo "[OK] Node.js already installed at $node_dir"
    return 0
  fi

  echo ""
  echo "--- Installing Node.js $NODE_VERSION ---"
  local tmp_dir="$(mktemp -d)"

  local node_platform="$PLATFORM"
  local node_arch="$ARCH_TAG"
  # Node uses "x64" for x86_64, "arm64" for aarch64
  local url="https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-${node_platform}-${node_arch}.tar.xz"

  download "$url" "$tmp_dir/node.tar.xz"
  mkdir -p "$node_dir"
  tar -xJf "$tmp_dir/node.tar.xz" -C "$node_dir" --strip-components=1
  rm -rf "$tmp_dir"

  if [ -x "$node_dir/bin/node" ]; then
    echo "[OK] Node.js $NODE_VERSION installed"
    "$node_dir/bin/node" --version
  else
    echo "[ERROR] Node.js installation failed"
    exit 1
  fi
}

# ============================================
#   NPM DEPENDENCIES
# ============================================
install_npm_deps() {
  local npm="$RUNTIME_DIR/node/bin/npm"
  local node="$RUNTIME_DIR/node/bin/node"

  # Frontend
  if [ -d "$PIDDY_ROOT/frontend" ] && [ -f "$PIDDY_ROOT/frontend/package.json" ]; then
    echo ""
    echo "--- Installing frontend dependencies ---"
    export PATH="$(dirname "$node"):$PATH"
    cd "$PIDDY_ROOT/frontend"
    "$npm" install --quiet 2>/dev/null || "$npm" install
    echo "[OK] Frontend dependencies installed"
    cd "$PIDDY_ROOT"
  fi

  # Desktop
  if [ -d "$PIDDY_ROOT/desktop" ] && [ -f "$PIDDY_ROOT/desktop/package.json" ]; then
    echo ""
    echo "--- Installing desktop dependencies ---"
    cd "$PIDDY_ROOT/desktop"
    "$npm" install --quiet 2>/dev/null || "$npm" install
    echo "[OK] Desktop dependencies installed"
    cd "$PIDDY_ROOT"
  fi
}

# ============================================
#   RUN
# ============================================
install_python
install_pip_deps
install_node
install_npm_deps

echo ""
echo "============================================"
echo "  Runtime bootstrap complete!"
echo "  Python: $RUNTIME_DIR/python/bin/python3"
echo "  Node:   $RUNTIME_DIR/node/bin/node"
echo ""
echo "  To start Piddy:  ./start.sh"
echo "============================================"
