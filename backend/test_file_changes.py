#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.services.repo_event_service import RepoEventProcessor
from app.services.event_history_service import EventHistoryService
from app.services.storage_service import StorageService
import tempfile
import json
import asyncio

async def test_file_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageService(data_root=tmpdir)
        history_service = EventHistoryService(data_root=tmpdir)
        processor = RepoEventProcessor(storage, history_service, ai_service=None)

        # 模拟一个push事件payload
        push_payload = {
            "commits": [
                {
                    "added": ["backend/app/api/v1/endpoints/webhook.py"],
                    "removed": [],
                    "modified": [".claude/settings.local.json"]
                }
            ]
        }

        state = {
            'issues': {},
            'prs': {},
            'contributors': {},
            'commits': [],
        }

        processor._process_push_event(state, push_payload)
        print(f"State file_changes: {state.get('file_changes', [])}")

        distribution = processor._calculate_code_change_distribution(state)
        print(f"Distribution: {distribution}")

if __name__ == "__main__":
    asyncio.run(test_file_changes())