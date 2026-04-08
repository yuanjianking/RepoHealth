import axios, { type AxiosResponse } from 'axios';
import type { CodeHealth, ProjectHealth, TeamWork, RiskAnalysis } from '../types';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

const isNetworkError = (error: unknown): boolean => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'request' in error &&
    !('response' in error)
  );
};

const safeGet = async <T>(url: string): Promise<AxiosResponse<T> | null> => {
  try {
    return await apiClient.get<T>(url);
  } catch (error: unknown) {
    if (isNetworkError(error)) {
      return null;
    }
    throw error;
  }
};

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add authorization token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);

    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login or refresh token
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Forbidden
      console.error('Access forbidden');
    } else if (error.response?.status === 404) {
      // Not found
      console.error('Resource not found');
    } else if (error.response?.status === 429) {
      // Rate limited
      console.error('Rate limited - too many requests');
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error occurred');
    }

    return Promise.reject(error);
  }
);

// repo integration endpoints
export const repoApi = {
  getHealthOverview: (owner: string, repo: string) =>
    safeGet<ProjectHealth>(`/repo/health/${owner}/${repo}`),

  getCodeHealth: (owner: string, repo: string) =>
    safeGet<CodeHealth>(`/repo/code-health/${owner}/${repo}`),

  getTeamWork: (owner: string, repo: string) =>
    safeGet<TeamWork>(`/repo/team-work/${owner}/${repo}`),

  getRiskAnalysis: (owner: string, repo: string) =>
    safeGet<RiskAnalysis>(`/repo/risk-analysis/${owner}/${repo}`),

};
