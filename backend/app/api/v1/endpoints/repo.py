"""
Repo API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_storage
from app.schemas.repo import (
    HealthOverviewResponse,
    CodeHealthResponse,
    TeamWorkResponse,
    RiskAnalysisResponse,
)
from app.services.storage_service import StorageService

router = APIRouter()

@router.get("/health/{owner}/{repo}", response_model=HealthOverviewResponse)
async def get_health_overview(
    owner: str,
    repo: str,
    storage: StorageService = Depends(get_storage),
):
    """
    Get repository health overview.
    """
    repository = f"{owner}/{repo}"

    # Try to get latest dashboard data from storage
    dashboard_record = await storage.get_dashboard_data(repository)

    if dashboard_record:
        data = dashboard_record.get("data", {})
        project_health = data.get("projectHealth", {})
        return HealthOverviewResponse(
            repository=repository,
            total_issues=project_health.get("totalIssues", 0),
            completed_issues=project_health.get("completedIssues", 0),
            pending_issues=project_health.get("pendingIssues", 0),
            delayed_issues=project_health.get("delayedIssues", 0),
            total_prs=project_health.get("totalPRs", 0),
            merged_prs=project_health.get("mergedPRs", 0),
            open_prs=project_health.get("openPRs", 0),
            in_review_prs=project_health.get("inReviewPRs", 0),
            average_comment_frequency=project_health.get("averageCommentFrequency", 0.0),
            quality_score=project_health.get("qualityScore", 0.0),
            saturation_score=project_health.get("saturationScore", 0.0),
            days_since_first_issue=project_health.get("daysSinceFirstIssue", 0),
            overall_delay_rate=project_health.get("overallDelayRate", 0.0)
        )
    else:
        # Return placeholder data
        return HealthOverviewResponse(
            repository=repository,
            total_issues=0,
            completed_issues=0,
            pending_issues=0,
            delayed_issues=0,
            total_prs=0,
            merged_prs=0,
            open_prs=0,
            in_review_prs=0,
            average_comment_frequency=0.0,
            quality_score=0.0,
            saturation_score=0.0,
            days_since_first_issue=0,
            overall_delay_rate=0.0
        )


@router.get("/code-health/{owner}/{repo}", response_model=CodeHealthResponse)
async def get_code_health(
    owner: str,
    repo: str,
    storage: StorageService = Depends(get_storage),
):
    """
    Get repository code health metrics.
    """
    repository = f"{owner}/{repo}"

    # Try to get latest dashboard data from storage
    dashboard_record = await storage.get_dashboard_data(repository)

    if dashboard_record:
        data = dashboard_record.get("data", {})
        code_health = data.get("codeHealth", {})
        return CodeHealthResponse(
            repository=repository,
            unmerged_prs=code_health.get("unmergedPRs", 0),
            commit_frequency=code_health.get("commitFrequency", 0),
            single_contributor_percentage=code_health.get("singleContributorPercentage", 0.0),
            code_change_distribution=code_health.get("codeChangeDistribution", {})
        )
    else:
        # Return placeholder data
        return CodeHealthResponse(
            repository=repository,
            unmerged_prs=0,
            commit_frequency=0,
            single_contributor_percentage=0.0,
            code_change_distribution={}
        )


@router.get("/team-work/{owner}/{repo}", response_model=TeamWorkResponse)
async def get_team_work(
    owner: str,
    repo: str,
    storage: StorageService = Depends(get_storage),
):
    """
    Get repository team work metrics.
    """
    repository = f"{owner}/{repo}"

    # Try to get latest dashboard data from storage
    dashboard_record = await storage.get_dashboard_data(repository)

    if dashboard_record:
        data = dashboard_record.get("data", {})
        team_work = data.get("teamWork", {})
        return TeamWorkResponse(
            repository=repository,
            members=team_work.get("members", []),
            team_average_delay_rate=team_work.get("teamAverageDelayRate", 0.0),
            team_quality_score=team_work.get("teamQualityScore", 0.0),
            team_saturation_score=team_work.get("teamSaturationScore", 0.0)
        )
    else:
        # Return placeholder data
        return TeamWorkResponse(
            repository=repository,
            members=[],
            team_average_delay_rate=0.0,
            team_quality_score=0.0,
            team_saturation_score=0.0
        )


@router.get("/risk-analysis/{owner}/{repo}", response_model=RiskAnalysisResponse)
async def get_risk_analysis(
    owner: str,
    repo: str,
    storage: StorageService = Depends(get_storage),
):
    """
    Get repository risk analysis.
    """
    repository = f"{owner}/{repo}"

    # Try to get latest risk analysis from storage
    analysis_results = await storage.list_analysis_results(repository, limit=1)

    if analysis_results:
        latest_result = analysis_results[0]
        result_data = latest_result.get("data", {})
        return RiskAnalysisResponse(
            repository=repository,
            overall_risk_level=result_data.get("overall_risk_level", "unknown"),
            risks=result_data.get("risks", []),
            mitigations=result_data.get("mitigations", []),
            generated_at=latest_result.get("updated_at", "")
        )
    else:
        # Return placeholder data
        return RiskAnalysisResponse(
            repository=repository,
            overall_risk_level="unknown",
            risks=[],
            mitigations=[],
            generated_at=""
        )