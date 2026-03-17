# Piddy Self-Contained Runtime Build Guide

This guide explains how to build Piddy as a completely self-contained executable with no external dependencies.

## Overview

**Goal**: Create a single `Piddy.exe` that:
- ✅ Contains frontend + backend + all dependencies
- ✅ Auto-starts backend on launch (no external ports)
- ✅ Works completely offline
- ✅ No Python installation required
- ✅ No npm required after build

## Architecture

```
┌──────────────────────────────────────┐
│  Piddy.exe (Single executable)       │
├──────────────────────────────────────┤
│  Electron Main Process               │
│  ├─ Spawns bundled backend binary    │
│  ├─ Serves React frontend            │
│  └─ Mana... internal communication   │
├──────────────────────────────────────┤
│  Frontend (React)                    │
│  └─ Communicates via localhost:8000  │
├──────────────────────────────────────┤
│  Backend (PyInstaller binary)        │
│  └─ No external Python dependency    │
└──────────────────────────────────────┘
```

## Prerequisites

- Python 3.9+
- Node.js 16+ with npm
- PyInstaller: `pip install pyinstaller`
- Required packages: `pip install -r requirements.txt`

## Build Process

### Step 1: Build Backend Binary

This creates a standalone Python executable using PyInstaller.

```bash
# From project root
python build_backend.py

# Output: dist/piddy-backend.exe (Windows) or dist/piddy-backend (Linux/Mac)
```

**What it does:**
- ✅ Validates environment
- ✅ Runs PyInstaller with proper configuration
- ✅ Bundles all Python dependencies
- ✅ Creates standalone binary (~100-150 MB)
- ✅ Copies binary to `desktop/resources/` for Electron packaging

**Options:**
```bash
python build_backend.py --clean      # Clean previous builds
python build_backend.py --skip-copy  # Skip copying to Electron
```

### Step 2: Build Electron App

This bundles the frontend and backend binary into a Windows installer/portable exe.

```bash
# From desktop directory
cd desktop

# Install dependencies (first time only)
npm install

# Build frontend
npm run build-react

# Build complete package with backend binary
npm run build
```

**What it creates:**
- `desktop/dist/Piddy-Setup.exe` - Installer
- `desktop/dist/Piddy.exe` - Portable executable

### Step 3: Optional - Build Custom Installers

```bash
# Windows installer + portable
npm run dist:win

# macOS
npm run dist:mac

# Linux
npm run dist:linux

# All platforms
npm run dist
```

## Configuration

### PyInstaller Configuration (`build_backend.spec`)

Located in project root. Configures:
- Entry point: `src/main.py`
- Hidden imports for FastAPI, Uvicorn, Pydantic, SQLAlchemy
- Data files bundling
- Output: `dist/piddy-backend`

Key settings:
```spec
console=True          # Show console window (for debugging)
onefile=True          # Single executable file
windowed=False        # Console app (better for subprocess)
```

### Electron Configuration (`desktop/package.json`)

Build configuration includes:
```json
"files": [
  "main.js",
  "preload.js",
  "piddy-backend.exe",    // Include bundled backend
  "node_modules/**/*"
],
"extraResources": [
  "../resources/piddy-backend*"  // Copy backend to app resources
]
```

### Backend Startup Logic (`desktop/main.js`)

The `findPython()` function now:
1. **First**: Checks for bundled `piddy-backend.exe/piddy-backend`
2. **Second**: Searches for system Python (fallback)

```javascript
function findPython() {
  // Check for bundled binary first
  const bundledPath = getResourcePath('piddy-backend.exe');
  if (fs.existsSync(bundledPath)) {
    return bundledPath;
  }
  
  // Fall back to system Python
  return findSystemPython();
}
```

The `startPythonBackend()` function:
- Detects if executable is binary or Python
- Spawns accordingly (no args for binary, args for Python)

```javascript
const isBundledBinary = pythonExe.includes('piddy-backend');
const args = isBundledBinary ? [] : [scriptPath, '--desktop'];
spawn(pythonExe, args, {/* ... */});
```

## Troubleshooting

### Build Fails: "PyInstaller not found"

```bash
pip install pyinstaller
python build_backend.py
```

### Build Fails: "start_piddy.py not found"

Ensure you're in the project root directory:
```bash
cd /path/to/Piddy
python build_backend.py
```

### Binary too large (>200 MB)

Normal for bundled Python + dependencies. Can optimize:
```bash
# Use upx compression (optional)
pip install upx
python build_backend.py
```

### Electron build missing backend binary

Ensure binary was copied:
```bash
ls desktop/resources/piddy-backend*
npm run build
```

### App starts but can't connect to backend

Backend binary might have crashed. Check logs:
```bash
# Windows
%APPDATA%\.piddy_logs\piddy_main.log

# Linux/Mac
~/.piddy_logs/piddy_main.log
```

### Backend times out to start

Increase timeout in `desktop/main.js`:
```javascript
const MAX_RETRIES = 10;  // Increase from 6
const TIMEOUT_BASE = 2000;  // Longer between retries
```

## Distribution

### Windows

**Installer** - Users can install or extract anywhere:
```bash
npm run dist:win
# Output: Piddy-Setup.exe
```

**Portable** - Single executable, no installation:
```bash
# Already created in npm run build
desktop/dist/Piddy.exe
```

### macOS

```bash
npm run dist:mac
# Output: Piddy-*.dmg
```

### Linux

```bash
npm run dist:linux
# Output: Piddy-*.AppImage
```

## Size Expectations

| Component | Size |
|---|---|
| Frontend bundle | ~3 MB |
| Python runtime | ~40 MB |
| Dependencies | ~60-100 MB |
| Piddy-backend.exe | ~100-150 MB |
| **Total Piddy.exe** | **~150-200 MB** |

### Optimization Tips

1. **Exclude unused packages** in `build_backend.spec`
2. **Use UPX compression** - reduces by 30-40%
3. **MinifyCSS/JS** - frontend optimization
4. **Remove dev dependencies** - npm prune --production

## Development Workflow

### During Development

**Option 1: Run separately** (faster iteration)
```bash
# Terminal 1: Backend
python -m src.main

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Electron (connect to external ports)
cd desktop && npm start
```

**Option 2: Build and run bundled**
```bash
# Full build cycle (slower but tests final product)
npm run build
desktop/dist/Piddy.exe
```

### Before Release

1. **Clean build**
```bash
python build_backend.py --clean
cd desktop
npm run build
```

2. **Test the executable**
```bash
desktop/dist/Piddy.exe
```

3. **Verify functionality**
   - ✅ App launches
   - ✅ Backend starts (check logs)
   - ✅ Frontend loads
   - ✅ API calls work
   - ✅ No console errors

4. **Create release**
```bash
npm run dist:win
# Upload: desktop/dist/Piddy-Setup.exe
```

## Advanced: Custom Backend

To integrate a different backend:

1. **Update entry point** in `build_backend.spec`:
```spec
a = Analysis(['path/to/your/main.py'], ...)
```

2. **Adjust hidden imports** based on your packages:
```spec
hidden_imports = [
  'your_package',
  'your_dependencies',
  ...
]
```

3. **Rebuild**:
```bash
python build_backend.py --clean
```

## Automation

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Build Piddy Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - run: pip install -r requirements.txt pyinstaller
      - run: python build_backend.py
      - run: cd desktop && npm ci && npm run build
      
      - uses: actions/upload-artifact@v3
        with:
          name: Piddy-Release
          path: desktop/dist/Piddy-*.exe
```

## Related Docs

- [DESKTOP_ARCHITECTURE.md](DESKTOP_ARCHITECTURE.md) - Architecture overview
- [DESKTOP_BUILD_GUIDE.md](DESKTOP_BUILD_GUIDE.md) - Original build guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT.md) - Deployment options

---

**Next Steps:**
1. ✅ Run `python build_backend.py`
2. ✅ Run `cd desktop && npm run build`
3. ✅ Test `desktop/dist/Piddy.exe`
4. ✅ Distribute or create installer
