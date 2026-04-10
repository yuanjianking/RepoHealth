import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.event_history_service import EventHistoryService
from app.services.storage_service import StorageService
from app.services.ai_service import get_ai_service


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
    except ValueError:
        return None


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


class RepoEventProcessor:
    DELAY_DAYS = 7

    def __init__(self, storage: StorageService, history_service: EventHistoryService, ai_service=None):
        self.storage = storage
        self.history = history_service
        self.ai_service = ai_service or get_ai_service()

    async def process_event(self, repository: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if event_type == 'ping':
            return {'message': 'pong'}

        self.history.append_event(repository, event_type, payload)

        state = self._build_state_from_history(repository)
        dashboard_record = await self._build_dashboard_record(repository, state)
        self.storage.save_dashboard_data(repository, dashboard_record)

        return dashboard_record

    def _build_state_from_history(self, repository: str) -> Dict[str, Any]:
        history = self.history.load_all_history(repository)
        state = {
            'issues': {},
            'prs': {},
            'contributors': {},
            'commits': [],
            'earliest_timestamp': None,
        }

        for event_type, records in history.items():
            for record in records:
                payload = record.get('payload', {})
                # 更新最早时间戳
                received_at = record.get('received_at')
                if received_at:
                    received_time = _parse_timestamp(received_at)
                    if received_time:
                        if state['earliest_timestamp'] is None or received_time < state['earliest_timestamp']:
                            state['earliest_timestamp'] = received_time

                if event_type == 'issues':
                    self._process_issues_event(state, payload)
                elif event_type == 'pull_request':
                    self._process_pull_request_event(state, payload)
                elif event_type == 'issue_comment':
                    self._process_issue_comment_event(state, payload)
                elif event_type == 'pull_request_comment':
                    self._process_issue_comment_event(state, payload)
                elif event_type == 'pull_request_review':
                    self._process_pull_request_review_event(state, payload)
                elif event_type == 'push':
                    self._process_push_event(state, payload)
                elif event_type == 'create':
                    # 暂时忽略create事件，但记录日志
                    pass

        return state

    def _get_issue_owner(self, issue: Dict[str, Any]) -> str:
        assignees = issue.get('assignees') or []
        if assignees:
            # Handle both dict assignees (from payload) and string assignees (from state)
            first_assignee = assignees[0]
            if isinstance(first_assignee, dict):
                return first_assignee.get('login', issue.get('user', {}).get('login', 'unknown'))
            else:
                # assignee is already a string (from state)
                return str(first_assignee)
        return issue.get('user', {}).get('login', 'unknown')

    def _get_pr_owner(self, pr: Dict[str, Any]) -> str:
        return pr.get('user', {}).get('login', 'unknown')

    def _ensure_member(self, state: Dict[str, Any], login: str) -> None:
        if login not in state['contributors']:
            state['contributors'][login] = {
                'login': login,
            }

    def _process_issues_event(self, state: Dict[str, Any], payload: Dict[str, Any]) -> None:
        issue = payload.get('issue', {})
        action = payload.get('action')
        number = issue.get('number')
        if number is None:
            return

        owner = self._get_issue_owner(issue)
        self._ensure_member(state, owner)

        issue_state = state['issues'].get(str(number), {
            'number': number,
            'created_at': issue.get('created_at'),
            'closed_at': issue.get('closed_at'),
            'state': issue.get('state', 'open'),
            'user': issue.get('user', {}).get('login', 'unknown'),
            'assignees': [owner],
            'comments': issue.get('comments', 0),
        })

        issue_state['created_at'] = issue.get('created_at') or issue_state.get('created_at')
        issue_state['state'] = issue.get('state', issue_state['state'])
        issue_state['closed_at'] = issue.get('closed_at') or issue_state.get('closed_at')
        issue_state['comments'] = issue.get('comments', issue_state.get('comments', 0))
        issue_state['assignees'] = [owner]

        if action in {'opened', 'reopened'}:
            issue_state['state'] = 'open'
            issue_state['closed_at'] = None
        elif action == 'closed':
            issue_state['state'] = 'closed'
            issue_state['closed_at'] = issue.get('closed_at', _format_timestamp(_utc_now()))

        state['issues'][str(number)] = issue_state

    def _process_pull_request_event(self, state: Dict[str, Any], payload: Dict[str, Any]) -> None:
        pr = payload.get('pull_request', {})
        action = payload.get('action')
        number = pr.get('number')
        if number is None:
            return

        owner = self._get_pr_owner(pr)
        self._ensure_member(state, owner)

        pr_state = state['prs'].get(str(number), {
            'number': number,
            'created_at': pr.get('created_at'),
            'closed_at': pr.get('closed_at'),
            'merged_at': pr.get('merged_at'),
            'state': pr.get('state', 'open'),
            'merged': pr.get('merged', False),
            'user': owner,
            'comments': pr.get('comments', 0) + pr.get('review_comments', 0),
            'requested_reviewers': [r.get('login') for r in pr.get('requested_reviewers', []) if r.get('login')],
            'review_state': 'pending',
            'additions': pr.get('additions', 0),
            'deletions': pr.get('deletions', 0),
        })

        pr_state['created_at'] = pr.get('created_at') or pr_state.get('created_at')
        pr_state['closed_at'] = pr.get('closed_at') or pr_state.get('closed_at')
        pr_state['merged_at'] = pr.get('merged_at') or pr_state.get('merged_at')
        pr_state['comments'] = pr.get('comments', pr_state.get('comments', 0)) + pr.get('review_comments', 0)
        pr_state['requested_reviewers'] = [r.get('login') for r in pr.get('requested_reviewers', []) if r.get('login')]
        pr_state['additions'] = pr.get('additions', pr_state.get('additions', 0))
        pr_state['deletions'] = pr.get('deletions', pr_state.get('deletions', 0))

        if action in {'opened', 'reopened'}:
            pr_state['state'] = 'open'
            pr_state['merged'] = False
            pr_state['closed_at'] = None
            pr_state['merged_at'] = None
        elif action == 'closed':
            pr_state['state'] = 'closed'
            pr_state['merged'] = pr.get('merged', False)
            pr_state['closed_at'] = pr.get('closed_at', _format_timestamp(_utc_now()))
            if pr_state['merged']:
                pr_state['merged_at'] = pr.get('merged_at', _format_timestamp(_utc_now()))
        elif action == 'synchronize':
            pr_state['state'] = 'open'

        state['prs'][str(number)] = pr_state

    def _process_issue_comment_event(self, state: Dict[str, Any], payload: Dict[str, Any]) -> None:
        issue = payload.get('issue', {})
        if not issue:
            return

        pr_marker = issue.get('pull_request')
        comment = payload.get('comment', {})
        if pr_marker:
            pr_number = issue.get('number')
            pr_state = state['prs'].get(str(pr_number))
            if pr_state:
                pr_state['comments'] = pr_state.get('comments', 0) + 1
                state['prs'][str(pr_number)] = pr_state

    def _process_pull_request_review_event(self, state: Dict[str, Any], payload: Dict[str, Any]) -> None:
        pr = payload.get('pull_request', {})
        review = payload.get('review', {})
        number = pr.get('number')
        if number is None:
            return

        pr_state = state['prs'].get(str(number))
        if not pr_state:
            return

        review_state = review.get('state', '').lower()
        if review_state in {'approved', 'changes_requested', 'commented'}:
            pr_state['review_state'] = review_state
            pr_state['comments'] = pr_state.get('comments', 0) + 1
            state['prs'][str(number)] = pr_state

    def _process_push_event(self, state: Dict[str, Any], payload: Dict[str, Any]) -> None:
        commits = payload.get('commits', [])
        if not isinstance(commits, list):
            return

        event_time = _utc_now()
        commit_count = len(commits)
        state['commits'].append({
            'timestamp': _format_timestamp(event_time),
            'count': commit_count,
        })

        # 收集文件变更信息
        if 'file_changes' not in state:
            state['file_changes'] = []

        total_files = 0
        for commit in commits:
            added = commit.get('added', [])
            removed = commit.get('removed', [])
            modified = commit.get('modified', [])

            # 合并所有变更文件
            all_files = added + removed + modified
            total_files += len(all_files)
            for file_path in all_files:
                state['file_changes'].append(file_path)
        print(f"DEBUG: _process_push_event processed {len(commits)} commits, {total_files} files")

    def _collect_member_metrics(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        member_map: Dict[str, Dict[str, Any]] = {}
        issues = list(state['issues'].values())
        prs = list(state['prs'].values())

        for issue in issues:
            owner = self._get_issue_owner(issue)
            self._ensure_member(state, owner)
            stats = member_map.setdefault(owner, {
                'name': owner,
                'totalIssues': 0,
                'completedIssues': 0,
                'pendingIssues': 0,
                'delayedIssues': 0,
                'totalPRs': 0,
                'mergedPRs': 0,
                'openPRs': 0,
                'inReviewPRs': 0,
                'commentFrequency': 0.0,
                'qualityScore': 0.0,
                'saturationScore': 0.0,
                'sumComments': 0,
            })

            stats['totalIssues'] += 1
            if issue.get('state') == 'closed':
                stats['completedIssues'] += 1
            else:
                stats['pendingIssues'] += 1
                if self._is_delayed(issue.get('created_at')):
                    stats['delayedIssues'] += 1

        for pr in prs:
            owner = pr.get('user', 'unknown')
            self._ensure_member(state, owner)
            stats = member_map.setdefault(owner, {
                'name': owner,
                'totalIssues': 0,
                'completedIssues': 0,
                'pendingIssues': 0,
                'delayedIssues': 0,
                'totalPRs': 0,
                'mergedPRs': 0,
                'openPRs': 0,
                'inReviewPRs': 0,
                'commentFrequency': 0.0,
                'qualityScore': 0.0,
                'saturationScore': 0.0,
                'sumComments': 0,
            })

            stats['totalPRs'] += 1
            stats['sumComments'] += pr.get('comments', 0)
            if pr.get('state') == 'open':
                stats['openPRs'] += 1
                if pr.get('review_state') not in {'approved', 'none'}:
                    stats['inReviewPRs'] += 1
            if pr.get('merged'):
                stats['mergedPRs'] += 1

        members: List[Dict[str, Any]] = []
        for login, stats in member_map.items():
            if stats['totalPRs'] > 0:
                stats['commentFrequency'] = round(stats['sumComments'] / stats['totalPRs'], 1)
            else:
                stats['commentFrequency'] = 0.0
            stats['qualityScore'] = self._calculate_quality_score(
                stats['mergedPRs'], stats['totalPRs'], stats['completedIssues'], stats['totalIssues']
            )
            stats['saturationScore'] = self._calculate_saturation_score(stats['pendingIssues'], stats['openPRs'])
            members.append({
                'name': stats['name'],
                'totalIssues': stats['totalIssues'],
                'completedIssues': stats['completedIssues'],
                'pendingIssues': stats['pendingIssues'],
                'delayedIssues': stats['delayedIssues'],
                'totalPRs': stats['totalPRs'],
                'mergedPRs': stats['mergedPRs'],
                'openPRs': stats['openPRs'],
                'inReviewPRs': stats['inReviewPRs'],
                'commentFrequency': stats['commentFrequency'],
                'qualityScore': stats['qualityScore'],
                'saturationScore': stats['saturationScore'],
            })

        return sorted(members, key=lambda item: (-item['totalPRs'], -item['totalIssues'], item['name']))

    async def _build_dashboard_record(self, repository: str, state: Dict[str, Any]) -> Dict[str, Any]:
        now = _utc_now()
        project_health = self._build_project_health(state)
        code_health = self._build_code_health(state)
        team_work = self._build_team_work(state)

        # Generate AI-powered risk analysis
        project_data = {
            'projectHealth': project_health,
            'codeHealth': code_health,
            'teamWork': team_work,
        }
        risk_analysis = await self.ai_service.analyze_project_health(project_data)

        return {
            'id': str(uuid4()),
            'data': {
                'projectHealth': project_health,
                'codeHealth': code_health,
                'teamWork': team_work,
                'riskAnalysis': risk_analysis,
            },
            'created_at': _format_timestamp(now),
            'updated_at': _format_timestamp(now),
        }

    def _build_project_health(self, state: Dict[str, Any]) -> Dict[str, Any]:
        issues = list(state['issues'].values())
        prs = list(state['prs'].values())
        total_issues = len(issues)
        completed_issues = sum(1 for issue in issues if issue.get('state') == 'closed')
        pending_issues = sum(1 for issue in issues if issue.get('state') == 'open')
        delayed_issues = sum(1 for issue in issues if issue.get('state') == 'open' and self._is_delayed(issue.get('created_at')))
        total_prs = len(prs)
        merged_prs = sum(1 for pr in prs if pr.get('merged'))
        open_prs = sum(1 for pr in prs if pr.get('state') == 'open')
        in_review_prs = sum(1 for pr in prs if pr.get('state') == 'open' and pr.get('review_state') not in {'approved', 'none'})
        average_comment_frequency = self._calculate_average_comment_frequency(prs)
        quality_score = self._calculate_quality_score(merged_prs, total_prs, completed_issues, total_issues)
        saturation_score = self._calculate_saturation_score(pending_issues, open_prs)
        earliest_issue = self._earliest_issue_time(issues)
        # 使用最早的事件时间（包括push等）或issue时间
        earliest_project = state.get('earliest_timestamp')
        if earliest_issue and earliest_project:
            earliest = min(earliest_issue, earliest_project)
        elif earliest_project:
            earliest = earliest_project
        else:
            earliest = earliest_issue
        days_since_first_issue = self._calculate_days_since_first_issue(earliest)
        overall_delay_rate = self._calculate_delay_rate(delayed_issues, total_issues)

        return {
            'totalIssues': total_issues,
            'completedIssues': completed_issues,
            'pendingIssues': pending_issues,
            'delayedIssues': delayed_issues,
            'totalPRs': total_prs,
            'mergedPRs': merged_prs,
            'openPRs': open_prs,
            'inReviewPRs': in_review_prs,
            'averageCommentFrequency': average_comment_frequency,
            'qualityScore': quality_score,
            'saturationScore': saturation_score,
            'daysSinceFirstIssue': days_since_first_issue,
            'overallDelayRate': overall_delay_rate,
        }

    def _build_code_health(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prs = list(state['prs'].values())
        unmerged_prs = sum(1 for pr in prs if pr.get('state') == 'open')
        commit_frequency = self._calculate_commit_frequency(state)
        single_contributor_percentage = self._calculate_single_contributor_percentage(state)
        code_change_distribution = self._calculate_code_change_distribution(state)

        return {
            'unmergedPRs': unmerged_prs,
            'commitFrequency': commit_frequency,
            'singleContributorPercentage': single_contributor_percentage,
            'codeChangeDistribution': code_change_distribution,
        }

    def _build_team_work(self, state: Dict[str, Any]) -> Dict[str, Any]:
        members = self._collect_member_metrics(state)
        team_average_delay_rate = self._calculate_delay_rate(
            sum(member['delayedIssues'] for member in members), sum(member['totalIssues'] for member in members)
        )
        team_quality_score = self._average([member['qualityScore'] for member in members])
        team_saturation_score = self._average([member['saturationScore'] for member in members])

        return {
            'members': members,
            'teamAverageDelayRate': team_average_delay_rate,
            'teamQualityScore': team_quality_score,
            'teamSaturationScore': team_saturation_score,
        }

    def _is_delayed(self, created_at: Optional[str], now: Optional[datetime] = None) -> bool:
        if not created_at:
            return False
        born = _parse_timestamp(created_at)
        if not born:
            return False
        now = now or _utc_now()
        return now - born > timedelta(days=self.DELAY_DAYS)

    def _calculate_average_comment_frequency(self, prs: List[Dict[str, Any]]) -> float:
        total_prs = len(prs)
        if total_prs == 0:
            return 0.0
        total_comments = sum(pr.get('comments', 0) for pr in prs)
        return round(total_comments / total_prs, 1)

    def _calculate_quality_score(self, merged_prs: int, total_prs: int, completed_issues: int, total_issues: int) -> int:
        """
        计算质量分数。

        分数基于：
        - PR合并率（50分）
        - Issue完成率（50分）

        如果某一类数据缺失，则只使用另一类数据计算（总分仍为100）。
        如果两类数据都缺失，返回0表示无法评估。
        """
        if total_prs == 0 and total_issues == 0:
            # 无数据，无法评估质量
            return 0

        pr_score = 0
        issue_score = 0

        if total_prs > 0:
            pr_score = (merged_prs / total_prs) * 50
        elif total_issues == 0:
            # 只有PR数据，PR分数占全部100分
            pr_score = (merged_prs / total_prs) * 100

        if total_issues > 0:
            issue_score = (completed_issues / total_issues) * 50
        elif total_prs == 0:
            # 只有Issue数据，Issue分数占全部100分
            issue_score = (completed_issues / total_issues) * 100

        score = int(round(min(100, max(0, pr_score + issue_score))))
        return score

    def _calculate_saturation_score(self, pending_issues: int, open_prs: int) -> int:
        """
        计算饱和度分数。

        分数反映团队工作负载饱和度：
        - 每个pending issue减少2分
        - 每个open PR减少3分
        - 最多减少100分（最低0分）

        公式可以基于历史数据进一步优化。
        """
        reduction = pending_issues * 2 + open_prs * 3
        score = 100 - min(100, reduction)  # 最多扣100分
        return max(0, score)  # 确保不低于0

    def _calculate_commit_frequency(self, state: Dict[str, Any]) -> int:
        commits = state.get('commits', [])
        if not commits:
            return 0
        count = sum(entry.get('count', 0) for entry in commits)
        timestamps = [_parse_timestamp(entry.get('timestamp')) for entry in commits]
        timestamps = [t for t in timestamps if t]
        if not timestamps:
            return 0
        duration_days = max(1, (max(timestamps) - min(timestamps)).days)
        return int(round(count / max(1, duration_days / 7)))

    def _calculate_single_contributor_percentage(self, state: Dict[str, Any]) -> int:
        contributors = state.get('contributors', {})
        if not contributors:
            return 0
        activity = {}
        for issue in state['issues'].values():
            assignees = issue.get('assignees', [])
            if assignees and len(assignees) > 0:
                owner = assignees[0]
            else:
                owner = issue.get('user', 'unknown')
            activity[owner] = activity.get(owner, 0) + 1
        for pr in state['prs'].values():
            owner = pr.get('user', 'unknown')
            activity[owner] = activity.get(owner, 0) + 1
        total = sum(activity.values())
        if total == 0:
            return 0
        max_share = max(activity.values()) / total
        return int(round(max_share * 100))

    def _calculate_code_change_distribution(self, state: Dict[str, Any]) -> Dict[str, int]:
        """
        计算代码变更类型分布。

        基于push事件中的文件变更分析，根据文件扩展名分类：
        - backend: .py, .java, .go, .c, .cpp, .cs, .rs, .php, .rb, .scala, .kt, .swift
        - frontend: .js, .ts, .tsx, .jsx, .css, .scss, .less, .sass, .html, .htm, .vue, .svelte
        - infrastructure: .yml, .yaml, .json, .toml, .ini, .cfg, .conf, Dockerfile, .sh, .bash, .ps1, .gitignore, .env*, docker-compose.*
        - documentation: .md, .txt, .rst, .adoc, .asciidoc, .tex, .pdf, .doc, .docx
        """
        # 从state中获取文件变更历史
        file_changes = state.get('file_changes', [])
        print(f"DEBUG: _calculate_code_change_distribution called, file_changes length: {len(file_changes)}")
        if not file_changes:
            # 无文件变更数据，返回零分布
            print("DEBUG: No file changes, returning zero distribution")
            return {
                'backend': 0,
                'frontend': 0,
                'infrastructure': 0,
                'documentation': 0,
            }

        # 分类统计
        category_counts = {
            'backend': 0,
            'frontend': 0,
            'infrastructure': 0,
            'documentation': 0,
            'unknown': 0,
        }

        # 定义文件扩展名到分类的映射
        extension_map = {
            # backend
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
            # frontend
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
            # infrastructure
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
            # documentation
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

        # 特殊文件处理（无扩展名或特殊文件名）
        special_files = {
            'Dockerfile': 'infrastructure',
            'docker-compose.yml': 'infrastructure',
            'docker-compose.yaml': 'infrastructure',
            'Makefile': 'infrastructure',
            'README': 'documentation',
            'LICENSE': 'documentation',
            'CHANGELOG': 'documentation',
        }

        for file_path in file_changes:
            # 检查是否为特殊文件
            file_name = file_path.split('/')[-1]
            if file_name in special_files:
                category = special_files[file_name]
                category_counts[category] += 1
                continue

            # 检查文件扩展名
            matched = False
            for ext, category in extension_map.items():
                if file_path.endswith(ext):
                    category_counts[category] += 1
                    matched = True
                    break

            # 环境文件处理（如.env, .env.local等）
            if not matched and file_name.startswith('.env'):
                category_counts['infrastructure'] += 1
                matched = True

            if not matched:
                category_counts['unknown'] += 1

        # 计算百分比（忽略unknown类别）
        total_known = sum(count for cat, count in category_counts.items() if cat != 'unknown')
        if total_known == 0:
            return {
                'backend': 0,
                'frontend': 0,
                'infrastructure': 0,
                'documentation': 0,
            }

        # 计算百分比并转换为整数
        distribution = {}
        for category in ['backend', 'frontend', 'infrastructure', 'documentation']:
            percentage = (category_counts[category] / total_known) * 100
            distribution[category] = int(round(percentage))

        # 确保总和为100（处理四舍五入误差）
        total = sum(distribution.values())
        if total != 100:
            # 将误差加到最大的类别中
            diff = 100 - total
            if diff != 0:
                max_category = max(distribution.items(), key=lambda x: x[1])[0]
                distribution[max_category] += diff

        return distribution

    def _earliest_issue_time(self, issues: List[Dict[str, Any]]) -> Optional[datetime]:
        timestamps = [_parse_timestamp(issue.get('created_at')) for issue in issues if issue.get('created_at')]
        timestamps = [ts for ts in timestamps if ts]
        return min(timestamps) if timestamps else None

    def _calculate_days_since_first_issue(self, earliest: Optional[datetime]) -> int:
        if not earliest:
            return 0
        return max(0, (_utc_now() - earliest).days)

    def _calculate_delay_rate(self, delayed: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round((delayed / total) * 100, 1)

    def _average(self, values: List[int]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 1)
