import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import TeamWork from './TeamWork';

describe('TeamWork', () => {
  const mockData = {
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
      {
        name: 'Bob',
        totalIssues: 18,
        completedIssues: 12,
        pendingIssues: 4,
        delayedIssues: 2,
        totalPRs: 12,
        mergedPRs: 9,
        openPRs: 2,
        inReviewPRs: 1,
        commentFrequency: 8,
        qualityScore: 68,
        saturationScore: 80,
      },
      {
        name: 'Charlie',
        totalIssues: 16,
        completedIssues: 16,
        pendingIssues: 0,
        delayedIssues: 0,
        totalPRs: 8,
        mergedPRs: 7,
        openPRs: 1,
        inReviewPRs: 0,
        commentFrequency: 12,
        qualityScore: 55,
        saturationScore: 95,
      },
    ],
    teamAverageDelayRate: 15,
    teamQualityScore: 75,
    teamSaturationScore: 80,
  };

  it('renders card title and subtitle', () => {
    render(<TeamWork data={mockData} />);

    expect(screen.getByText('团队成员工作状态')).toBeInTheDocument();
    expect(screen.getByText('个人任务、PR及质量指标')).toBeInTheDocument();
  });

  it('displays team quality and saturation scores with status labels', () => {
    render(<TeamWork data={mockData} />);

    expect(screen.getByText('75')).toBeInTheDocument();
    expect(screen.getAllByText('中等').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('80')).toBeInTheDocument();
  });

  it('shows the correct score label for team quality thresholds', () => {
    const { rerender } = render(<TeamWork data={{ ...mockData, teamQualityScore: 85 }} />);
    expect(screen.getAllByText('良好').length).toBeGreaterThanOrEqual(1);

    rerender(<TeamWork data={{ ...mockData, teamQualityScore: 65 }} />);
    expect(screen.getAllByText('中等').length).toBeGreaterThan(0);

    rerender(<TeamWork data={{ ...mockData, teamQualityScore: 55 }} />);
    expect(screen.getByText('需要关注')).toBeInTheDocument();
  });

  it('renders member details and counts', () => {
    const { container } = render(<TeamWork data={mockData} />);

    expect(screen.getByText('成员详细指标')).toBeInTheDocument();
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('Charlie')).toBeInTheDocument();

    expect(screen.getByText('15/20')).toBeInTheDocument();
    expect(screen.getByText('8/10')).toBeInTheDocument();

    const memberStats = container.querySelectorAll('.member-stat');
    expect(
      Array.from(memberStats).some((el) => /延迟:\s*2/.test(el.textContent ?? ''))
    ).toBe(true);
  });

  it('displays comment frequency status for each member', () => {
    render(<TeamWork data={mockData} />);

    expect(screen.getByText('4.0 (低)')).toBeInTheDocument();
    expect(screen.getByText('12.0 (高)')).toBeInTheDocument();
    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('55')).toBeInTheDocument();
  });

  it('renders progress bars for each member', () => {
    const { container } = render(<TeamWork data={mockData} />);
    const prBars = container.querySelectorAll('.pr-bar-fill');
    expect(prBars).toHaveLength(6);
  });

  it('matches snapshot with typical data', () => {
    const { container } = render(<TeamWork data={mockData} />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with extreme data', () => {
    const extremeData = {
      members: [
        {
          name: 'Overworked',
          totalIssues: 40,
          completedIssues: 30,
          pendingIssues: 5,
          delayedIssues: 5,
          totalPRs: 20,
          mergedPRs: 15,
          openPRs: 3,
          inReviewPRs: 2,
          commentFrequency: 15,
          qualityScore: 45,
          saturationScore: 95,
        },
        {
          name: 'Underworked',
          totalIssues: 5,
          completedIssues: 5,
          pendingIssues: 0,
          delayedIssues: 0,
          totalPRs: 2,
          mergedPRs: 2,
          openPRs: 0,
          inReviewPRs: 0,
          commentFrequency: 2,
          qualityScore: 90,
          saturationScore: 40,
        },
      ],
      teamAverageDelayRate: 22.5,
      teamQualityScore: 65,
      teamSaturationScore: 80,
    };
    const { container } = render(<TeamWork data={extremeData} />);
    expect(container).toMatchSnapshot();
  });
});
