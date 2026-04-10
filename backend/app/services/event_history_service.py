import json
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import get_settings
from app.core.utils import (
    format_timestamp,
    normalize_repository_name,
    ensure_directory_exists,
    parse_timestamp,
    utc_now,
)

EVENT_FILE_MAP = {
    "issues": "issues.jsonl",
    "pull_request": "pull_requests.jsonl",
    "issue_comment": "issue_comments.jsonl",
    "pull_request_review": "pull_request_reviews.jsonl",
    "pull_request_comment": "pull_request_reviews.jsonl",
    "push": "pushes.jsonl",
    "create": "creates.jsonl",
}




class EventHistoryService:
    def __init__(self, data_root: Path | None = None) -> None:
        if data_root is None:
            settings = get_settings()
            data_root = settings.dashboard_data_root
        self.data_root = data_root

    def _normalize_repository(self, repository: str) -> str:
        """Normalize repository name for filesystem use."""
        return normalize_repository_name(repository)

    def _ensure_repo_directory(self, repository: str) -> Path:
        """Ensure repository directory exists."""
        repo_dir = self._normalize_repository(repository)
        path = self.data_root / repo_dir
        return ensure_directory_exists(path)

    def _get_event_file_path(self, repository: str, event_type: str) -> Path:
        repo_dir = self._normalize_repository(repository)
        file_name = EVENT_FILE_MAP.get(event_type, "events.jsonl")
        return self.data_root / repo_dir / file_name

    def append_event(self, repository: str, event_type: str, payload: Dict[str, Any]) -> None:
        # 如果是issue_comment事件，检查是否为PR评论
        if event_type == "issue_comment":
            issue = payload.get("issue", {})
            if issue.get("pull_request") is not None:
                # PR评论，改为pull_request_comment事件类型
                event_type = "pull_request_comment"

        event_file = self._get_event_file_path(repository, event_type)
        # Ensure parent directory exists
        event_file.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "event_type": event_type,
            "received_at": format_timestamp(utc_now()),
            "payload": payload,
        }
        with event_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_event_history(self, repository: str, event_type: str) -> List[Dict[str, Any]]:
        file_path = self._get_event_file_path(repository, event_type)
        if not file_path.exists():
            return []

        records: List[Dict[str, Any]] = []
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                text = line.strip()
                if not text:
                    continue
                parsed = self._safe_json_loads(text)
                if not parsed:
                    continue
                # 过滤事件类型
                record_event_type = parsed.get("event_type")
                if record_event_type == event_type:
                    records.append(parsed)
                # 特殊情况：对于pull_request_comment，也接受issue_comment记录（如果是PR评论）
                elif event_type == "pull_request_comment" and record_event_type == "issue_comment":
                    # 检查是否为PR评论
                    payload = parsed.get("payload", {})
                    issue = payload.get("issue", {})
                    if issue.get("pull_request") is not None:
                        # 将其视为pull_request_comment
                        parsed["event_type"] = "pull_request_comment"
                        records.append(parsed)

        return records

    def load_all_history(self, repository: str) -> Dict[str, List[Dict[str, Any]]]:
        return {
            event_type: self.load_event_history(repository, event_type)
            for event_type in EVENT_FILE_MAP.keys()
        }

    def _safe_json_loads(self, text: str) -> Dict[str, Any] | None:
        try:
            return json.loads(text)
        except Exception:
            return None
