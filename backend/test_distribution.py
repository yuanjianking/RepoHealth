#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入所需的函数和类，避免依赖
from datetime import datetime, timezone

def _parse_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
    except ValueError:
        return None

# 手动测试分类逻辑
extension_map = {
    '.py': 'backend',
    '.java': 'backend',
    '.go': 'backend',
    '.c': 'backend',
    '.cpp': 'backend',
    '.cc': 'backend',
    '.h': 'backend',
    '.hpp': 'backend',
    '.cs': 'backend',
    '.rs': 'backend',
    '.php': 'backend',
    '.rb': 'backend',
    '.scala': 'backend',
    '.kt': 'backend',
    '.kts': 'backend',
    '.swift': 'backend',
    '.m': 'backend',
    '.js': 'frontend',
    '.jsx': 'frontend',
    '.ts': 'frontend',
    '.tsx': 'frontend',
    '.css': 'frontend',
    '.scss': 'frontend',
    '.less': 'frontend',
    '.sass': 'frontend',
    '.html': 'frontend',
    '.htm': 'frontend',
    '.vue': 'frontend',
    '.svelte': 'frontend',
    '.astro': 'frontend',
    '.yml': 'infrastructure',
    '.yaml': 'infrastructure',
    '.json': 'infrastructure',
    '.toml': 'infrastructure',
    '.ini': 'infrastructure',
    '.cfg': 'infrastructure',
    '.conf': 'infrastructure',
    '.sh': 'infrastructure',
    '.bash': 'infrastructure',
    '.ps1': 'infrastructure',
    '.bat': 'infrastructure',
    '.cmd': 'infrastructure',
    '.gitignore': 'infrastructure',
    '.dockerignore': 'infrastructure',
    '.md': 'documentation',
    '.txt': 'documentation',
    '.rst': 'documentation',
    '.adoc': 'documentation',
    '.asciidoc': 'documentation',
    '.tex': 'documentation',
    '.pdf': 'documentation',
    '.doc': 'documentation',
    '.docx': 'documentation',
    '.rtf': 'documentation',
}

special_files = {
    'Dockerfile': 'infrastructure',
    'docker-compose.yml': 'infrastructure',
    'docker-compose.yaml': 'infrastructure',
    'Makefile': 'infrastructure',
    'README': 'documentation',
    'LICENSE': 'documentation',
    'CHANGELOG': 'documentation',
}

def classify_file(file_path):
    file_name = file_path.split('/')[-1]
    if file_name in special_files:
        return special_files[file_name]

    for ext, category in extension_map.items():
        if file_path.endswith(ext):
            return category

    if file_name.startswith('.env'):
        return 'infrastructure'

    return 'unknown'

# 测试一些文件
test_files = [
    'backend/app/api/v1/endpoints/webhook.py',
    'frontend/src/components/risk/RiskAnalysis.tsx',
    '.claude/settings.local.json',
    'test.md',
    'Dockerfile',
    'README.md',
    '.env.local',
    'unknown.xyz'
]

for f in test_files:
    print(f"{f} -> {classify_file(f)}")