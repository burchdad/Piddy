# 🔨 Building Piddy Desktop App from Source

This guide explains how to build Piddy into a standalone desktop application for Windows, macOS, and Linux.

## 📋 Prerequisites

### System Requirements
- **Node.js 16+** - Download from https://nodejs.org/
- **Python 3.9+** - Download from https://python.org/
- **npm** - Comes with Node.js
- **Git** - For version control

### Platform-Specific Requirements

**Windows:**
- Visual Studio Build Tools or Visual C++ redistributable
- NSIS (for installer) - Use: `choco install nsis` or download from https://nsis.sourceforge.io/

**macOS:**
- Xcode Command Line Tools: `xcode-select --install`
- For DMG: Built into the Electron Builder

**Linux:**
- Build essentials: `sudo apt-get install build-essential`
- For AppImage: `sudo apt-get install appimage-builder` (optional)

## 🚀 Quick Start Build

```bash
# 1. Clone repository
git clone https://github.com/burchdad/Piddy.git
cd Piddy

# 2. Install dependencies
npm install --prefix desktop

# 3. Build React frontend
npm install --prefix frontend
npm run build --prefix frontend

# 4. Build for all platforms
cd desktop
npm run build
# or specific platform:
npm run dist:win    # Windows
npm run dist:mac    # macOS
npm run dist:linux  # Linux
```

Built applications will be in `desktop/dist/`

## 📦 Build Details

### Using Build Scripts

We provide automated build scripts for convenience:

```bash
# Build for all platforms
bash build_scripts/build_desktop.sh all

# Build for specific platform
bash build_scripts/build_desktop.sh windows
bash build_scripts/build_desktop.sh macos
bash build_scripts/build_desktop.sh linux
```

### Manual Build Process

#### 1. Setup

```bash
cd /path/to/Piddy
npm install --prefix desktop
npm install --prefix frontend
```

#### 2. Build Frontend

```bash
npm run build --prefix frontend
```

This creates optimized production build in `frontend/dist/`

#### 3. Build Desktop App

```bash
cd desktop
npm run dist:win     # Windows
npm run dist:mac     # macOS
npm run dist:linux   # Linux
npm run dist         # All platforms (slower)
```

#### 4. Find Artifacts

```bash
ls -lh desktop/dist/
```

Output will contain:
- Windows: `.exe` installer and portable executable
- macOS: `.dmg` installer and `.zip` archive
- Linux: `.AppImage` bundle and `.deb` package

## 🎨 Creating App Icon

```bash
# Generate icons from SVG template
python generate_desktop_icon.py
```

This creates icons in `desktop/assets/` for Windows, macOS, and Linux.

## 🧪 Development & Testing

### Run in Development Mode

```bash
# Terminal 1: Backend server
python start_piddy.py

# Terminal 2: Electron dev app
npm run dev --prefix desktop
```

This enables hot-reload for both React and Electron.

### Test Before Build

```bash
# Pack without full build (faster)
cd desktop
npm run pack
```

This creates unpacked app in `dist/` directory without installer.

## 🔐 Code Signing (Optional but Recommended)

### Windows Signing

```bash
# Set environment variable with signing cert
$env:ELECTRON_BUILDER_SIGN_URL = "path/to/cert.pfx"
$env:ELECTRON_BUILDER_SIGN_PASSWORD = "cert-password"

npm run dist:win
```

### macOS Signing

```bash
# Set Apple Developer ID
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="app-password"
export APPLE_TEAM_ID="XXXXXXXXXX"

npm run dist:mac
```

### Linux Signing

```bash
# For deb packages
export GPG_KEY_ID="your-key-id"
npm run dist:linux
```

## 📤 Distributing Builds

### GitHub Releases

```bash
# Tag a release
git tag v1.0.0
git push origin v1.0.0

# Create GitHub Release and upload artifacts:
# 1. Go to https://github.com/burchdad/Piddy/releases
# 2. Create new release
# 3. Upload files from desktop/dist/
```

### Auto-Update Setup

Piddy supports auto-updates via GitHub releases:

1. **First Release:** Build and upload to GitHub
2. **Subsequent Updates:** Build new version and upload
3. **Users:** Will see "Update Available" and can auto-update

## 🐛 Troubleshooting

### Build Fails: "Python not found"
```bash
# Make sure Python 3.9+ is in PATH
python --version

# Or specify explicitly
NPM_PYTHON_PATH=/usr/bin/python3 npm run build --prefix desktop
```

### Build Fails: "node-gyp build"
```bash
# Rebuild native modules
npm rebuild --prefix desktop

# Or use pre-built binaries
npm install --prefix desktop --build-from-source=false
```

### Windows Build Hangs
```bash
# Clear npm cache
npm cache clean --force

# Clear Electron cache
rm -r ~/.cache/electron

# Try again
npm run dist:win
```

### macOS Build on Linux/Windows
Only native builds work. To build for macOS, you need a macOS machine.

### Icon Issues
If icons don't appear:
1. Check `desktop/assets/icon.png` exists (256x256)
2. Run `python generate_desktop_icon.py`
3. Try with different icon format or size

## 📊 Build Artifacts Explained

### Windows
- **Piddy-1.0.0.exe** - Full installer (recommended for users)
- **Piddy 1.0.0.exe** - Portable executable (no installation)

### macOS
- **Piddy-1.0.0.dmg** - Disk image (recommended for users)
- **Piddy-1.0.0-mac.zip** - Direct app archive

### Linux
- **Piddy-1.0.0.AppImage** - Self-contained executable (recommended)
- **piddy_1.0.0_amd64.deb** - Debian package (for apt)

## 🔄 Continuous Integration

GitHub Actions workflow for auto-building:

Create `.github/workflows/build-desktop.yml`:

```yaml
name: Build Desktop App

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: npm install --prefix desktop
      - run: npm run build --prefix frontend
      - run: npm run dist --prefix desktop
      - uses: softprops/action-gh-release@v1
        with:
          files: desktop/dist/**/*
```

## 📚 Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [Node-gyp Troubleshooting](https://github.com/nodejs/node-gyp/wiki)

## 🤝 Contributing to Desktop App

When modifying the desktop app:

1. Test thoroughly in dev mode
2. Build for all platforms before releasing
3. Test installers on each platform
4. Document any new dependencies
5. Update version in `desktop/package.json`

---

**Questions?** Open an issue on [GitHub](https://github.com/burchdad/Piddy/issues)
