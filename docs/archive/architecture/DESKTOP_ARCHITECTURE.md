# 🖥️ Piddy Desktop App - Architecture & Development

Internal architecture documentation for the Piddy desktop application.

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Piddy Desktop Application                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │      Electron Main Process (main.js)              │  │
│  │  - Window management                              │  │
│  │  - Lifecycle management                           │  │
│  │  - IPC bridges                                    │  │
│  │  - Backend process spawning                       │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↕                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │      React Frontend (preload.js)                  │  │
│  │  - Chat interface                                 │  │
│  │  - Dashboard UI                                   │  │
│  │  - Secure API access                              │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↕                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │   Python Backend (start_piddy.py --desktop)       │  │
│  │  - FastAPI server (port 8000)                     │  │
│  │  - Background service                             │  │
│  │  - AI agent logic                                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
desktop/
├── main.js              # Electron main process
├── preload.js           # Secure context bridge
├── package.json         # Node dependencies & build config
├── assets/
│   ├── icon.png         # App icon
│   ├── icon.svg         # Icon source
│   └── icon_256.png     # High-res icon
└── dist/                # Built applications (generated)
    ├── Piddy Setup.exe                    # Windows installer
    ├── Piddy 1.0.0.exe                   # Windows portable
    ├── Piddy-1.0.0.dmg                   # macOS installer
    └── Piddy-1.0.0.AppImage              # Linux executable

src/
└── desktop_launcher.py  # Python desktop entry point

build_scripts/
├── build_desktop.sh         # Main build script
├── build_windows_installer.nsis
├── build_macos_dmg.sh
└── build_linux_appimage.sh

generate_desktop_icon.py    # Icon generation utility
desktop_dev.py              # Dev mode runner
```

## 🔄 Process Flow

### Application Startup

```
1. User clicks Piddy icon
   ↓
2. Electron main.js initializes
   ↓
3. main.js spawns Python backend
   ├─ Runs: python start_piddy.py --desktop
   ├─ Waits for: GET /health to respond
   └─ Timeout after: 30 seconds
   ↓
4. Backend started successfully
   ├─ FastAPI on :8000
   ├─ React frontend on :3000 (dev) or :8000 (prod)
   └─ Background service processing
   ↓
5. Electron creates browser window
   ├─ Loads: http://localhost:3000 (dev)
   ├─ Loads: file:// index.html (prod)
   └─ Preload script injects Piddy API
   ↓
6. React app renders
   ├─ Connects to backend API
   ├─ Initializes chat interface
   └─ Ready for user input
```

### API Communication Flow

```
┌─ React Component
│  └─ axios.get('/api/approvals')
│     └─ HTTP request to localhost:8000
│        └─ Python backend
│           └─ Response JSON
│              └─ React state update
└─ UI re-renders
```

### IPC Communication Flow

```
┌─ React Frontend
│  └─ window.piddy.backendStatus()
│     └─ ipcRenderer.invoke('backend-status')
│        └─ IPC message to main process
│           └─ main.js handler
│              └─ Returns: { ready: boolean }
│                 └─ Promise resolves in React
└─ Component updates UI
```

## 🔐 Security Architecture

### Electron Security Model

- **Context Isolation** - Main and renderer processes isolated
- **Preload Script** - Only exposes safe APIs via `contextBridge`
- **No Node Integration** - Renderer cannot access Node.js APIs
- **Sandbox** - Renderer runs in secure sandbox

### Exposed APIs (preload.js)

```javascript
window.piddy = {
  backendStatus: () => Promise<{ ready: boolean }>
  getVersion: () => Promise<{ version: string }>
  openExternal: (url: string) => Promise<void>
  onWindowLoaded: (callback: () => void) => void
  onBackendReady: (callback: () => void) => void
  onBackendStopped: (callback: (data: any) => void) => void
}
```

### Safe Communication Pattern

✅ Good:
```javascript
// Using exposed API
window.piddy.backendStatus()
  .then(status => console.log(status))
```

❌ Bad (blocked):
```javascript
// Trying to access Node
await require('child_process').spawn(...)

// Trying to access filesystem
require('fs').readFile(...)

// Trying to require from main
require('electron').app.quit()
```

## 🛠️ Development Mode

### Starting Development Server

```bash
# Terminal 1: Backend
python start_piddy.py

# Terminal 2: Electron dev
npm run dev --prefix desktop
```

This:
- Watches React source files for changes (hot reload)
- Watches Electron main process (auto-restart)
- Opens DevTools automatically
- Enables debugging

### Debugging

**React Component Issues:**
```
DevTools → Components → React Developer Tools
```

**Backend Issues:**
```
Check: http://localhost:8000/docs (FastAPI docs)
```

**Electron Issues:**
```
DevTools → Console
```

## 🚀 Production Build

### Build Flow

```
1. npm run build --prefix frontend
   └─ Creates optimized React build in frontend/dist/

2. npm run dist --prefix desktop
   └─ Reads Electron Builder config
   └─ Includes frontend build in electron
   └─ Bundles with Python interpreter
   └─ Runs platform-specific builders
   └─ Creates installers/packages

3. Result: desktop/dist/ contains:
   ├─ Windows: .exe + portable .exe
   ├─ macOS: .dmg + .zip
   └─ Linux: .AppImage + .deb
```

### Production Code Paths

In production:
- React served from: `file://` (static files, not dev server)
- API calls to: `http://localhost:8000`
- Python: Bundled with NW.js or PyOxidizer
- No console/DevTools by default

## 📊 Performance Considerations

### Startup Time
- Cold start: ~3-5 seconds (Python subprocess)
- Warm start: ~1-2 seconds (cached modules)
- Window render: ~200ms (React + CSS)

### Memory Usage
- Electron process: ~150-200 MB
- Python process: ~100-300 MB (depends on models)
- React bundles: ~50-100 MB

### Network
- All communication is localhost (no network latency)
- Typical response times: <100ms

## 🔄 Update Mechanism

### Auto-Update Architecture

```
Current App (v1.0.0)
    ↓
Check GitHub for latest release
    ↓
Found v1.1.0 available
    ↓
Show "Update Available" notification
    ↓
User clicks "Update"
    ↓
Download new version (~50-100 MB)
    ↓
Verify integrity (signature check)
    ↓
Restart with new version
    ↓
New App (v1.1.0) running
```

### Implementing Auto-Update

```javascript
// In main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  mainWindow.webContents.send('update-available');
});
```

## 🐛 Common Issues & Solutions

### Backend Won't Start
- Check Python binary is found
- Check port 8000 is not in use
- Check logs in `~/.piddy/logs/`

### React App Blank
- Check frontend bundle was built
- Check `frontend/dist/` exists
- Check browser DevTools for errors

### High Memory Usage
- Close other applications
- Clear browser cache
- Restart the app

### Network Errors
- Backend might not be ready yet
- Check health endpoint: `localhost:8000/health`

## 📝 Adding New Features

### Adding a New Electron Feature

1. **Add to preload.js:**
```javascript
myNewFeature: () => ipcRenderer.invoke('my-new-feature')
```

2. **Add handler in main.js:**
```javascript
ipcMain.handle('my-new-feature', async () => {
  return doSomething();
});
```

3. **Use in React:**
```javascript
const result = await window.piddy.myNewFeature();
```

### Adding a New Backend Endpoint

1. **Add to src/main.py:**
```python
@app.get("/api/my-endpoint")
async def my_endpoint():
    return {"data": "value"}
```

2. **Call from React:**
```javascript
const response = await fetch('http://localhost:8000/api/my-endpoint');
```

## 🎯 Testing Checklist

Before releasing a new version:

- [ ] Installer runs without errors
- [ ] App launches successfully
- [ ] Backend connects properly
- [ ] Frontend renders correctly
- [ ] Chat interface works
- [ ] No console errors
- [ ] Memory usage reasonable
- [ ] All API endpoints working
- [ ] Update notification appears (if new version)
- [ ] Quit properly (no zombie processes)

---

**Questions?** Check [issues](https://github.com/burchdad/Piddy/issues) or ask in discussions.
