/**
 * Preload script - runs in both main and renderer process context
 * Provides secure IPC bridge for frontend
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer process
contextBridge.exposeInMainWorld('piddy', {
  // Check backend status
  backendStatus: () => ipcRenderer.invoke('backend-status'),

  // Get app version
  getVersion: () => ipcRenderer.invoke('get-version'),

  // Open external URL
  openExternal: (url) => ipcRenderer.invoke('open-external', url),

  // Listen for backend events
  onWindowLoaded: (callback) =>
    ipcRenderer.on('window-loaded', () => callback()),

  onBackendReady: (callback) =>
    ipcRenderer.on('backend-ready', () => callback()),

  onBackendStopped: (callback) =>
    ipcRenderer.on('backend-stopped', (event, data) => callback(data))
});

console.log('[Preload] Piddy API exposed to renderer');
