// Configuration for the app

export const API_BASE_URL = import.meta.env.VITE_APP_URL || 'http://localhost:8000';

export const getApiUrl = () => API_BASE_URL;

export const config = {
  apiUrl: API_BASE_URL,
  endpoints: {
    trips: '/api/trips',
    optimize: '/api/optimize',
    locations: '/api/locations',
    traffic: '/api/traffic',
  },
};
