import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardHeader from './DashboardHeader';

describe('DashboardHeader', () => {
  it('renders project name and subtitle', () => {
    render(<DashboardHeader projectName="Test Project" />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('健康监控系统')).toBeInTheDocument();
  });

  it('matches snapshot', () => {
    const { container } = render(<DashboardHeader projectName="Test Project" />);
    expect(container).toMatchSnapshot();
  });
});
