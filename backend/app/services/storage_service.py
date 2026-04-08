import json
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

        This reads the file from the end to find the last non-empty line,
        which is more efficient for large files.
        """
        try:
            with file_path.open('rb') as f:
                # Go to the end of the file
                f.seek(0, 2)  # 2 = SEEK_END
                file_size = f.tell()

                # If file is empty
                if file_size == 0:
                    return None

                # Start from the end, looking for the last newline
                buffer_size = 1024
                position = file_size
                # Skip trailing newline if present
                f.seek(-1, 2)  # Go to last byte
                if f.read(1) == b'\n':
                    position -= 1  # Skip the trailing newline

                last_line = b""

                while position > 0:
                    # Calculate how much to read
                    read_size = min(buffer_size, position)
                    position -= read_size
                    f.seek(position)
                    chunk = f.read(read_size)

                    # Search for newline from the end of chunk
                    if b'\n' in chunk:
                        # Split by newline
                        lines = chunk.split(b'\n')
                        # The last element might be partial (part of a line)
                        if last_line:
                            lines[-1] = last_line + lines[-1]

                        # Now find the last complete line
                        # Start from the second last element (since the last might be partial)
                        for i in range(len(lines) - 2, -1, -1):
                            line = lines[i].strip()
                            if line:
                                try:
                                    return json.loads(line.decode('utf-8'))
                                except (json.JSONDecodeError, UnicodeDecodeError):
                                    # This might be a partial line, continue accumulating
                                    # Save the partial line and continue searching backwards
                                    last_line = b'\n'.join(lines[i:])
                                    break
                        else:
                            # No non-empty line found in this chunk
                            # Save the partial line and continue
                            last_line = lines[-1] if lines else b""
                            continue

                        break  # Found a line and returned or saved partial line
                    else:
                        # No newline in this chunk, prepend to last_line
                        last_line = chunk + last_line

                # If we've read the entire file and found no newline (single line file)
                if last_line:
                    last_line = last_line.strip()
                    if last_line:
                        try:
                            return json.loads(last_line.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
        except (OSError, IOError):
            # File might not exist or permission error
            pass

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

        project_health = data.get('projectHealth', {})
        overall_delay_rate = project_health.get('overallDelayRate', 0.0)
        quality_score = project_health.get('qualityScore', 0.0)

        if overall_delay_rate > 20 or quality_score < 50:
            overall_risk_level = 'high'
        elif overall_delay_rate > 10 or quality_score < 70:
            overall_risk_level = 'medium'
        else:
            overall_risk_level = 'low'

        risks = [
            {
                'title': 'Team workload imbalance',
                'probability': 'high' if overall_delay_rate > 15 else 'medium',
                'impact': 'high' if quality_score < 70 else 'medium',
                'description': 'Evaluate task distribution and address delayed work items.',
            }
        ]

        mitigations = [
            {'action': 'Improve PR review cadence'},
            {'action': 'Reduce issue backlog and prioritize delayed tasks'},
            {'action': 'Monitor team workload and adjust assignments'},
        ]

        return [
            {
                'data': {
                    'overall_risk_level': overall_risk_level,
                    'risks': risks,
                    'mitigations': mitigations,
                },
                'updated_at': dashboard_record.get('updated_at', ''),
            }
        ]


async def get_storage_service() -> StorageService:
    return StorageService()
