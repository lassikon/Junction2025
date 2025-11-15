/**
 * Centralized API configuration
 * 
 * This module provides a single source of truth for the API base URL.
 * 
 * Environment Variable:
 * - REACT_APP_API_URL: The base URL for the backend API (e.g., "http://localhost:8000")
 * 
 * Default Behavior:
 * - If REACT_APP_API_URL is not set, defaults to "/api" for same-origin requests behind nginx
 */

// Get the API URL from environment variable, defaulting to "/api"
export const API_URL = process.env.REACT_APP_API_URL || "/api";

/**
 * Build a full API endpoint URL
 * @param {string} path - The endpoint path (e.g., "/game/123" or "game/123")
 * @returns {string} - The complete API URL
 */
export const buildApiUrl = (path) => {
  // Remove leading slash from path if it exists to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  // If API_URL already ends with a slash, don't add another one
  const separator = API_URL.endsWith('/') ? '' : '/';
  
  return `${API_URL}${separator}${cleanPath}`;
};

/**
 * Get the base API URL
 * @returns {string} - The base API URL
 */
export const getApiUrl = () => API_URL;

// Default export for convenience
export default {
  API_URL,
  buildApiUrl,
  getApiUrl,
};

