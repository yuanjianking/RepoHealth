"""
Repo API schemas for request/response validation.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field

# Health overview schemas
class HealthOverviewResponse(BaseModel):
    """Schema for health overview response."""

    repository: str = Field(..., description="Repository full name")
    total_issues: int = Field(..., alias="totalIssues", description="Total number of issues")
    completed_issues: int = Field(..., alias="completedIssues", description="Number of completed issues")
    pending_issues: int = Field(..., alias="pendingIssues", description="Number of pending issues")
    delayed_issues: int = Field(..., alias="delayedIssues", description="Number of delayed issues")
    total_prs: int = Field(..., alias="totalPRs", description="Total number of pull requests")
    merged_prs: int = Field(..., alias="mergedPRs", description="Number of merged pull requests")
    open_prs: int = Field(..., alias="openPRs", description="Number of open pull requests")
    in_review_prs: int = Field(..., alias="inReviewPRs", description="Number of pull requests in review")
    average_comment_frequency: float = Field(..., alias="averageCommentFrequency", description="Average comments per PR")
    quality_score: float = Field(..., alias="qualityScore", ge=0, le=100, description="Quality score (0-100)")
    saturation_score: float = Field(..., alias="saturationScore", ge=0, le=100, description="Saturation score (0-100)")
    days_since_first_issue: int = Field(..., alias="daysSinceFirstIssue", description="Days since first issue")
    overall_delay_rate: float = Field(..., alias="overallDelayRate", ge=0, le=100, description="Overall delay rate (%)")

    model_config = {"populate_by_name": True}


# Code health schemas
class CodeHealthResponse(BaseModel):
    """Schema for code health response."""

    repository: str = Field(..., description="Repository full name")
    unmerged_prs: int = Field(..., alias="unmergedPRs", description="Number of unmerged pull requests")
    commit_frequency: int = Field(..., alias="commitFrequency", description="Commit frequency per week")
    single_contributor_percentage: float = Field(..., alias="singleContributorPercentage", ge=0, le=100, description="Percentage of contributions from single contributor")
    code_change_distribution: Dict[str, float] = Field(..., alias="codeChangeDistribution", description="Code change distribution across categories")

    model_config = {"populate_by_name": True}


# Team work schemas
class TeamWorkResponse(BaseModel):
    """Schema for team work response."""

    repository: str = Field(..., description="Repository full name")
    members: List[Dict[str, Any]] = Field(..., description="Team members data")
    team_average_delay_rate: float = Field(..., alias="teamAverageDelayRate", ge=0, le=100, description="Team average delay rate (%)")
    team_quality_score: float = Field(..., alias="teamQualityScore", ge=0, le=100, description="Team quality score (0-100)")
    team_saturation_score: float = Field(..., alias="teamSaturationScore", ge=0, le=100, description="Team saturation score (0-100)")

    model_config = {"populate_by_name": True}



# Risk analysis schemas
class RiskAnalysisResponse(BaseModel):
    """Schema for risk analysis response."""

    repository: str = Field(..., description="Repository full name")
    overall_risk_level: str = Field(..., description="Overall risk level")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="Risk list")
    mitigations: List[Dict[str, Any]] = Field(default_factory=list, description="Mitigation strategies")
    generated_at: str = Field(..., description="Generation timestamp")
