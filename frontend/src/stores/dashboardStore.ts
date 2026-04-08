import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { repoApi } from '../services/api';
import type { CodeHealth, ProjectHealth, TeamWork } from '../types';

interface DashboardState {
  // Dashboard data
  projectHealth: ProjectHealth | null;
  codeHealth: CodeHealth | null;
  teamWork: TeamWork | null;

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
        loading: false,
        lastUpdated: null,
        error: null,

        // Fetch all dashboard data
        fetchDashboardData: async () => {
          try {
            set({ loading: true, error: null });

            // Fetch all data in parallel using fixed repository
            const [healthRes, codeRes, teamRes] = await Promise.all([
              repoApi.getHealthOverview('example', 'repo'),
              repoApi.getCodeHealth('example', 'repo'),
              repoApi.getTeamWork('example', 'repo'),
            ]);

            set({
              projectHealth: healthRes?.data ?? null,
              codeHealth: codeRes?.data ?? null,
              teamWork: teamRes?.data ?? null,
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
