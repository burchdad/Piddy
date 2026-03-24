---
name: electron-desktop
description: Build cross-platform desktop apps with Electron — main/renderer processes, IPC, preload scripts, and packaging
---

# Electron Desktop Development

## Project Structure

```
desktop/
├── main.js            # Main process (Node.js)
├── preload.js         # Bridge between main and renderer
├── ipc-bridge.js      # IPC channel definitions
├── package.json       # Electron dependencies
└── python-bridge.js   # Spawn and communicate with Python backend
```

## Main Process

```javascript
const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile("index.html");
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
```

## Preload Script (Context Bridge)

```javascript
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  rpc: (method, params) => ipcRenderer.invoke("rpc-call", method, params),
  stream: (method, params, callback) => {
    const channel = `stream-${Date.now()}`;
    ipcRenderer.on(channel, (_, data) => callback(data));
    ipcRenderer.send("stream-start", { method, params, channel });
    return () => ipcRenderer.send("stream-stop", channel);
  },
  onUpdate: (callback) => ipcRenderer.on("update-available", (_, info) => callback(info)),
});
```

## IPC Communication

```javascript
// Main process — handle IPC
const { ipcMain } = require("electron");

ipcMain.handle("rpc-call", async (event, method, params) => {
  return await callPythonBackend(method, params);
});

// Renderer process — call via preload bridge
const result = await window.api.rpc("system.overview", {});
```

## Stdio RPC Pattern (Piddy's Approach)

Instead of opening network ports, communicate with Python via stdin/stdout:

```javascript
const { spawn } = require("child_process");

const python = spawn("python", ["rpc_server.py"], { stdio: ["pipe", "pipe", "pipe"] });

function sendRPC(method, params) {
  const msg = JSON.stringify({ jsonrpc: "2.0", method, params, id: Date.now() });
  python.stdin.write(msg + "\n");
}

python.stdout.on("data", (data) => {
  const response = JSON.parse(data.toString().trim());
  // handle response
});
```

## Key Patterns
- Always use `contextIsolation: true` and `nodeIntegration: false` for security
- Expose only necessary APIs through `contextBridge`
- Main process handles file system, native APIs, and spawning
- Renderer process is a standard web page (React, Vue, etc.)
- Use `ipcMain.handle` / `ipcRenderer.invoke` for async request-response
- Package with `electron-builder` or `electron-forge`
- Auto-update: `electron-updater` with GitHub Releases or S3
- Use `app.getPath("userData")` for persistent storage location
