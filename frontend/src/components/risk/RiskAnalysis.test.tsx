import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import RiskAnalysis from './RiskAnalysis';

describe('RiskAnalysis', () => {
  const projectData = {
    totalIssues: 100,
    completedIssues: 50,
    delayedIssues: 50,
    totalPRs: 50,
    mergedPRs: 12,
    openPRs: 20,
    inReviewPRs: 5,
    averageCommentFrequency: 18,
    qualityScore: 45,
    saturationScore: 95,
    overallDelayRate: 20,
    daysSinceFirstIssue: 400,
  };

  it('renders card title and subtitle', () => {
    render(<RiskAnalysis projectData={projectData} />);

    expect(screen.getByText('风险分析与预警')).toBeInTheDocument();
    expect(screen.getByText('基于项目数据的 AI 风险评估')).toBeInTheDocument();
  });

  it('renders identified risk items based on project data', () => {
    render(<RiskAnalysis projectData={projectData} />);

    expect(screen.getByText('已识别风险')).toBeInTheDocument();
    expect(screen.getByText('高任务延迟率')).toBeInTheDocument();
    expect(screen.getByText('PR 合并率低')).toBeInTheDocument();
    expect(screen.getByText('高指摘频率')).toBeInTheDocument();
    expect(screen.getByText('代码质量偏低')).toBeInTheDocument();
    expect(screen.getByText('资源过饱和')).toBeInTheDocument();
    expect(screen.getByText('项目周期过长')).toBeInTheDocument();
  });

  it('displays severity badges in Chinese', () => {
    render(<RiskAnalysis projectData={projectData} />);

    expect(screen.getAllByText('高').length).toBeGreaterThan(0);
    expect(screen.getAllByText('中').length).toBeGreaterThan(0);
  });

  it('displays probability percentages and impact details', () => {
    render(<RiskAnalysis projectData={projectData} />);

    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
    expect(screen.getByText('55%')).toBeInTheDocument();
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getByText('3.5%')).toBeInTheDocument();

    expect(screen.getByText('项目进度受阻，可能导致延期交付')).toBeInTheDocument();
    expect(screen.getByText('代码集成缓慢，可能产生技术债务')).toBeInTheDocument();
    expect(screen.getByText('代码审查过程冗长，影响开发效率')).toBeInTheDocument();
    expect(screen.getByText('软件稳定性风险增加，维护成本上升')).toBeInTheDocument();
  });

  it('shows recommendation messages for each risk', () => {
    render(<RiskAnalysis projectData={projectData} />);

    expect(screen.getAllByText('需要立即采取行动').length).toBeGreaterThan(0);
    expect(screen.getAllByText('低优先级 - 定期监控').length).toBeGreaterThan(0);
  });

  it('matches snapshot with high-risk project data', () => {
    const { container } = render(<RiskAnalysis projectData={projectData} />);
    expect(container).toMatchSnapshot();
  });

  it('renders default health risk when there are no triggers', () => {
    const healthyData = {
      totalIssues: 20,
      completedIssues: 20,
      delayedIssues: 0,
      totalPRs: 10,
      mergedPRs: 10,
      openPRs: 0,
      inReviewPRs: 0,
      averageCommentFrequency: 2,
      qualityScore: 90,
      saturationScore: 50,
      overallDelayRate: 5,
      daysSinceFirstIssue: 100,
    };

    render(<RiskAnalysis projectData={healthyData} />);
    expect(screen.getByText('项目整体健康')).toBeInTheDocument();
    expect(screen.getByText('低优先级 - 定期监控')).toBeInTheDocument();
  });
});
