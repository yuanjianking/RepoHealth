import React, { useEffect } from 'react';
import { DashboardHeader, HealthOverview, CodeHealth, TeamWork, RiskAnalysis } from '../components';
import useDashboardStore from '../stores/dashboardStore';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  // Use store data instead of mock data
  const { projectHealth, codeHealth, teamWork, riskAnalysis, loading, error, fetchDashboardData } =
    useDashboardStore();

  useEffect(() => {
    // Fetch data when component mounts
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="dashboard-page">
        <DashboardHeader projectName="RepoHealth" />
        <div className="dashboard-content">
          <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>加载中...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <DashboardHeader projectName="RepoHealth" />
        <div className="dashboard-content">
          <div style={{ padding: '40px', textAlign: 'center', color: '#f44336' }}>
            错误: {error}
          </div>
        </div>
      </div>
    );
  }

  // Use store data if available, otherwise show empty state
  const displayData = {
    projectHealth: projectHealth || {
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
    codeHealth: codeHealth || {
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
    teamWork: teamWork || {
      members: [],
      teamAverageDelayRate: 0,
      teamQualityScore: 0,
      teamSaturationScore: 0,
    },
    riskAnalysis: riskAnalysis || {
      repository: 'unknown/repo',
      overall_risk_level: 'unknown',
      risks: [],
      mitigations: [],
      generated_at: '',
    },
  };

  return (
    <div className="dashboard-page">
      <DashboardHeader projectName="RepoHealth" />

      <div className="dashboard-content">
        <div className="dashboard-grid">
          <div className="grid-item full-width">
            <HealthOverview data={displayData.projectHealth} />
          </div>

          <div className="grid-item">
            <CodeHealth data={displayData.codeHealth} />
          </div>

          <div className="grid-item">
            <TeamWork data={displayData.teamWork} />
          </div>

          <div className="grid-item">
            <RiskAnalysis riskData={displayData.riskAnalysis} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
