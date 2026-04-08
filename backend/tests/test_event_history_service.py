import json
from pathlib import Path

from app.services.event_history_service import EventHistoryService


def test_event_history_service_appends_and_loads_events(tmp_path: Path):
    history = EventHistoryService(data_root=tmp_path)
    repository = "example/repo"
    payload = {"action": "opened", "issue": {"number": 1}}

    history.append_event(repository, "issues", payload)

    repo_dir = tmp_path / "example_repo"
    issues_file = repo_dir / "issues.jsonl"
    assert issues_file.exists()

    with issues_file.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_type"] == "issues"
    assert data["payload"] == payload

    loaded = history.load_event_history(repository, "issues")
    assert len(loaded) == 1
    assert loaded[0]["payload"] == payload

    all_history = history.load_all_history(repository)
    assert "issues" in all_history
    assert all_history["issues"][0]["payload"] == payload
