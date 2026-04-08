import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional


from app.core.config import get_settings
from app.core.utils import (
    format_timestamp,
    normalize_repository_name,
    ensure_directory_exists,
    parse_timestamp,
    utc_now,
)
class StorageService:
    def __init__(self, data_root: Path | None = None):
        if data_root is None:
            settings = get_settings()
            data_root = settings.dashboard_data_root
        self.data_root = data_root

    def _normalize_repository(self, repository: str) -> str:
        return normalize_repository_name(repository)

    def _ensure_repo_directory(self, repository: str) -> Path:
        repo_dir = self._normalize_repository(repository)
        path = self.data_root / repo_dir
        return ensure_directory_exists(path)

    def _get_dashboard_file(self, repository: str) -> Path:
        repo_dir = self._normalize_repository(repository)
        return self.data_root / repo_dir / 'dashboard.jsonl'

    def _get_state_file(self, repository: str) -> Path:
        repo_dir = self._normalize_repository(repository)
        return self.data_root / repo_dir / 'state.json'

    async def get_dashboard_data(self, repository: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_dashboard_file(repository)
        if not file_path.exists():
            return None

        # Read the last non-empty line from the file
        return self._read_last_jsonl_record(file_path)

    def _read_last_jsonl_record(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Read the last valid JSON record from a JSONL file.
        """
        try:
            with file_path.open('r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    return None
                last_line = lines[-1]
                return json.loads(last_line)
        except (json.JSONDecodeError, OSError, IOError):
            # File might not exist, permission error, or invalid JSON
            return None

    def load_repository_state(self, repository: str) -> Dict[str, Any]:
        state_file = self._get_state_file(repository)
        if not state_file.exists():
            return {
                'issues': {},
                'prs': {},
                'contributors': {},
                'commits': [],
                'created_at': format_timestamp(utc_now()),
                'updated_at': format_timestamp(utc_now()),
            }

        try:
            with state_file.open('r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {
                'issues': {},
                'prs': {},
                'contributors': {},
                'commits': [],
                'created_at': format_timestamp(utc_now()),
                'updated_at': format_timestamp(utc_now()),
            }

    def save_repository_state(self, repository: str, state: Dict[str, Any]) -> None:
        repo_dir = self._ensure_repo_directory(repository)
        state_file = repo_dir / 'state.json'
        with state_file.open('w', encoding='utf-8') as file:
            json.dump(state, file, indent=2)

    def save_dashboard_data(self, repository: str, record: Dict[str, Any]) -> None:
        repo_dir = self._ensure_repo_directory(repository)
        dashboard_file = repo_dir / 'dashboard.jsonl'
        with dashboard_file.open('a', encoding='utf-8') as file:
            file.write(json.dumps(record, ensure_ascii=False) + '\n')

    async def list_analysis_results(self, repository: str, limit: int = 1) -> List[Dict[str, Any]]:
        dashboard_record = await self.get_dashboard_data(repository)
        if not dashboard_record:
            return []

        data = dashboard_record.get('data', {})
        risk_analysis = data.get('riskAnalysis')
        if isinstance(risk_analysis, dict):
            return [
                {
                    'data': risk_analysis,
                    'updated_at': dashboard_record.get('updated_at', ''),
                }
            ]

        # No risk analysis found in dashboard data
        # Return empty list, which will cause the API endpoint to return placeholder data
        return []


async def get_storage_service() -> StorageService:
    return StorageService()
