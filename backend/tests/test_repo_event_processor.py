import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.services.event_history_service import EventHistoryService
from app.services.repo_event_service import RepoEventProcessor
from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_repo_event_processor_generates_dashboard_from_history(tmp_path: Path):
    storage = StorageService(data_root=tmp_path)
    history_service = EventHistoryService(data_root=tmp_path)

    # Mock AI service that returns a simple risk analysis
    mock_ai_service = AsyncMock()
    mock_ai_service.analyze_project_health.return_value = {
        'overall_risk_level': 'low',
        'risks': [],
        'mitigations': [],
        'analysis_method': 'mock',
        'analysis_summary': 'Mock analysis for testing',
    }

    processor = RepoEventProcessor(storage, history_service, ai_service=mock_ai_service)
    repository = "example/repo"

    issue_payload = {
        "action": "opened",
        "issue": {
            "number": 1,
            "created_at": "2026-04-08T00:00:00Z",
            "state": "open",
            "user": {"login": "alice"},
            "assignees": [{"login": "alice"}],
            "comments": 0,
        },
    }

    pr_payload = {
        "action": "opened",
        "pull_request": {
            "number": 2,
            "created_at": "2026-04-08T00:10:00Z",
            "state": "open",
            "merged": False,
            "user": {"login": "bob"},
            "comments": 1,
            "review_comments": 0,
            "requested_reviewers": [],
            "additions": 10,
            "deletions": 2,
        },
    }

    await processor.process_event(repository, "issues", issue_payload)
    await processor.process_event(repository, "pull_request", pr_payload)

    dashboard_file = tmp_path / "example_repo" / "dashboard.jsonl"
    assert dashboard_file.exists()

    with dashboard_file.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    assert len(lines) == 2
    latest_record = json.loads(lines[-1])
    assert latest_record["data"]["projectHealth"]["totalIssues"] == 1
    assert latest_record["data"]["projectHealth"]["totalPRs"] == 1
    assert latest_record["data"]["teamWork"]
    assert latest_record["data"]["codeHealth"]["unmergedPRs"] == 1
    # Verify risk analysis is included
    assert "riskAnalysis" in latest_record["data"]
    assert latest_record["data"]["riskAnalysis"]["overall_risk_level"] == "low"
