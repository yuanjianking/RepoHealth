import React from 'react';
import './HealthOverview.css';

interface HealthOverviewProps {
  data: {
    // 项目整体任务统计
    totalIssues: number;
    completedIssues: number;
    pendingIssues: number;
    delayedIssues: number;
    // PR 统计
    totalPRs: number;
    mergedPRs: number;
    openPRs: number;
    inReviewPRs: number;
    // 质量指标
    averageCommentFrequency: number; // 平均每个PR的评论数
    qualityScore: number; // 品质评分 0-100
    saturationScore: number; // 饱和度评分 0-100
    // 时间跨度
    daysSinceFirstIssue: number;
    // 延迟状况
    overallDelayRate: number;
  };
}

const HealthOverview: React.FC<HealthOverviewProps> = ({ data }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return '健康';
    if (score >= 60) return '中等';
    return '严重';
  };

  // 计算衍生指标
  const issueCompletionRate =
    data.totalIssues > 0 ? Math.round((data.completedIssues / data.totalIssues) * 100) : 0;
  const prMergeRate = data.totalPRs > 0 ? Math.round((data.mergedPRs / data.totalPRs) * 100) : 0;

  return (
    <div className="health-overview">
      <div className="card-header">
        <h2 className="card-title">项目健康总览</h2>
        <div className="card-subtitle">项目任务、PR及质量指标</div>
      </div>

      <div className="overview-content">
        <div className="overall-score">
          <div className="score-circle">
            <svg width="120" height="120" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" fill="none" stroke="#e0e0e0" strokeWidth="12" />
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke={getScoreColor(data.qualityScore)}
                strokeWidth="12"
                strokeDasharray={`${data.qualityScore * 3.393} 340`}
                strokeDashoffset="85"
                transform="rotate(-90 60 60)"
              />
            </svg>
            <div className="score-value">{data.qualityScore}</div>
            <div className="score-label">{getScoreLabel(data.qualityScore)}</div>
          </div>
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <div style={{ fontSize: '14px', color: '#666' }}>品质评分</div>
          </div>
        </div>

        <div className="metrics-grid">
          <div className="metric-item">
            <div className="metric-label">任务完成率</div>
            <div className="metric-value">
              <span className="value">{issueCompletionRate}%</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${issueCompletionRate}%`,
                    backgroundColor: getScoreColor(issueCompletionRate),
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                {data.completedIssues} / {data.totalIssues} 任务
              </div>
            </div>
          </div>

          <div className="metric-item">
            <div className="metric-label">PR 合并率</div>
            <div className="metric-value">
              <span className="value">{prMergeRate}%</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${prMergeRate}%`,
                    backgroundColor: getScoreColor(prMergeRate),
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                {data.mergedPRs} / {data.totalPRs} PRs
              </div>
            </div>
          </div>

          <div className="metric-item">
            <div className="metric-label">平均指摘频率</div>
            <div className="metric-value">
              <span className="value">{data.averageCommentFrequency.toFixed(1)}</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${Math.min(100, data.averageCommentFrequency * 10)}%`,
                    backgroundColor:
                      data.averageCommentFrequency <= 5
                        ? '#4caf50'
                        : data.averageCommentFrequency <= 10
                          ? '#ff9800'
                          : '#f44336',
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>评论数 / PR</div>
            </div>
          </div>

          <div className="metric-item">
            <div className="metric-label">饱和度评分</div>
            <div className="metric-value">
              <span className="value">{data.saturationScore}</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${data.saturationScore}%`,
                    backgroundColor: getScoreColor(data.saturationScore),
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>资源使用效率</div>
            </div>
          </div>

          <div className="metric-item">
            <div className="metric-label">项目运行时间</div>
            <div className="metric-value">
              <span className="value">{data.daysSinceFirstIssue} 天</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${Math.min(100, (data.daysSinceFirstIssue / 365) * 100)}%`,
                    backgroundColor: '#2196f3',
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                从第一个 Issue 起
              </div>
            </div>
          </div>

          <div className="metric-item">
            <div className="metric-label">整体延迟率</div>
            <div className="metric-value">
              <span className="value">{data.overallDelayRate}%</span>
              <div className="metric-bar">
                <div
                  className="metric-fill"
                  style={{
                    width: `${data.overallDelayRate}%`,
                    backgroundColor:
                      data.overallDelayRate <= 10
                        ? '#4caf50'
                        : data.overallDelayRate <= 20
                          ? '#ff9800'
                          : '#f44336',
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>延迟任务比例</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthOverview;
