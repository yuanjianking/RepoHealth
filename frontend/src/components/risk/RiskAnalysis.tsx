import React from 'react';
import './RiskAnalysis.css';

interface Risk {
  id: number;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  impact: string;
}

interface RiskAnalysisProps {
  projectData: {
    // 任务指标
    totalIssues: number;
    completedIssues: number;
    delayedIssues: number;
    // PR 指标
    totalPRs: number;
    mergedPRs: number;
    openPRs: number;
    inReviewPRs: number;
    averageCommentFrequency: number;
    // 质量指标
    qualityScore: number;
    saturationScore: number;
    overallDelayRate: number;
    daysSinceFirstIssue: number;
  };
}

const RiskAnalysis: React.FC<RiskAnalysisProps> = ({ projectData }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#d32f2f';
      case 'high':
        return '#f44336';
      case 'medium':
        return '#ff9800';
      case 'low':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 70) return '#f44336';
    if (probability >= 40) return '#ff9800';
    return '#4caf50';
  };

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '严重';
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return severity;
    }
  };

  // 基于项目数据生成风险预警
  const generateRisks = (): Risk[] => {
    const risks: Risk[] = [];
    let id = 1;

    // 任务延迟风险
    const delayedIssueRate =
      projectData.totalIssues > 0 ? (projectData.delayedIssues / projectData.totalIssues) * 100 : 0;
    if (delayedIssueRate > 20) {
      risks.push({
        id: id++,
        title: '高任务延迟率',
        severity: delayedIssueRate > 40 ? 'high' : delayedIssueRate > 20 ? 'medium' : 'low',
        probability: Math.min(90, delayedIssueRate),
        impact: '项目进度受阻，可能导致延期交付',
      });
    }

    // PR 合并风险
    const prMergeRate =
      projectData.totalPRs > 0 ? (projectData.mergedPRs / projectData.totalPRs) * 100 : 0;
    if (prMergeRate < 60) {
      risks.push({
        id: id++,
        title: 'PR 合并率低',
        severity: prMergeRate < 30 ? 'high' : prMergeRate < 50 ? 'medium' : 'low',
        probability: 100 - prMergeRate,
        impact: '代码集成缓慢，可能产生技术债务',
      });
    }

    // 指摘频率风险
    if (projectData.averageCommentFrequency > 10) {
      risks.push({
        id: id++,
        title: '高指摘频率',
        severity: projectData.averageCommentFrequency > 15 ? 'high' : 'medium',
        probability: Math.min(80, (projectData.averageCommentFrequency - 5) * 10),
        impact: '代码审查过程冗长，影响开发效率',
      });
    }

    // 质量评分风险
    if (projectData.qualityScore < 60) {
      risks.push({
        id: id++,
        title: '代码质量偏低',
        severity: projectData.qualityScore < 40 ? 'high' : 'medium',
        probability: 100 - projectData.qualityScore,
        impact: '软件稳定性风险增加，维护成本上升',
      });
    }

    // 饱和度风险
    if (projectData.saturationScore > 90) {
      risks.push({
        id: id++,
        title: '资源过饱和',
        severity: 'medium',
        probability: projectData.saturationScore - 80,
        impact: '团队负荷过高，可能导致疲劳和错误',
      });
    }

    // 长期项目风险
    if (projectData.daysSinceFirstIssue > 365) {
      risks.push({
        id: id++,
        title: '项目周期过长',
        severity: 'medium',
        probability: Math.min(70, (projectData.daysSinceFirstIssue - 365) / 10),
        impact: '项目动力下降，技术栈可能过时',
      });
    }

    // 默认风险：项目整体健康
    if (risks.length === 0) {
      risks.push({
        id: id++,
        title: '项目整体健康',
        severity: 'low',
        probability: 10,
        impact: '目前无明显风险，继续保持',
      });
    }

    return risks;
  };

  const risks = generateRisks();

  return (
    <div className="risk-analysis">
      <div className="card-header">
        <h2 className="card-title">风险分析与预警</h2>
        <div className="card-subtitle">基于项目数据的 AI 风险评估</div>
      </div>

      <div className="risk-content">
        <div className="risk-list-container">
          <h3 className="section-title">已识别风险</h3>
          <div className="risk-list">
            {risks.map((risk) => (
              <div key={risk.id} className="risk-item">
                <div className="risk-header">
                  <div className="risk-title">{risk.title}</div>
                  <div className="risk-severity">
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(risk.severity) }}
                    >
                      {getSeverityText(risk.severity)}
                    </span>
                  </div>
                </div>

                <div className="risk-metrics">
                  <div className="risk-metric">
                    <div className="metric-label">可能性</div>
                    <div className="metric-value">
                      <span className="probability-value">{risk.probability}%</span>
                      <div className="probability-bar">
                        <div
                          className="probability-fill"
                          style={{
                            width: `${risk.probability}%`,
                            backgroundColor: getProbabilityColor(risk.probability),
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="risk-metric">
                    <div className="metric-label">影响</div>
                    <div className="metric-value">
                      <span className="impact-description">{risk.impact}</span>
                    </div>
                  </div>
                </div>

                <div className="risk-recommendation">
                  <strong>建议:</strong>
                  {risk.severity === 'critical' || risk.severity === 'high'
                    ? ' 需要立即采取行动'
                    : risk.probability >= 60
                      ? ' 密切监控并制定缓解计划'
                      : ' 低优先级 - 定期监控'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAnalysis;
