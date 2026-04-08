import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { repoApi } from '../services/api';
import type { CodeHealth, ProjectHealth, TeamWork, RiskAnalysis } from '../types';

// Default repository configuration from environment variables
const DEFAULT_OWNER = import.meta.env.VITE_DEFAULT_OWNER || 'example';
const DEFAULT_REPO = import.meta.env.VITE_DEFAULT_REPO || 'repo';

interface DashboardState {
  // Dashboard data
  projectHealth: ProjectHealth | null;
  codeHealth: CodeHealth | null;
  teamWork: TeamWork | null;
  riskAnalysis: RiskAnalysis | null;

  // UI state
  loading: boolean;
  lastUpdated: string | null;
  error: string | null;

  // Actions
  fetchDashboardData: () => Promise<void>;
  refreshData: () => Promise<void>;
  clearError: () => void;
}

const useDashboardStore = create<DashboardState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        projectHealth: null,
        codeHealth: null,
        teamWork: null,
        riskAnalysis: null,
        loading: false,
        lastUpdated: null,
        error: null,

        // Fetch all dashboard data
        fetchDashboardData: async () => {
          try {
            set({ loading: true, error: null });

            // Fetch all data in parallel using fixed repository
            const [healthRes, codeRes, teamRes, riskRes] = await Promise.all([
              repoApi.getHealthOverview(DEFAULT_OWNER, DEFAULT_REPO),
              repoApi.getCodeHealth(DEFAULT_OWNER, DEFAULT_REPO),
              repoApi.getTeamWork(DEFAULT_OWNER, DEFAULT_REPO),
              repoApi.getRiskAnalysis(DEFAULT_OWNER, DEFAULT_REPO),
            ]);

            set({
              projectHealth: healthRes?.data ?? null,
              codeHealth: codeRes?.data ?? null,
              teamWork: teamRes?.data ?? null,
              riskAnalysis: riskRes?.data ?? null,
              lastUpdated: new Date().toISOString(),
              error: null,
            });
          } catch (error: unknown) {
            const message = error instanceof Error ? error.message : String(error);
            set({ error: message || 'Failed to fetch dashboard data' });
          } finally {
            set({ loading: false });
          }
        },

        // Refresh data
        refreshData: async () => {
          await get().fetchDashboardData();
        },

        // Clear error
        clearError: () => {
          set({ error: null });
        },

      }),
      {
        name: 'dashboard-storage',
        partialize: () => ({}),
      }
    )
  )
);

export default useDashboardStore;
