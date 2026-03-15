# 🖥️ Piddy Desktop App - Quick Build Guide

## ✅ Now Fixed! Working Build Instructions

The Electron dependencies have been updated to working versions. Follow these steps to build.

## 🚀 Quick Start (30 seconds)

```bash
cd /workspaces/Piddy/desktop

# Step 1: Install dependencies (1 minute)
npm install --legacy-peer-deps

# Step 2: Test build (creates unpacked app)
npm run pack

# Step 3: Check output
ls -lh dist/

# Results:
# - Linux: dist/linux-unpacked/piddy (executable)
# - macOS would be: dist/*/Piddy.app
# - Windows would be: dist/Piddy 1.0.0.exe
```

## 📦 Building for Distribution

### For All Platforms (slow, ~5 minutes)
```bash
npm run dist
# Creates installers in dist/
```

### For Specific Platform (fast, ~2 minutes)
```bash
npm run dist:win     # Windows installer
npm run dist:mac     # macOS DMG
npm run dist:linux   # Linux AppImage
```

## 📂 Build Output Locations

After building, installers will be in: `desktop/dist/`

```
dist/
├── builder-debug.yml              # Build metadata
├── linux-unpacked/                # Unpacked Linux app
│   └── piddy                       # Executable
├── Piddy-Setup.exe               # Windows installer
├── Piddy 1.0.0.exe               # Windows portable
├── Piddy-1.0.0.dmg              # macOS installer
├── Piddy-1.0.0.AppImage         # Linux AppImage
└── piddy_1.0.0_amd64.deb        # Linux Debian package
```

## 🧪 Testing the Build

### Test Linux App (from workspace)
```bash
cd /workspaces/Piddy/desktop/dist/linux-unpacked
./piddy --help
./piddy &    # Run in background
# Opens Piddy with Electron window
```

### Test Windows Installer (on Windows)
```
- Download: Piddy-Setup.exe
- Double-click to install
- Launches from Start Menu
```

### Test macOS app (on macOS)
```bash
- Open: Piddy-1.0.0.dmg
- Drag Piddy to Applications folder
- Launch from Applications
```

## ❌ Common Issues & Fixes

### Error: "electron not found"
```bash
# Solution: npm install wasn't successful
npm install --legacy-peer-deps
```

### Error: "electron-builder not found"
```bash
# Solution: Same as above
npm install --legacy-peer-deps
```

### npm install hangs or times out
```bash
# Solution: Increase timeout and use cache
npm install --legacy-peer-deps --timeout=600000 --no-audit
```

### Build is very slow
```bash
# This is normal for first build (200+ MB Electron download)
# Subsequent builds are much faster
# Current: ~2-5 minutes per platform
# You can: npm run pack (much faster test)
```

### Port 8000 already in use
```bash
# The backend tries to start on port 8000
# Kill the process using it:
lsof -i :8000          # Find process
kill -9 <PID>          # Kill it

# Or use different port:
# (Not implemented yet, but frontend can fall back to :3000)
```

## 📋 Checklist Before Release

- [ ] `npm install --legacy-peer-deps` succeeds
- [ ] `npm run pack` creates dist/
- [ ] Linux app in dist/linux-unpacked/ runs
- [ ] No errors in console when app launches
- [ ] Chat interface loads
- [ ] Python backend starts automatically

## 🎯 Next Steps After Build

1. **Test the app:**
   ```bash
   cd desktop/dist/linux-unpacked
   ./piddy
   # Should open desktop window with Piddy chat
   ```

2. **Upload to GitHub Releases:**
   - Create tag: `git tag v1.0.0-desktop`
   - Push tag: `git push origin v1.0.0-desktop`
   - Go to GitHub Releases
   - Upload files from `dist/`

3. **Users can download** and run:
   - Windows: `Piddy-Setup.exe` → Click → Works
   - macOS: `Piddy-1.0.0.dmg` → Drag to App... → Launch
   - Linux: `Piddy-1.0.0.AppImage` → Make executable → Run

## 🔍 Troubleshooting the App

### App won't launch
1. Check Python is installed: `python3 --version`
2. Check no process is using port 8000: `lsof -i :8000`
3. Check logs: `~/.piddy/logs/`

### Backend not starting
1. Verify Python 3.9+ installed
2. Check system resources (RAM, disk space)
3. Review logs in `~/.piddy/logs/`

### Chat interface blank
1. Check browser console (Ctrl+Shift+I)
2. Check DevTools for errors
3. Verify backend is running on http://localhost:8000

## 📝 Development Mode

If you want to hack on the code:

```bash
# Terminal 1: Backend
python /workspaces/Piddy/start_piddy.py

# Terminal 2: Electron dev mode
cd /workspaces/Piddy/desktop
npm run dev
```

This enables:
- Hot reload of React changes
- Auto-restart of Electron on main.js changes
- DevTools for debugging

## 💡 Tips

- **First build is slow** - Downloads 200+ MB Electron binary once
- **Subsequent builds are faster** - Binary is cached
- **Test quickly**: `npm run pack` instead of `npm run dist`
- **Monitor logs**: `tail -f ~/.piddy/logs/piddy_desktop_*.log`
- **Clean rebuild**: `rm -rf dist node_modules && npm install --legacy-peer-deps`

---

**Still stuck?** Check [GitHub Issues](https://github.com/burchdad/Piddy/issues)
