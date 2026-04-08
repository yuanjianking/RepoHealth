// API configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// GitHub related constants
export const GITHUB = {
  EVENT_TYPES: {
    PUSH: 'push',
    PULL_REQUEST: 'pull_request',
    ISSUES: 'issues',
    PULL_REQUEST_REVIEW: 'pull_request_review',
    PULL_REQUEST_REVIEW_COMMENT: 'pull_request_review_comment',
  },
  WEBHOOK_EVENTS: [
    'push',
    'pull_request',
    'issues',
    'pull_request_review',
    'pull_request_review_comment',
  ],
  API_RATE_LIMIT: 5000, // Requests per hour for authenticated users
};

// Risk analysis constants
export const RISK = {
  SEVERITY: {
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low',
  },
  PROBABILITY_THRESHOLDS: {
    HIGH: 70,
    MEDIUM: 40,
    LOW: 0,
  },
  IMPACT_LEVELS: {
    HIGH: 'High impact - immediate action required',
    MEDIUM: 'Medium impact - monitor closely',
    LOW: 'Low impact - periodic review',
  },
};

// Chart colors
export const CHART_COLORS = {
  PRIMARY: '#1890ff',
  SUCCESS: '#52c41a',
  WARNING: '#fa8c16',
  ERROR: '#f5222d',
  INFO: '#13c2c2',
  CATEGORIES: [
    '#3f51b5', // Blue
    '#2196f3', // Light Blue
    '#4caf50', // Green
    '#ff9800', // Orange
    '#f44336', // Red
    '#9c27b0', // Purple
    '#00bcd4', // Cyan
    '#ffeb3b', // Yellow
  ],
  GRADIENT: {
    GOOD: ['#52c41a', '#b7eb8f'],
    WARNING: ['#fa8c16', '#ffd591'],
    ERROR: ['#f5222d', '#ffa39e'],
  },
};

// Local storage keys
export const STORAGE_KEYS = {
  SELECTED_REPOSITORY: 'repohealth_selected_repository',
  DASHBOARD_STATE: 'repohealth_dashboard_state',
  USER_PREFERENCES: 'repohealth_user_preferences',
  AUTH_TOKEN: 'repohealth_auth_token',
  GITHUB_TOKEN: 'repohealth_github_token',
  AI_API_KEY: 'repohealth_ai_api_key',
};

// Time periods for data aggregation
export const TIME_PERIODS = {
  DAY: '1d',
  WEEK: '7d',
  MONTH: '30d',
  QUARTER: '90d',
  YEAR: '365d',
  ALL: 'all',
};

// Default repository (for demo purposes)
export const DEFAULT_REPOSITORY = {
  OWNER: 'example',
  NAME: 'repo',
  DISPLAY_NAME: 'example/repo',
};

// Page titles
export const PAGE_TITLES = {
  DASHBOARD: 'Dashboard - RepoHealth',
  SETTINGS: 'Settings - RepoHealth',
  REPOSITORIES: 'Repositories - RepoHealth',
  ANALYTICS: 'Analytics - RepoHealth',
  DOCUMENTATION: 'Documentation - RepoHealth',
};

// Validation constants
export const VALIDATION = {
  GITHUB_USERNAME: /^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$/,
  REPOSITORY_NAME: /^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,100}$/,
  API_KEY: /^[a-zA-Z0-9_\-.]{20,}$/,
  URL: /^https?:\/\/.+/,
};
