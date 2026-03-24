/**
 * Minimal preload for splash screen — exposes IPC for status updates
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('splash', {
  onStatus: (callback) => ipcRenderer.on('splash-status', (event, data) => callback(data)),
  onComplete: (callback) => ipcRenderer.on('splash-complete', () => callback()),
});
