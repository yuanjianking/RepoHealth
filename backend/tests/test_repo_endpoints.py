from pathlib import Path

from fastapi.testclient import TestClient

from app.core.dependencies import get_storage
from app.main import app
from app.services.storage_service import StorageService


def test_team_work_endpoint_returns_placeholder(tmp_path: Path):
    storage = StorageService(data_root=tmp_path)

    def override_get_storage():
        return storage

    app.dependency_overrides[get_storage] = override_get_storage
    client = TestClient(app)

    response = client.get("/api/v1/repo/team-work/example/repo")
    assert response.status_code == 200
    data = response.json()
    assert data["repository"] == "example/repo"
    assert data["members"] == []
    assert data["teamAverageDelayRate"] == 0.0
    assert data["teamQualityScore"] == 0.0
    assert data["teamSaturationScore"] == 0.0

    app.dependency_overrides.clear()


def test_health_overview_endpoint_reads_dashboard(tmp_path: Path):
    storage = StorageService(data_root=tmp_path)
    repo_dir = tmp_path / "example_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)
    dashboard_file = repo_dir / "dashboard.jsonl"
    dashboard_file.write_text(
        "{\"id\": \"abc\", \"data\": {\"projectHealth\": {\"totalIssues\": 5, \"completedIssues\": 3, \"pendingIssues\": 2, \"delayedIssues\": 1, \"totalPRs\": 2, \"mergedPRs\": 1, \"openPRs\": 1, \"inReviewPRs\": 0, \"averageCommentFrequency\": 4.0, \"qualityScore\": 80, \"saturationScore\": 70, \"daysSinceFirstIssue\": 12, \"overallDelayRate\": 20.0}}, \"created_at\": \"2026-04-08T00:00:00Z\", \"updated_at\": \"2026-04-08T00:00:00Z\"}\n"
    )

    def override_get_storage():
        return storage

    app.dependency_overrides[get_storage] = override_get_storage
    client = TestClient(app)

    response = client.get("/api/v1/repo/health/example/repo")
    assert response.status_code == 200
    data = response.json()
    assert data["repository"] == "example/repo"
    assert data["totalIssues"] == 5
    assert data["completedIssues"] == 3
    assert data["totalPRs"] == 2
    assert data["qualityScore"] == 80

    app.dependency_overrides.clear()
