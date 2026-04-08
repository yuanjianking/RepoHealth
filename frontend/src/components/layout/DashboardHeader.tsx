import React from 'react';
import './DashboardHeader.css';

interface DashboardHeaderProps {
  projectName: string;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ projectName }) => {
  return (
    <header className="dashboard-header">
      <div className="header-left">
        <h1 className="project-name">{projectName}</h1>
        <p className="project-subtitle">健康监控系统</p>
      </div>

      <div className="header-right"></div>
    </header>
  );
};

export default DashboardHeader;
