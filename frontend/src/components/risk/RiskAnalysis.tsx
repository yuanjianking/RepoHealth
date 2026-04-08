import React from 'react';
import './RiskAnalysis.css';
import type { RiskAnalysis } from '../../types';

interface RiskAnalysisProps {
  riskData: RiskAnalysis;
}

const RiskAnalysisComponent: React.FC<RiskAnalysisProps> = ({ riskData }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '#d32f2f';
      case 'high':
        return '#f44336';
      case 'medium':
        return '#ff9800';
      case 'low':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const getSeverityText = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '严重';
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return severity;
    }
  };

  const getProbabilityText = (probability: string) => {
    switch (probability.toLowerCase()) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return probability;
    }
  };

  const getImpactText = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return impact;
    }
  };

  const getRecommendation = (riskProbability: string, riskImpact: string) => {
    const prob = riskProbability.toLowerCase();
    const impact = riskImpact.toLowerCase();

    if (prob === 'high' && impact === 'high') {
      return '需要立即采取行动';
    } else if (prob === 'high' || impact === 'high') {
      return '密切监控并制定缓解计划';
    } else if (prob === 'medium' && impact === 'medium') {
      return '制定预防措施，定期检查';
    } else {
      return '低优先级 - 定期监控';
    }
  };

  // 如果没有风险，显示健康状态
  const isHealthy = riskData.risks.length === 0;
  const overallRiskColor = getSeverityColor(riskData.overall_risk_level);

  return (
    <div className="risk-analysis">
      <div className="card-header">
        <h2 className="card-title">风险分析与预警</h2>
        <div className="card-subtitle">基于项目数据的 AI 风险评估</div>
        <div className="overall-risk" style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="overall-risk-label" style={{ fontSize: '14px', color: '#666' }}>整体风险等级: </span>
          <span
            className="overall-risk-badge"
            style={{
              backgroundColor: overallRiskColor,
              color: 'white',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '13px',
              fontWeight: '600'
            }}
          >
            {getSeverityText(riskData.overall_risk_level)}
          </span>
          <span className="generated-time" style={{ fontSize: '12px', color: '#888' }}>
            （生成时间: {riskData.generated_at || '未知'}）
          </span>
        </div>
      </div>

      <div className="risk-content">
        {isHealthy ? (
          <div className="healthy-state" style={{
            textAlign: 'center',
            padding: '40px 20px',
            background: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <div className="healthy-icon" style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
            <h3 className="healthy-title" style={{ fontSize: '20px', fontWeight: '600', color: '#28a745', marginBottom: '8px' }}>
              项目状态健康
            </h3>
            <p className="healthy-description" style={{ fontSize: '14px', color: '#666', lineHeight: '1.5', maxWidth: '500px', margin: '0 auto' }}>
              目前未检测到显著风险，项目运行状况良好，继续保持当前工作状态。
            </p>
          </div>
        ) : (
          <>
            <div className="risk-list-container">
              <h3 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#1a1a1a', marginBottom: '16px' }}>
                已识别风险 ({riskData.risks.length})
              </h3>
              <div className="risk-list">
                {riskData.risks.map((risk, index) => (
                  <div key={index} className="risk-item">
                    <div className="risk-header">
                      <div className="risk-title">{risk.title}</div>
                      <div className="risk-severity" style={{ display: 'flex', gap: '8px' }}>
                        <span
                          className="severity-badge"
                          style={{ backgroundColor: getSeverityColor(risk.probability) }}
                        >
                          可能性: {getProbabilityText(risk.probability)}
                        </span>
                        <span
                          className="severity-badge"
                          style={{ backgroundColor: getSeverityColor(risk.impact) }}
                        >
                          影响: {getImpactText(risk.impact)}
                        </span>
                      </div>
                    </div>

                    <div className="risk-description" style={{
                      fontSize: '14px',
                      color: '#555',
                      lineHeight: '1.5',
                      margin: '12px 0',
                      padding: '8px 12px',
                      background: '#f8f9fa',
                      borderRadius: '4px'
                    }}>
                      {risk.description}
                    </div>

                    <div className="risk-recommendation">
                      <strong>建议:</strong> {getRecommendation(risk.probability, risk.impact)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {riskData.mitigations.length > 0 && (
              <div className="mitigation-container" style={{ marginTop: '24px' }}>
                <h3 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#1a1a1a', marginBottom: '16px' }}>
                  缓解措施建议
                </h3>
                <div className="mitigation-list" style={{
                  background: '#f8f9fa',
                  borderRadius: '6px',
                  padding: '16px',
                  border: '1px solid #e9ecef'
                }}>
                  {riskData.mitigations.map((mitigation, index) => (
                    <div key={index} className="mitigation-item" style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      marginBottom: '12px',
                      paddingBottom: '12px',
                      borderBottom: index < riskData.mitigations.length - 1 ? '1px solid #e9ecef' : 'none'
                    }}>
                      <span className="mitigation-number" style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#666',
                        minWidth: '24px'
                      }}>
                        {index + 1}.
                      </span>
                      <span className="mitigation-action" style={{
                        fontSize: '14px',
                        color: '#333',
                        lineHeight: '1.5',
                        flex: 1
                      }}>
                        {mitigation.action}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default RiskAnalysisComponent;