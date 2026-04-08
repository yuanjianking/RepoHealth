import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HealthOverview from './HealthOverview';

describe('HealthOverview', () => {
  const mockData = {
    totalIssues: 40,
    completedIssues: 30,
    pendingIssues: 5,
    delayedIssues: 5,
    totalPRs: 25,
    mergedPRs: 18,
    openPRs: 5,
    inReviewPRs: 2,
    averageCommentFrequency: 6.4,
    qualityScore: 85,
    saturationScore: 78,
    daysSinceFirstIssue: 120,
    overallDelayRate: 12,
  };

  it('renders card title and subtitle', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('项目健康总览')).toBeInTheDocument();
    expect(screen.getByText('项目任务、PR及质量指标')).toBeInTheDocument();
  });

  it('displays quality score and health label', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('健康')).toBeInTheDocument();
  });

  it('displays issue completion rate and task totals', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('30 / 40 任务')).toBeInTheDocument();
  });

  it('displays PR merge rate and PR totals', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('72%')).toBeInTheDocument();
    expect(screen.getByText('18 / 25 PRs')).toBeInTheDocument();
  });

  it('displays average comment frequency and label', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('6.4')).toBeInTheDocument();
    expect(screen.getByText('评论数 / PR')).toBeInTheDocument();
  });

  it('displays saturation score and project duration', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('78')).toBeInTheDocument();
    expect(screen.getByText('资源使用效率')).toBeInTheDocument();
    expect(screen.getByText('120 天')).toBeInTheDocument();
  });

  it('displays overall delay rate', () => {
    render(<HealthOverview data={mockData} />);

    expect(screen.getByText('12%')).toBeInTheDocument();
    expect(screen.getByText('延迟任务比例')).toBeInTheDocument();
  });

  it('renders metric bars for all overview metrics', () => {
    const { container } = render(<HealthOverview data={mockData} />);
    const metricBars = container.querySelectorAll('.metric-fill');
    expect(metricBars.length).toBeGreaterThanOrEqual(6);
  });

  it('matches snapshot with healthy data', () => {
    const { container } = render(<HealthOverview data={mockData} />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with critical data', () => {
    const criticalData = {
      totalIssues: 20,
      completedIssues: 8,
      pendingIssues: 6,
      delayedIssues: 6,
      totalPRs: 15,
      mergedPRs: 5,
      openPRs: 8,
      inReviewPRs: 2,
      averageCommentFrequency: 12.3,
      qualityScore: 45,
      saturationScore: 92,
      daysSinceFirstIssue: 200,
      overallDelayRate: 25,
    };

    const { container } = render(<HealthOverview data={criticalData} />);
    expect(container).toMatchSnapshot();
  });
});
