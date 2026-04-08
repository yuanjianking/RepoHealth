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
  if (typeof error !== 'object' || error === null) {
    return false;
  }

  const axiosError = error as Record<string, unknown>;

  // Check for standard Axios network error patterns
  const hasRequest = 'request' in axiosError;
  const hasResponse = 'response' in axiosError;
  const errorCode = axiosError.code as string | undefined;

  // Network error: request made but no response received
  if (hasRequest && !hasResponse) {
    return true;
  }

  // Check for specific network error codes
  if (errorCode) {
    const networkErrorCodes = [
      'ERR_NETWORK',
      'ECONNABORTED', // Connection aborted (timeout)
      'ECONNRESET',   // Connection reset
      'ETIMEDOUT',    // Connection timed out
    ];
    return networkErrorCodes.includes(errorCode);
  }

  // Check error message for network-related keywords
  const errorMessage = (axiosError.message as string || '').toLowerCase();
  const networkKeywords = [
    'network',
    'connection',
    'timeout',
    'aborted',
    'reset',
    'failed',
    'refused',
  ];

  return networkKeywords.some(keyword => errorMessage.includes(keyword));
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
    // Enhanced error logging with more context
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', {
        status: error.response.status,
        statusText: error.response.statusText,
        url: error.config?.url,
        method: error.config?.method,
        data: error.response.data,
        headers: error.response.headers,
      });
    } else if (error.request) {
      // Request was made but no response received (network error)
      console.error('Network Error:', {
        code: error.code,
        message: error.message,
        url: error.config?.url,
        method: error.config?.method,
        timeout: error.config?.timeout,
      });
    } else {
      // Error occurred in request configuration
      console.error('Request Configuration Error:', error.message);
    }

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
    } else if (!error.response && error.request) {
      // Network error (no response received)
      console.error('Network connection error - check if backend server is running');
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
