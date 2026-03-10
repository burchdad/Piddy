/**
 * API utility for consistent backend URL usage
 */
export const getApiUrl = (endpoint) => {
  const baseUrl = import.meta.env.VITE_API_URL || '';
  if (baseUrl) {
    return `${baseUrl}${endpoint}`;
  }
  // Fallback for local development
  return endpoint;
};

export const fetchApi = async (endpoint, options = {}) => {
  const url = getApiUrl(endpoint);
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};
