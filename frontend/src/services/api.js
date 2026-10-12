/**
 * api.js — Centralized API client for Auditor AI frontend.
 *
 * All API calls go through here. The base URL is read from the
 * VITE_API_URL environment variable, falling back to localhost for dev.
 *
 * Usage:
 *   import api from '../services/api';
 *   const data = await api.get('/dashboard/stats');
 *   const data = await api.post('/audits/upload', formData, { isFormData: true });
 *
 * 401 Handling:
 *   Any 401 from the backend automatically clears localStorage and
 *   dispatches a custom 'auth:logout' event. AuthContext listens to
 *   this event and redirects to login — no manual wiring required.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getHeaders = (isFormData = false) => {
  const token = localStorage.getItem('token');
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!isFormData) headers['Content-Type'] = 'application/json';
  return headers;
};

/** Clear session and notify AuthContext to redirect to login. */
const handleUnauthorized = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.dispatchEvent(new Event('auth:logout'));
};

const handleResponse = async (response, path = '') => {
  const isAuthEndpoint = path.includes('/api/auth/');
  if (response.status === 401 && !isAuthEndpoint) {
    handleUnauthorized();
    throw new Error('Session expired. Please log in again.');
  }
  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      errorDetail = errData.detail || JSON.stringify(errData);
    } catch (_) { /* ignore parse errors */ }
    throw new Error(errorDetail);
  }
  return response.json();
};

const api = {
  /** Build a full URL for a given path (used for iframes, links, etc.) */
  url: (path) => `${BASE_URL}${path}`,

  get: async (path) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(response, path);
  },

  post: async (path, body, { isFormData = false } = {}) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: getHeaders(isFormData),
      body: isFormData ? body : JSON.stringify(body),
    });
    return handleResponse(response, path);
  },

  put: async (path, body) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });
    return handleResponse(response, path);
  },

  delete: async (path) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse(response, path);
  },

  /** For streaming responses (e.g., export PDF/DOCX) — returns raw Response */
  getStream: async (path) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    if (response.status === 401) {
      handleUnauthorized();
      throw new Error('Session expired. Please log in again.');
    }
    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}`;
      try {
        const errData = await response.json();
        errorDetail = errData.detail || JSON.stringify(errData);
      } catch (_) { /* ignore */ }
      throw new Error(errorDetail);
    }
    return response;
  },
};

export default api;
