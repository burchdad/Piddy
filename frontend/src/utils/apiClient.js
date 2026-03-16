/**
 * API Client utility for making requests to the Piddy backend
 * Automatically handles Electron and web environments
 */

function getBackendUrl() {
  // Check if running in Electron desktop app
  if (window.piddy && window.piddy.backendUrl) {
    return window.piddy.backendUrl;
  }
  
  // Check environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Default to localhost for development
  return 'http://localhost:8000';
}

/**
 * Make an API request to the backend
 * @param {string} endpoint - e.g., '/api/system/overview'
 * @param {object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise<any>}
 */
export async function apiRequest(endpoint, options = {}) {
  const backendUrl = getBackendUrl();
  const url = `${backendUrl}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`❌ API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Get the backend URL (useful for debugging)
 */
export function getApiUrl() {
  return getBackendUrl();
}

// Export default object with all methods
export default {
  request: apiRequest,
  getUrl: getApiUrl,
  getBackendUrl,
};
