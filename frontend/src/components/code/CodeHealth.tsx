import React from 'react';
import './CodeHealth.css';

interface CodeHealthProps {
  data: {
    unmergedPRs: number;
    commitFrequency: number;
    singleContributorPercentage: number;
    codeChangeDistribution: {
      backend: number;
      frontend: number;
      infrastructure: number;
      documentation: number;
    };
  };
}

const CodeHealth: React.FC<CodeHealthProps> = ({ data }) => {
  return (
    <div className="code-health">
      <div className="card-header">
        <h2 className="card-title">代码健康度</h2>
        <div className="card-subtitle">代码质量与活动指标</div>
      </div>

      <div className="code-health-content">
        <div className="code-metrics">
          <div className="code-metric">
            <div className="code-metric-label">未合并PR数</div>
            <div className="code-metric-value">
              <span className="metric-number">{data.unmergedPRs}</span>
              <div className={`metric-trend ${data.unmergedPRs > 10 ? 'negative' : 'positive'}`}>
                {data.unmergedPRs > 10 ? '⚠️ 高' : '✓ 良好'}
              </div>
            </div>
          </div>

          <div className="code-metric">
            <div className="code-metric-label">提交频率</div>
            <div className="code-metric-value">
              <span className="metric-number">{data.commitFrequency}</span>
              <div className="metric-unit">次/周</div>
            </div>
          </div>

          <div className="code-metric">
            <div className="code-metric-label">单一贡献者比例</div>
            <div className="code-metric-value">
              <span className="metric-number">{data.singleContributorPercentage}%</span>
              <div
                className={`metric-trend ${data.singleContributorPercentage > 30 ? 'warning' : 'positive'}`}
              >
                {data.singleContributorPercentage > 30 ? '高风险' : '平衡'}
              </div>
            </div>
          </div>
        </div>

        <div className="distribution-section">
          <h3 className="section-title">代码变更分布</h3>
          <div className="distribution-chart">
            {Object.entries(data.codeChangeDistribution).map(([category, percentage]) => {
              const categoryMap: Record<string, string> = {
                backend: '后端',
                frontend: '前端',
                infrastructure: '基础设施',
                documentation: '文档',
              };
              const categoryName = categoryMap[category] || category;
              return (
                <div key={category} className="distribution-bar">
                  <div className="bar-label">{categoryName}</div>
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor:
                          category === 'backend'
                            ? '#3f51b5'
                            : category === 'frontend'
                              ? '#2196f3'
                              : category === 'infrastructure'
                                ? '#ff9800'
                                : '#4caf50',
                      }}
                    ></div>
                    <div className="bar-percentage">{percentage}%</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeHealth;
