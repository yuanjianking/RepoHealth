#!/usr/bin/env python3
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.event_history_service import EventHistoryService

def test_pr_comment_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EventHistoryService(data_root=Path(tmpdir))
        repository = "owner/repo"

        # 模拟一个PR评论的payload（issue中包含pull_request字段）
        pr_comment_payload = {
            "action": "created",
            "issue": {
                "number": 2,
                "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/2"},
                "user": {"login": "user"},
            },
            "comment": {"id": 123, "user": {"login": "user"}},
        }

        # 模拟一个普通issue评论的payload（无pull_request字段）
        issue_comment_payload = {
            "action": "created",
            "issue": {
                "number": 1,
                "user": {"login": "user"},
                # 无pull_request字段
            },
            "comment": {"id": 456, "user": {"login": "user"}},
        }

        # 存储PR评论
        storage.append_event(repository, "issue_comment", pr_comment_payload)
        # 存储issue评论
        storage.append_event(repository, "issue_comment", issue_comment_payload)

        # 检查文件内容
        pr_comment_file = Path(tmpdir) / "owner_repo" / "pull_request_reviews.jsonl"
        issue_comment_file = Path(tmpdir) / "owner_repo" / "issue_comments.jsonl"

        print(f"PR comment file exists: {pr_comment_file.exists()}")
        print(f"Issue comment file exists: {issue_comment_file.exists()}")

        if pr_comment_file.exists():
            with pr_comment_file.open('r') as f:
                lines = [json.loads(line.strip()) for line in f if line.strip()]
                print(f"Pull request reviews file lines: {len(lines)}")
                for line in lines:
                    print(f"  event_type: {line.get('event_type')}, issue number: {line.get('payload', {}).get('issue', {}).get('number')}")

        if issue_comment_file.exists():
            with issue_comment_file.open('r') as f:
                lines = [json.loads(line.strip()) for line in f if line.strip()]
                print(f"Issue comments file lines: {len(lines)}")
                for line in lines:
                    print(f"  event_type: {line.get('event_type')}, issue number: {line.get('payload', {}).get('issue', {}).get('number')}")

        # 加载事件历史
        print("\nLoading pull_request_comment events:")
        pr_comments = storage.load_event_history(repository, "pull_request_comment")
        print(f"Found {len(pr_comments)} PR comments")
        for rec in pr_comments:
            print(f"  event_type: {rec.get('event_type')}, issue number: {rec.get('payload', {}).get('issue', {}).get('number')}")

        print("\nLoading issue_comment events:")
        issue_comments = storage.load_event_history(repository, "issue_comment")
        print(f"Found {len(issue_comments)} issue comments")
        for rec in issue_comments:
            print(f"  event_type: {rec.get('event_type')}, issue number: {rec.get('payload', {}).get('issue', {}).get('number')}")

        # 验证
        assert len(pr_comments) == 1, f"Expected 1 PR comment, got {len(pr_comments)}"
        assert len(issue_comments) == 1, f"Expected 1 issue comment, got {len(issue_comments)}"
        print("\nTest passed!")

if __name__ == "__main__":
    test_pr_comment_storage()