import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CodeHealth from './CodeHealth';

describe('CodeHealth', () => {
  const mockData = {
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

  it('renders card title and subtitle', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('代码健康度')).toBeInTheDocument();
    expect(screen.getByText('代码质量与活动指标')).toBeInTheDocument();
  });

  it('displays unmerged PRs with positive trend when <= 10', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('✓ 良好')).toBeInTheDocument();
  });

  it('displays unmerged PRs with negative trend when > 10', () => {
    const highPRData = {
      ...mockData,
      unmergedPRs: 15,
    };
    render(<CodeHealth data={highPRData} />);

    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('⚠️ 高')).toBeInTheDocument();
  });

  it('displays commit frequency with unit', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('次/周')).toBeInTheDocument();
  });

  it('displays single contributor percentage with balanced status when <= 30', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('25%')).toBeInTheDocument();
    expect(screen.getByText('平衡')).toBeInTheDocument();
  });

  it('displays single contributor percentage with warning status when > 30', () => {
    const highContributorData = {
      ...mockData,
      singleContributorPercentage: 45,
    };
    render(<CodeHealth data={highContributorData} />);

    expect(screen.getByText('45%')).toBeInTheDocument();
    expect(screen.getByText('高风险')).toBeInTheDocument();
  });

  it('renders code change distribution section with all categories', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('代码变更分布')).toBeInTheDocument();
    expect(screen.getByText('后端')).toBeInTheDocument();
    expect(screen.getByText('前端')).toBeInTheDocument();
    expect(screen.getByText('基础设施')).toBeInTheDocument();
    expect(screen.getByText('文档')).toBeInTheDocument();
  });

  it('displays correct percentages for each distribution category', () => {
    render(<CodeHealth data={mockData} />);

    expect(screen.getByText('40%')).toBeInTheDocument();
    expect(screen.getByText('35%')).toBeInTheDocument();
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getByText('10%')).toBeInTheDocument();
  });

  it('applies correct background colors to distribution bars', () => {
    const { container } = render(<CodeHealth data={mockData} />);

    const backendBar = container.querySelector('.bar-fill[style*="background-color: #3f51b5"]');
    const frontendBar = container.querySelector('.bar-fill[style*="background-color: #2196f3"]');
    const infrastructureBar = container.querySelector(
      '.bar-fill[style*="background-color: #ff9800"]'
    );
    const documentationBar = container.querySelector(
      '.bar-fill[style*="background-color: #4caf50"]'
    );

    expect(backendBar).toBeInTheDocument();
    expect(frontendBar).toBeInTheDocument();
    expect(infrastructureBar).toBeInTheDocument();
    expect(documentationBar).toBeInTheDocument();
  });

  it('matches snapshot with normal data', () => {
    const { container } = render(<CodeHealth data={mockData} />);
    expect(container).toMatchSnapshot();
  });

  it('matches snapshot with high risk data', () => {
    const highRiskData = {
      unmergedPRs: 20,
      commitFrequency: 3,
      singleContributorPercentage: 80,
      codeChangeDistribution: {
        backend: 10,
        frontend: 80,
        infrastructure: 5,
        documentation: 5,
      },
    };
    const { container } = render(<CodeHealth data={highRiskData} />);
    expect(container).toMatchSnapshot();
  });
});
