import json
from pathlib import Path

from app.services.storage_service import StorageService


def test_storage_service_can_save_and_load_dashboard(tmp_path: Path):
    storage = StorageService(data_root=tmp_path)
    repository = "example/repo"
    record = {"id": "test-id", "data": {"projectHealth": {}}, "created_at": "2026-04-08T00:00:00Z", "updated_at": "2026-04-08T00:00:00Z"}

    storage.save_dashboard_data(repository, record)

    repo_dir = tmp_path / "example_repo"
    dashboard_file = repo_dir / "dashboard.jsonl"
    assert dashboard_file.exists()

    with dashboard_file.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    assert len(lines) == 1
    loaded = json.loads(lines[0])
    assert loaded["id"] == "test-id"
    assert loaded["data"] == {"projectHealth": {}}

    latest = __import__("asyncio").run(storage.get_dashboard_data(repository))
    assert latest is not None
    assert latest["id"] == "test-id"


def test_storage_service_normalizes_repository_path(tmp_path: Path):
    storage = StorageService(data_root=tmp_path)
    repository = "owner/name"
    repo_dir = tmp_path / "owner_name"
    storage.save_dashboard_data(repository, {"id": "1", "data": {}, "created_at": "2026-04-08T00:00:00Z", "updated_at": "2026-04-08T00:00:00Z"})

    assert repo_dir.exists()
    assert (repo_dir / "dashboard.jsonl").exists()
