/**
 * Frontend API Wrapper for IPC Bridge & HTTP Fallback
 * Provides clean, fetch-like interface for React components
 * Automatically uses Electron IPC when available (zero-port), falls back to HTTP
 */

/**
 * Check if running in Electron
 */
const isElectron = () => {
  return typeof window !== 'undefined' && window.piddy && window.piddy.api;
};

/**
 * Get API URL for HTTP requests
 */
export const getApiUrl = (endpoint) => {
  // Check if running in Electron with backend URL provided
  if (window.piddy && window.piddy.backendUrl) {
    return `${window.piddy.backendUrl}${endpoint}`;
  }
  
  // Check environment variable (for Vercel/production)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return `${envUrl}${endpoint}`;
  }
  
  // Fallback for local development (relative URL)
  return endpoint;
};

/**
 * Make an API call using IPC or HTTP fallback
 * @param {string} endpoint - API endpoint path (e.g., '/api/system/overview')
 * @param {Object} options - Request options (method, data, etc.)
 * @returns {Promise<Object>} Response data
 */
export async function apiCall(endpoint, options = {}) {
  const { method = 'GET', data = null, timeout = 30000 } = options;

  if (isElectron()) {
    // Use IPC bridge (zero-port)
    return await ipcCall(endpoint, method, data, timeout);
  } else {
    // Fallback to HTTP
    return await httpCall(endpoint, method, data, timeout);
  }
}

/**
 * IPC-based API call
 */
async function ipcCall(endpoint, method = 'GET', data = null, timeout = 30000) {
  try {
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`IPC call timeout after ${timeout}ms`)), timeout)
    );

    const callPromise = (async () => {
      switch (method.toUpperCase()) {
        case 'GET':
          return await window.piddy.api.get(endpoint);
        case 'POST':
          return await window.piddy.api.post(endpoint, data);
        case 'PUT':
          return await window.piddy.api.put(endpoint, data);
        case 'DELETE':
          return await window.piddy.api.delete(endpoint);
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
    })();

    return await Promise.race([callPromise, timeoutPromise]);
  } catch (error) {
    console.error(`[IPC] Error calling ${method} ${endpoint}:`, error);
    throw error;
  }
}

/**
 * HTTP fallback API call
 */
async function httpCall(endpoint, method = 'GET', data = null, timeout = 30000) {
  try {
    const url = getApiUrl(endpoint);
    console.log(`📡 HTTP: ${method} ${url}`);

    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`[HTTP] Error calling ${method} ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Legacy compatibility function
 */
export const fetchApi = async (endpoint, method = 'GET', body = null) => {
  console.log(`📡 fetchApi: ${method} ${endpoint}`);
  return apiCall(endpoint, { method, data: body });
};

/**
 * Namespace-based API object for cleaner component usage
 */
export const api = {
  // Generic methods
  get: (endpoint, options) => apiCall(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, data, options) => apiCall(endpoint, { ...options, method: 'POST', data }),
  put: (endpoint, data, options) => apiCall(endpoint, { ...options, method: 'PUT', data }),
  delete: (endpoint, options) => apiCall(endpoint, { ...options, method: 'DELETE' }),

  // System endpoints
  system: {
    overview: (options) => apiCall('/api/system/overview', { ...options, method: 'GET' }),
    health: (options) => apiCall('/api/system/health', { ...options, method: 'GET' }),
    config: (options) => apiCall('/api/system/config', { ...options, method: 'GET' }),
    metrics: (options) => apiCall('/api/system/metrics', { ...options, method: 'GET' }),
    logs: (filters, options) =>
      apiCall('/api/system/logs', { ...options, method: 'POST', data: filters }),
    status: (options) => apiCall('/api/system/status', { ...options, method: 'GET' }),
  },

  // Agent endpoints
  agents: {
    list: (options) => apiCall('/api/agents', { ...options, method: 'GET' }),
    get: (id, options) => apiCall(`/api/agents/${id}`, { ...options, method: 'GET' }),
    create: (config, options) =>
      apiCall('/api/agents', { ...options, method: 'POST', data: config }),
    update: (id, config, options) =>
      apiCall(`/api/agents/${id}`, { ...options, method: 'PUT', data: config }),
    delete: (id, options) => apiCall(`/api/agents/${id}`, { ...options, method: 'DELETE' }),
  },

  // Message endpoints
  messages: {
    list: (filters, options) =>
      apiCall('/api/messages', { ...options, method: 'POST', data: filters }),
    get: (id, options) => apiCall(`/api/messages/${id}`, { ...options, method: 'GET' }),
    send: (message, options) =>
      apiCall('/api/messages', { ...options, method: 'POST', data: message }),
  },

  // Decision endpoints
  decisions: {
    list: (filters, options) =>
      apiCall('/api/decisions', { ...options, method: 'POST', data: filters }),
    get: (id, options) => apiCall(`/api/decisions/${id}`, { ...options, method: 'GET' }),
    create: (decision, options) =>
      apiCall('/api/decisions', { ...options, method: 'POST', data: decision }),
    update: (id, decision, options) =>
      apiCall(`/api/decisions/${id}`, { ...options, method: 'PUT', data: decision }),
  },

  // Mission endpoints
  missions: {
    list: (filters, options) =>
      apiCall('/api/missions', { ...options, method: 'POST', data: filters }),
    get: (id, options) => apiCall(`/api/missions/${id}`, { ...options, method: 'GET' }),
    create: (mission, options) =>
      apiCall('/api/missions', { ...options, method: 'POST', data: mission }),
    update: (id, mission, options) =>
      apiCall(`/api/missions/${id}`, { ...options, method: 'PUT', data: mission }),
    execute: (id, options) =>
      apiCall(`/api/missions/${id}/execute`, { ...options, method: 'POST' }),
  },

  // Utility: check if using IPC or HTTP
  isUsingIPC: isElectron,
  isUsingHTTP: () => !isElectron(),
};

export default api;
