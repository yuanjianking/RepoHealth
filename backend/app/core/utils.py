"""
Utility functions for RepoHealth backend.

Contains common functions used across the application to avoid duplication.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def format_timestamp(value: datetime) -> str:
    """
    Format datetime to ISO 8601 string with UTC timezone.

    Args:
        value: Datetime to format

    Returns:
        ISO 8601 string (e.g., "2026-04-08T12:00:00Z")
    """
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 string to datetime.

    Args:
        value: ISO 8601 string or None

    Returns:
        Datetime object or None if parsing fails
    """
    if not value:
        return None
    try:
        # Handle both "Z" and "+00:00" timezone formats
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def normalize_repository_name(repository: str) -> str:
    """
    Normalize repository name for filesystem use.

    Replaces '/' with '_' to create safe directory names.

    Args:
        repository: Repository name (e.g., "owner/repo")

    Returns:
        Normalized name (e.g., "owner_repo")
    """
    return repository.replace("/", "_")


def ensure_directory_exists(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The same path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON string, returning None on error.

    Args:
        text: JSON string

    Returns:
        Parsed dictionary or None
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def calculate_days_between(start: datetime, end: datetime) -> int:
    """
    Calculate days between two datetimes.

    Args:
        start: Start datetime
        end: End datetime

    Returns:
        Number of days (integer)
    """
    delta = end - start
    return max(0, delta.days)