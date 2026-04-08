import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardPage from './DashboardPage';

// Mock the components to simplify testing
vi.mock('../components', () => ({
  DashboardHeader: () => <div data-testid="dashboard-header">DashboardHeader</div>,
  HealthOverview: () => <div data-testid="health-overview">HealthOverview</div>,
  CodeHealth: () => <div data-testid="code-health">CodeHealth</div>,
  TeamWork: () => <div data-testid="team-work">TeamWork</div>,
  RiskAnalysis: () => <div data-testid="risk-analysis">RiskAnalysis</div>,
}));

vi.mock('../stores/dashboardStore', () => ({
  default: vi.fn(() => ({
    projectHealth: {
      totalIssues: 0,
      completedIssues: 0,
      pendingIssues: 0,
      delayedIssues: 0,
      totalPRs: 0,
      mergedPRs: 0,
      openPRs: 0,
      inReviewPRs: 0,
      averageCommentFrequency: 0,
      qualityScore: 0,
      saturationScore: 0,
      daysSinceFirstIssue: 0,
      overallDelayRate: 0,
    },
    codeHealth: {
      unmergedPRs: 0,
      commitFrequency: 0,
      singleContributorPercentage: 0,
      codeChangeDistribution: {
        backend: 0,
        frontend: 0,
        infrastructure: 0,
        documentation: 0,
      },
    },
    teamWork: {
      members: [],
      teamAverageDelayRate: 0,
      teamQualityScore: 0,
      teamSaturationScore: 0,
    },
    loading: false,
    error: null,
    fetchDashboardData: vi.fn(),
  })),
}));

describe('DashboardPage', () => {
  it('renders without crashing', () => {
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-header')).toBeInTheDocument();
  });

  it('renders all dashboard components', () => {
    render(<DashboardPage />);

    expect(screen.getByTestId('health-overview')).toBeInTheDocument();
    expect(screen.getByTestId('code-health')).toBeInTheDocument();
    expect(screen.getByTestId('team-work')).toBeInTheDocument();
    expect(screen.getByTestId('risk-analysis')).toBeInTheDocument();
  });

  it('has correct CSS classes', () => {
    const { container } = render(<DashboardPage />);

    const dashboardElement = container.querySelector('.dashboard-page');
    expect(dashboardElement).toBeInTheDocument();

    const dashboardContent = container.querySelector('.dashboard-content');
    expect(dashboardContent).toBeInTheDocument();

    const dashboardGrid = container.querySelector('.dashboard-grid');
    expect(dashboardGrid).toBeInTheDocument();
  });

  it('matches snapshot', () => {
    const { container } = render(<DashboardPage />);
    expect(container).toMatchSnapshot();
  });
});
