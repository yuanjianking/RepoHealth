import { describe, it, expect, vi, beforeEach } from 'vitest';
import { repoApi } from './api';

// Mock axios
vi.mock('axios', () => {
  const mockInstance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };

  const mockAxios = {
    create: vi.fn(() => mockInstance),
  };

  return { default: mockAxios };
});

// Mock import.meta.env
vi.stubGlobal('import', {
  meta: {
    env: {
      VITE_API_URL: 'http://test-api.example.com',
    },
  },
});

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('exports all API modules', () => {
    expect(repoApi).toBeDefined();
  });

  describe('Repository API', () => {
    it('has getHealthOverview method', () => {
      expect(typeof repoApi.getHealthOverview).toBe('function');
    });

    it('has getCodeHealth method', () => {
      expect(typeof repoApi.getCodeHealth).toBe('function');
    });

    it('has getTeamWork method', () => {
      expect(typeof repoApi.getTeamWork).toBe('function');
    });
  });
});
