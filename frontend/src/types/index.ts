
interface ProjectHealth {
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
}

interface CodeHealth {
  unmergedPRs: number;
  commitFrequency: number;
  singleContributorPercentage: number;
  codeChangeDistribution: {
    backend: number;
    frontend: number;
    infrastructure: number;
    documentation: number;
  };
}

interface TeamWork {
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
}
export type { ProjectHealth, CodeHealth, TeamWork };