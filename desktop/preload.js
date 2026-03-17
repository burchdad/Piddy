/**
 * Preload script - runs in both main and renderer process context
 * Provides secure IPC bridge for frontend
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer process
contextBridge.exposeInMainWorld('piddy', {
  // Backend configuration
backendUrl: 'http://localhost:8000',
  
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
    ipcRenderer.on('backend-stopped', (event, data) => callback(data)),

  // ===== IPC API Bridge (zero-port architecture) =====
  // System endpoints
  api: {
    system: {
      overview: () => ipcRenderer.invoke('api:system:overview'),
      health: () => ipcRenderer.invoke('api:system:health'),
      config: () => ipcRenderer.invoke('api:system:config'),
      metrics: () => ipcRenderer.invoke('api:system:metrics'),
      logs: (filters) => ipcRenderer.invoke('api:system:logs', filters),
      status: () => ipcRenderer.invoke('api:system:status')
    },

    // Agent endpoints
    agents: {
      list: () => ipcRenderer.invoke('api:agents:list'),
      get: (id) => ipcRenderer.invoke('api:agents:get', id),
      create: (config) => ipcRenderer.invoke('api:agents:create', config),
      update: (id, config) => ipcRenderer.invoke('api:agents:update', id, config),
      delete: (id) => ipcRenderer.invoke('api:agents:delete', id),
      vote: (agentId, decision) => ipcRenderer.invoke('api:agents:vote', agentId, decision)
    },

    // Message endpoints
    messages: {
      list: (filters) => ipcRenderer.invoke('api:messages:list', filters),
      get: (id) => ipcRenderer.invoke('api:messages:get', id),
      send: (message) => ipcRenderer.invoke('api:messages:send', message),
      stream: (streamCallback) => ipcRenderer.on('api:messages:stream', (event, data) => streamCallback(data))
    },

    // Decision endpoints
    decisions: {
      list: (filters) => ipcRenderer.invoke('api:decisions:list', filters),
      get: (id) => ipcRenderer.invoke('api:decisions:get', id),
      create: (decision) => ipcRenderer.invoke('api:decisions:create', decision),
      update: (id, decision) => ipcRenderer.invoke('api:decisions:update', id, decision)
    },

    // Mission endpoints
    missions: {
      list: (filters) => ipcRenderer.invoke('api:missions:list', filters),
      get: (id) => ipcRenderer.invoke('api:missions:get', id),
      create: (mission) => ipcRenderer.invoke('api:missions:create', mission),
      update: (id, mission) => ipcRenderer.invoke('api:missions:update', id, mission),
      execute: (id) => ipcRenderer.invoke('api:missions:execute', id)
    },

    // Log endpoints
    logs: {
      list: (filters) => ipcRenderer.invoke('api:logs:list', filters),
      get: (id) => ipcRenderer.invoke('api:logs:get', id),
      clear: () => ipcRenderer.invoke('api:logs:clear'),
      export: (format) => ipcRenderer.invoke('api:logs:export', format)
    },

    // Test endpoints
    tests: {
      list: () => ipcRenderer.invoke('api:tests:list'),
      get: (id) => ipcRenderer.invoke('api:tests:get', id),
      run: (id) => ipcRenderer.invoke('api:tests:run', id),
      results: () => ipcRenderer.invoke('api:tests:results')
    },

    // Metrics endpoints
    metrics: {
      current: () => ipcRenderer.invoke('api:metrics:current'),
      history: (timeRange) => ipcRenderer.invoke('api:metrics:history', timeRange),
      aggregated: () => ipcRenderer.invoke('api:metrics:aggregated')
    },

    // Phase endpoints
    phases: {
      list: () => ipcRenderer.invoke('api:phases:list'),
      current: () => ipcRenderer.invoke('api:phases:current'),
      advance: () => ipcRenderer.invoke('api:phases:advance'),
      status: () => ipcRenderer.invoke('api:phases:status')
    },

    // Security endpoints
    security: {
      permissions: () => ipcRenderer.invoke('api:security:permissions'),
      audit: (filters) => ipcRenderer.invoke('api:security:audit', filters),
      authorize: (resource, action) => ipcRenderer.invoke('api:security:authorize', resource, action)
    },

    // Generic endpoints (for flexibility)
    get: (endpoint, queryParams) => ipcRenderer.invoke('api:get', endpoint, queryParams),
    post: (endpoint, data) => ipcRenderer.invoke('api:post', endpoint, data),
    put: (endpoint, data) => ipcRenderer.invoke('api:put', endpoint, data),
    delete: (endpoint) => ipcRenderer.invoke('api:delete', endpoint),

    // Utilities
    invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
    on: (channel, callback) => ipcRenderer.on(channel, (event, data) => callback(data))
  }
});

console.log('[Preload] Piddy API exposed to renderer');
console.log('[Preload] Backend URL:', 'http://localhost:8000');
console.log('[Preload] IPC Bridge ready - use window.piddy.api for zero-port calls');
