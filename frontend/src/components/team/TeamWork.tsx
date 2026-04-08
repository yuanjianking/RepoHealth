import React from 'react';
import './TeamWork.css';

interface TeamWorkProps {
  data: {
    members: Array<{
      name: string;
      // 任务指标
      totalIssues: number;
      completedIssues: number;
      pendingIssues: number;
      delayedIssues: number;
      // PR 指标
      totalPRs: number;
      mergedPRs: number;
      openPRs: number;
      inReviewPRs: number;
      commentFrequency: number; // 平均每个PR的评论数
      // 品质与饱和度
      qualityScore: number;
      saturationScore: number;
    }>;
    // 团队整体指标
    teamAverageDelayRate: number;
    teamQualityScore: number;
    teamSaturationScore: number;
  };
}

const TeamWork: React.FC<TeamWorkProps> = ({ data }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return '良好';
    if (score >= 60) return '中等';
    return '需要关注';
  };

  const getCommentFrequencyColor = (freq: number) => {
    if (freq <= 5) return '#4caf50';
    if (freq <= 10) return '#ff9800';
    return '#f44336';
  };

  const getCommentFrequencyLabel = (freq: number) => {
    if (freq <= 5) return '低';
    if (freq <= 10) return '中';
    return '高';
  };

  // 评估成员工作状态
  const evaluateMemberStatus = (member: (typeof data.members)[0]) => {
    // 计算工作量指标（任务数 + PR数）
    const workload = member.totalIssues + member.totalPRs;

    // 计算团队平均工作量
    const totalWorkload = data.members.reduce((sum, m) => sum + m.totalIssues + m.totalPRs, 0);
    const avgWorkload = totalWorkload / data.members.length;

    // 工作量相对比例
    const workloadRatio = workload / avgWorkload;

    // 判断条件
    const isIdle = workloadRatio < 0.5 && member.qualityScore >= 60; // 工作量低但质量尚可
    const isOverloaded = workloadRatio > 1.5 || member.saturationScore > 90; // 工作太多或饱和度过高
    const needsGuidance = member.qualityScore < 60 || member.commentFrequency > 10; // 质量低或指摘多

    if (isIdle) {
      return { type: 'idle', label: '空闲', color: '#ff9800', description: '工作量较少' };
    }
    if (isOverloaded) {
      return { type: 'overloaded', label: '过载', color: '#f44336', description: '工作负荷过高' };
    }
    if (needsGuidance) {
      return {
        type: 'needsGuidance',
        label: '需指导',
        color: '#2196f3',
        description: '需要技术指导',
      };
    }
    return { type: 'normal', label: '正常', color: '#4caf50', description: '工作状态良好' };
  };

  // 计算成员任务完成率的最大值用于条形图
  const maxCompletionRate = Math.max(
    ...data.members.map((m) => (m.totalIssues > 0 ? (m.completedIssues / m.totalIssues) * 100 : 0))
  );

  // 计算成员状态分布
  const memberStatuses = data.members.map(evaluateMemberStatus);
  const statusCounts = {
    idle: memberStatuses.filter((s) => s.type === 'idle').length,
    overloaded: memberStatuses.filter((s) => s.type === 'overloaded').length,
    needsGuidance: memberStatuses.filter((s) => s.type === 'needsGuidance').length,
    normal: memberStatuses.filter((s) => s.type === 'normal').length,
  };

  return (
    <div className="team-work">
      <div className="card-header">
        <h2 className="card-title">团队成员工作状态</h2>
        <div className="card-subtitle">个人任务、PR及质量指标</div>
      </div>

      <div className="team-work-content">
        <div className="team-stats">
          <div className="team-stat">
            <div className="team-stat-label">团队平均质量分</div>
            <div className="team-stat-value">
              <span className="stat-number">{data.teamQualityScore}</span>
              <div
                className="stat-badge"
                style={{ backgroundColor: getScoreColor(data.teamQualityScore) }}
              >
                {getScoreLabel(data.teamQualityScore)}
              </div>
            </div>
          </div>

          <div className="team-stat">
            <div className="team-stat-label">团队平均饱和度</div>
            <div className="team-stat-value">
              <span className="stat-number">{data.teamSaturationScore}</span>
              <div
                className="stat-badge"
                style={{ backgroundColor: getScoreColor(data.teamSaturationScore) }}
              >
                {getScoreLabel(data.teamSaturationScore)}
              </div>
            </div>
          </div>

          <div className="team-stat">
            <div className="team-stat-label">成员状态分布</div>
            <div className="team-stat-value">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#ff9800' }}>空闲: {statusCounts.idle}</span>
                  <span style={{ color: '#f44336' }}>过载: {statusCounts.overloaded}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#2196f3' }}>需指导: {statusCounts.needsGuidance}</span>
                  <span style={{ color: '#4caf50' }}>正常: {statusCounts.normal}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="team-members">
          <h3 className="section-title">成员详细指标</h3>
          <div className="members-list">
            {data.members.map((member, index) => {
              const completionRate =
                member.totalIssues > 0 ? (member.completedIssues / member.totalIssues) * 100 : 0;
              const prMergeRate =
                member.totalPRs > 0 ? (member.mergedPRs / member.totalPRs) * 100 : 0;
              const completionBarWidth =
                maxCompletionRate > 0 ? (completionRate / maxCompletionRate) * 100 : 0;
              const memberStatus = evaluateMemberStatus(member);

              return (
                <div key={index} className="member-item">
                  <div className="member-info">
                    <div className="member-name">{member.name}</div>
                    <div
                      className="member-status-badge"
                      style={{
                        backgroundColor: memberStatus.color,
                        color: 'white',
                        fontSize: '12px',
                        padding: '2px 8px',
                        borderRadius: '10px',
                        fontWeight: '600',
                        marginLeft: '8px',
                      }}
                    >
                      {memberStatus.label}
                    </div>
                    <div className="member-stats">
                      <span className="member-stat">
                        <span className="stat-label">任务:</span>
                        <span className="stat-value">
                          {member.completedIssues}/{member.totalIssues}
                        </span>
                      </span>
                      <span className="member-stat">
                        <span className="stat-label">PR:</span>
                        <span className="stat-value">
                          {member.mergedPRs}/{member.totalPRs}
                        </span>
                      </span>
                      <span className="member-stat">
                        <span className="stat-label">延迟:</span>
                        <span className="stat-value">{member.delayedIssues}</span>
                      </span>
                    </div>
                  </div>

                  <div className="member-bars">
                    <div className="pr-bar-container">
                      <div className="bar-label">任务完成率</div>
                      <div className="pr-bar">
                        <div
                          className="pr-bar-fill"
                          style={{
                            width: `${completionBarWidth}%`,
                            backgroundColor: getScoreColor(completionRate),
                          }}
                        ></div>
                      </div>
                      <div style={{ minWidth: '60px', textAlign: 'right', fontSize: '14px' }}>
                        {completionRate.toFixed(1)}%
                      </div>
                    </div>

                    <div className="pr-bar-container">
                      <div className="bar-label">PR合并率</div>
                      <div className="pr-bar">
                        <div
                          className="pr-bar-fill"
                          style={{
                            width: `${prMergeRate}%`,
                            backgroundColor: getScoreColor(prMergeRate),
                          }}
                        ></div>
                      </div>
                      <div style={{ minWidth: '60px', textAlign: 'right', fontSize: '14px' }}>
                        {prMergeRate.toFixed(1)}%
                      </div>
                    </div>

                    <div className="delay-container">
                      <div className="delay-rate">
                        <span className="delay-label">指摘频率:</span>
                        <span
                          className="delay-value"
                          style={{ color: getCommentFrequencyColor(member.commentFrequency) }}
                        >
                          {member.commentFrequency.toFixed(1)} (
                          {getCommentFrequencyLabel(member.commentFrequency)})
                        </span>
                      </div>
                      <div className="delay-rate">
                        <span className="delay-label">质量分:</span>
                        <span
                          className="delay-value"
                          style={{ color: getScoreColor(member.qualityScore) }}
                        >
                          {member.qualityScore}
                        </span>
                      </div>
                    </div>

                    <div className="saturation-analysis">
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        工作饱和度分析:
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '12px',
                        }}
                      >
                        <span>工作量: {member.totalIssues + member.totalPRs}</span>
                        <span
                          style={{
                            color:
                              member.saturationScore > 90
                                ? '#f44336'
                                : member.saturationScore > 70
                                  ? '#ff9800'
                                  : '#4caf50',
                          }}
                        >
                          饱和度: {member.saturationScore}
                        </span>
                        <span>{memberStatus.description}</span>
                      </div>
                    </div>
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

export default TeamWork;
