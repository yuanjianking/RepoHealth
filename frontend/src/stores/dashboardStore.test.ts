import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import type { AxiosResponse } from 'axios';
import useDashboardStore from './dashboardStore';

// Mock the API
vi.mock('../services/api', () => ({
  repoApi: {
    getRepositories: vi.fn(),
    getHealthOverview: vi.fn(),
    getCodeHealth: vi.fn(),
    getTeamWork: vi.fn(),
    getMilestones: vi.fn(),
    getRiskAnalysis: vi.fn(),
    syncRepository: vi.fn(),
  },
}));

import { repoApi } from '../services/api';

const mockedRepoApi = vi.mocked(repoApi, true);

describe('dashboardStore', () => {
  beforeEach(() => {
    // Clear all mocks and reset store before each test
    vi.clearAllMocks();
    act(() => {
      useDashboardStore.setState({
        projectHealth: null,
        codeHealth: null,
        teamWork: null,
        loading: false,
        lastUpdated: null,
        error: null,
      });
    });
  });

  it('has correct initial state', () => {
    const state = useDashboardStore.getState();

    expect(state.projectHealth).toBeNull();
    expect(state.codeHealth).toBeNull();
    expect(state.teamWork).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.lastUpdated).toBeNull();
    expect(state.error).toBeNull();
  });



  it('clears error correctly', () => {
    // First set an error
    const state = useDashboardStore.getState();
    act(() => {
      useDashboardStore.setState({ error: 'Some error' });
    });

    expect(useDashboardStore.getState().error).toBe('Some error');

    // Clear the error
    act(() => {
      state.clearError();
    });

    expect(useDashboardStore.getState().error).toBeNull();
  });

  const mockHealth = {
    totalIssues: 20,
    completedIssues: 15,
    pendingIssues: 3,
    delayedIssues: 2,
    totalPRs: 10,
    mergedPRs: 8,
    openPRs: 1,
    inReviewPRs: 1,
    averageCommentFrequency: 4.0,
    qualityScore: 85,
    saturationScore: 70,
    daysSinceFirstIssue: 90,
    overallDelayRate: 5,
  };

  const mockCode = {
    unmergedPRs: 5,
    commitFrequency: 12,
    singleContributorPercentage: 25,
    codeChangeDistribution: {
      backend: 40,
      frontend: 35,
      infrastructure: 15,
      documentation: 10,
    },
  };

  const mockTeam = {
    members: [
      {
        name: 'Alice',
        totalIssues: 20,
        completedIssues: 15,
        pendingIssues: 3,
        delayedIssues: 2,
        totalPRs: 10,
        mergedPRs: 8,
        openPRs: 1,
        inReviewPRs: 1,
        commentFrequency: 4,
        qualityScore: 85,
        saturationScore: 70,
      },
    ],
    teamAverageDelayRate: 7,
    teamQualityScore: 85,
    teamSaturationScore: 70,
  };

  describe('fetchDashboardData', () => {
    beforeEach(() => {
      mockedRepoApi.getHealthOverview.mockResolvedValue(
        { data: mockHealth } as AxiosResponse<typeof mockHealth>
      );
      mockedRepoApi.getCodeHealth.mockResolvedValue(
        { data: mockCode } as AxiosResponse<typeof mockCode>
      );
      mockedRepoApi.getTeamWork.mockResolvedValue(
        { data: mockTeam } as AxiosResponse<typeof mockTeam>
      );
    });

    it('fetches all dashboard data from the API', async () => {
      const { result } = renderHook(() => useDashboardStore());

      await act(async () => {
        await result.current.fetchDashboardData();
      });

      expect(mockedRepoApi.getHealthOverview).toHaveBeenCalledWith('example', 'repo');
      expect(mockedRepoApi.getCodeHealth).toHaveBeenCalledWith('example', 'repo');
      expect(mockedRepoApi.getTeamWork).toHaveBeenCalledWith('example', 'repo');
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).not.toBeNull();
      expect(result.current.projectHealth).toEqual(mockHealth);
      expect(result.current.codeHealth).toEqual(mockCode);
      expect(result.current.teamWork).toEqual(mockTeam);
    });
  });
});
