/**
 * API utility for consistent backend URL usage
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

export const fetchApi = async (endpoint, method = 'GET', body = null) => {
  const url = getApiUrl(endpoint);
  console.log(`📡 fetchApi: ${method} ${url}`);
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }
  
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};
