"""
AI service for risk analysis using DeepSeek API.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered risk analysis."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.deepseek_api_key
        self.api_base = settings.deepseek_api_base
        self.model = settings.deepseek_model

        if not self.api_key:
            logger.warning("DeepSeek API key not configured. AI analysis will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
            )

    def is_available(self) -> bool:
        """Check if AI service is available (API key configured)."""
        return self.client is not None

    async def analyze_project_health(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project health data and generate risk assessment using AI.

        Args:
            project_data: Project health data from dashboard

        Returns:
            AI-generated risk analysis with overall risk level, risks, and mitigations
        """
        if not self.is_available():
            logger.warning("AI service not available, returning fallback analysis")
            return self._generate_fallback_analysis(project_data)

        try:
            # Prepare project data for AI analysis
            analysis_data = self._prepare_analysis_data(project_data)

            # Generate AI prompt
            prompt = self._create_risk_analysis_prompt(analysis_data)

            # Call AI API
            response = self._call_ai_api(prompt)

            # Parse AI response
            risk_analysis = self._parse_ai_response(response, analysis_data)

            logger.info("AI risk analysis generated successfully")
            return risk_analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fall back to rule-based analysis
            return self._generate_fallback_analysis(project_data)

    def _prepare_analysis_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare project data for AI analysis."""
        project_health = project_data.get('projectHealth', {})
        code_health = project_data.get('codeHealth', {})
        team_work = project_data.get('teamWork', {})

        # Extract key metrics
        return {
            'project_health': {
                'total_issues': project_health.get('totalIssues', 0),
                'completed_issues': project_health.get('completedIssues', 0),
                'pending_issues': project_health.get('pendingIssues', 0),
                'delayed_issues': project_health.get('delayedIssues', 0),
                'total_prs': project_health.get('totalPRs', 0),
                'merged_prs': project_health.get('mergedPRs', 0),
                'open_prs': project_health.get('openPRs', 0),
                'in_review_prs': project_health.get('inReviewPRs', 0),
                'average_comment_frequency': project_health.get('averageCommentFrequency', 0.0),
                'quality_score': project_health.get('qualityScore', 0.0),
                'saturation_score': project_health.get('saturationScore', 0.0),
                'overall_delay_rate': project_health.get('overallDelayRate', 0.0),
                'days_since_first_issue': project_health.get('daysSinceFirstIssue', 0),
            },
            'code_health': {
                'unmerged_prs': code_health.get('unmergedPRs', 0),
                'commit_frequency': code_health.get('commitFrequency', 0),
                'single_contributor_percentage': code_health.get('singleContributorPercentage', 0.0),
                'code_change_distribution': code_health.get('codeChangeDistribution', {}),
            },
            'team_work': {
                'member_count': len(team_work.get('members', [])),
                'team_average_delay_rate': team_work.get('teamAverageDelayRate', 0.0),
                'team_quality_score': team_work.get('teamQualityScore', 0.0),
                'team_saturation_score': team_work.get('teamSaturationScore', 0.0),
            }
        }

    def _create_risk_analysis_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Create prompt for AI risk analysis."""
        project_health = analysis_data['project_health']
        code_health = analysis_data['code_health']
        team_work = analysis_data['team_work']

        prompt = f"""You are a senior software engineering manager analyzing repository health metrics.
        Please provide a comprehensive risk analysis based on the following project data:

        ## PROJECT HEALTH METRICS:
        - Total Issues: {project_health['total_issues']}
        - Completed Issues: {project_health['completed_issues']}
        - Pending Issues: {project_health['pending_issues']}
        - Delayed Issues: {project_health['delayed_issues']}
        - Overall Delay Rate: {project_health['overall_delay_rate']:.1f}%
        - Quality Score: {project_health['quality_score']:.1f}/100
        - Saturation Score: {project_health['saturation_score']:.1f}/100
        - Days Since First Issue: {project_health['days_since_first_issue']}

        ## CODE HEALTH METRICS:
        - Total PRs: {project_health['total_prs']}
        - Merged PRs: {project_health['merged_prs']}
        - Open PRs: {project_health['open_prs']}
        - PRs in Review: {project_health['in_review_prs']}
        - Average Comments per PR: {project_health['average_comment_frequency']:.1f}
        - Unmerged PRs: {code_health['unmerged_prs']}
        - Commit Frequency: {code_health['commit_frequency']} commits/week
        - Single Contributor %: {code_health['single_contributor_percentage']:.1f}%

        ## TEAM METRICS:
        - Team Members: {team_work['member_count']}
        - Team Average Delay Rate: {team_work['team_average_delay_rate']:.1f}%
        - Team Quality Score: {team_work['team_quality_score']:.1f}/100
        - Team Saturation Score: {team_work['team_saturation_score']:.1f}/100

        Please analyze this data and provide:
        1. An overall risk level (low, medium, high, critical)
        2. 1-4 specific risks with probability (low, medium, high) and impact (low, medium, high)
        3. 2-4 practical mitigation strategies

        Format your response as JSON with this exact structure:
        {{
            "overall_risk_level": "low|medium|high|critical",
            "risks": [
                {{
                    "title": "Risk title",
                    "probability": "low|medium|high",
                    "impact": "low|medium|high",
                    "description": "Detailed risk description"
                }}
            ],
            "mitigations": [
                {{
                    "action": "Specific mitigation action"
                }}
            ],
            "analysis_summary": "Brief summary of the analysis"
        }}

        Focus on software engineering best practices, team productivity, code quality, and project management.
        Be realistic and actionable. If all metrics look healthy, still provide a baseline analysis with low risks.
        """

        return prompt

    def _call_ai_api(self, prompt: str) -> str:
        """Call the AI API with the given prompt."""
        if not self.client:
            raise ValueError("AI client not initialized")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a software engineering expert specializing in project health and risk analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            raise

    def _parse_ai_response(self, ai_response: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured risk analysis."""
        try:
            result = json.loads(ai_response)

            # Validate structure
            required_fields = ['overall_risk_level', 'risks', 'mitigations']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure risks and mitigations are lists
            if not isinstance(result['risks'], list):
                result['risks'] = []
            if not isinstance(result['mitigations'], list):
                result['mitigations'] = []

            # Validate each risk
            validated_risks = []
            for risk in result['risks'][:4]:  # Limit to 4 risks max
                if isinstance(risk, dict):
                    validated_risk = {
                        'title': risk.get('title', 'Unnamed Risk'),
                        'probability': risk.get('probability', 'medium').lower(),
                        'impact': risk.get('impact', 'medium').lower(),
                        'description': risk.get('description', 'No description provided')
                    }
                    # Ensure valid probability and impact values
                    if validated_risk['probability'] not in ['low', 'medium', 'high']:
                        validated_risk['probability'] = 'medium'
                    if validated_risk['impact'] not in ['low', 'medium', 'high']:
                        validated_risk['impact'] = 'medium'
                    validated_risks.append(validated_risk)

            result['risks'] = validated_risks

            # Validate mitigations
            validated_mitigations = []
            for mitigation in result['mitigations'][:4]:  # Limit to 4 mitigations max
                if isinstance(mitigation, dict):
                    validated_mitigations.append({
                        'action': mitigation.get('action', 'Unspecified mitigation')
                    })

            result['mitigations'] = validated_mitigations

            # Add metadata
            result['analysis_method'] = 'ai'
            result['analysis_summary'] = result.get('analysis_summary', 'AI-generated risk analysis')

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from AI: {e}")

    def _generate_fallback_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback rule-based analysis when AI is unavailable."""
        logger.info("Generating fallback rule-based analysis")

        project_health = project_data.get('projectHealth', {})
        overall_delay_rate = project_health.get('overallDelayRate', 0.0)
        quality_score = project_health.get('qualityScore', 0.0)

        # Rule-based risk level
        if overall_delay_rate > 20 or quality_score < 50:
            overall_risk_level = 'high'
        elif overall_delay_rate > 10 or quality_score < 70:
            overall_risk_level = 'medium'
        else:
            overall_risk_level = 'low'

        # Generate risks based on data
        risks = []

        if overall_delay_rate > 15:
            risks.append({
                'title': 'High Task Delay Rate',
                'probability': 'high' if overall_delay_rate > 25 else 'medium',
                'impact': 'high' if overall_delay_rate > 30 else 'medium',
                'description': f'Project has {overall_delay_rate:.1f}% delayed issues, which may impact delivery timelines.'
            })

        if quality_score < 70:
            risks.append({
                'title': 'Code Quality Concerns',
                'probability': 'high' if quality_score < 50 else 'medium',
                'impact': 'high' if quality_score < 60 else 'medium',
                'description': f'Code quality score is {quality_score:.1f}/100, indicating potential maintainability issues.'
            })

        # If no specific risks detected but data exists, provide general assessment
        if not risks and (project_health.get('totalIssues', 0) > 0 or project_health.get('totalPRs', 0) > 0):
            risks.append({
                'title': 'Project Monitoring',
                'probability': 'low',
                'impact': 'low',
                'description': 'Project shows baseline activity. Continue monitoring for emerging risks.'
            })

        # Default mitigation strategies
        mitigations = [
            {'action': 'Regularly review and prioritize backlog items'},
            {'action': 'Improve code review practices and documentation'},
            {'action': 'Monitor team workload and adjust assignments as needed'},
        ]

        return {
            'overall_risk_level': overall_risk_level,
            'risks': risks,
            'mitigations': mitigations,
            'analysis_method': 'rule_based',
            'analysis_summary': 'Rule-based risk analysis (AI service unavailable)'
        }


# Global AI service instance
_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get or create the global AI service instance."""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance