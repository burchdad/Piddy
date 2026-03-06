import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Decisions() {
  const [decisions, setDecisions] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [filterAgent, setFilterAgent] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/decisions');
        const data = await response.json();
        setDecisions(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch decisions:', error);
        setLoading(false);
      }
    };

    fetchDecisions();
    const interval = setInterval(fetchDecisions, 15000);
    return () => clearInterval(interval);
  }, []);

  const filteredDecisions = decisions?.filter(d => 
    filterAgent === 'all' || d.agent_id === filterAgent
  ) || [];

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return '#51cf66';
    if (confidence >= 0.75) return '#4299e1';
    if (confidence >= 0.6) return '#ffd93d';
    return '#ff6b6b';
  };

  const getValidationStatus = (validation) => {
    if (validation.passed) return '✅ Passed';
    return '❌ Failed';
  };

  return (
    <div className="page decisions">
      <div className="header-section">
        <h2>🧠 AI Decision Viewer</h2>
        <p className="subtitle">Inspect LLM reasoning, confidence, and validation for autonomous decisions</p>
      </div>

      {loading ? (
        <div className="loading">Loading decisions...</div>
      ) : (
        <>
          {/* Filter */}
          <div className="filter-group" style={{ marginBottom: '2rem' }}>
            <label style={{ marginRight: '1rem', color: 'var(--text-secondary)' }}>Filter by Agent:</label>
            <select 
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Agents</option>
              {[...new Set(decisions?.map(d => d.agent_id) || [])].map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </select>
          </div>

          {/* Decisions Grid */}
          <div className="decisions-grid">
            {filteredDecisions.map((decision, index) => (
              <div 
                key={index} 
                className="decision-card"
                onClick={() => setSelectedDecision(selectedDecision?.id === decision.id ? null : decision)}
              >
                {/* Header */}
                <div className="decision-header">
                  <div>
                    <div className="decision-task">{decision.task}</div>
                    <div className="decision-agent">{decision.agent_id}</div>
                  </div>
                  <div className="decision-meta">
                    <span className="decision-timestamp">{new Date(decision.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="decision-stats">
                  <div className="decision-stat">
                    <span className="stat-label">Confidence</span>
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill"
                        style={{
                          width: `${decision.confidence * 100}%`,
                          backgroundColor: getConfidenceColor(decision.confidence)
                        }}
                      />
                    </div>
                    <span className="stat-value">{(decision.confidence * 100).toFixed(1)}%</span>
                  </div>

                  <div className="decision-stat">
                    <span className="stat-label">Action</span>
                    <span className="stat-value" style={{ color: 'var(--primary-color)' }}>
                      {decision.action}
                    </span>
                  </div>

                  <div className="decision-stat">
                    <span className="stat-label">Result</span>
                    <span className={`stat-value ${decision.validation.passed ? 'success' : 'error'}`}>
                      {getValidationStatus(decision.validation)}
                    </span>
                  </div>
                </div>

                {/* Expandable Details */}
                {selectedDecision?.id === decision.id && (
                  <div className="decision-details">
                    {/* Context */}
                    <div className="detail-section">
                      <h4>📋 Context</h4>
                      <div className="context-box">
                        <p><strong>Goal:</strong> {decision.context.goal}</p>
                        <p><strong>Constraints:</strong> {decision.context.constraints}</p>
                        <p><strong>Available Options:</strong> {decision.context.available_options}</p>
                      </div>
                    </div>

                    {/* LLM Reasoning */}
                    <div className="detail-section">
                      <h4>🧠 LLM Reasoning</h4>
                      <div className="reasoning-chain">
                        {decision.reasoning_chain.map((step, idx) => (
                          <div key={idx} className="reasoning-step">
                            <div className="step-number">{idx + 1}</div>
                            <div className="step-content">
                              <strong>{step.stage}</strong>
                              <p>{step.thought}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Decision Factors */}
                    <div className="detail-section">
                      <h4>⚖️ Decision Factors</h4>
                      <div className="factors-grid">
                        {decision.factors.map((factor, idx) => (
                          <div key={idx} className="factor-item">
                            <div className="factor-name">{factor.name}</div>
                            <div className="factor-weight">Weight: {(factor.weight * 100).toFixed(0)}%</div>
                            <div className="factor-contribution">{factor.contribution}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Validation Results */}
                    <div className="detail-section">
                      <h4>✓ Validation Results</h4>
                      <div className={`validation-box ${decision.validation.passed ? 'passed' : 'failed'}`}>
                        <div className="validation-status">
                          {decision.validation.passed ? '✅ VALIDATION PASSED' : '❌ VALIDATION FAILED'}
                        </div>
                        <div className="validation-checks">
                          {decision.validation.checks.map((check, idx) => (
                            <div key={idx} className={`check-item ${check.passed ? 'passed' : 'failed'}`}>
                              <span className="check-icon">{check.passed ? '✓' : '✗'}</span>
                              <span className="check-name">{check.name}</span>
                              <span className="check-detail">{check.detail}</span>
                            </div>
                          ))}
                        </div>
                        <div className="validation-score">
                          <strong>Validation Score: {(decision.validation.score * 100).toFixed(1)}%</strong>
                        </div>
                      </div>
                    </div>

                    {/* Action Taken */}
                    <div className="detail-section">
                      <h4>🎯 Action Taken</h4>
                      <div className="action-box">
                        <p><strong>Type:</strong> {decision.action}</p>
                        <p><strong>Parameters:</strong></p>
                        <pre>{JSON.stringify(decision.parameters, null, 2)}</pre>
                      </div>
                    </div>

                    {/* Outcome (if available) */}
                    {decision.outcome && (
                      <div className="detail-section">
                        <h4>📊 Outcome</h4>
                        <div className={`outcome-box ${decision.outcome.success ? 'success' : 'failure'}`}>
                          <p><strong>Success:</strong> {decision.outcome.success ? 'Yes' : 'No'}</p>
                          <p><strong>Result:</strong> {decision.outcome.result_description}</p>
                          <p><strong>Learning:</strong> {decision.outcome.learning_point}</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredDecisions.length === 0 && (
            <div className="empty-state">
              <p>No decisions found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Decisions;
