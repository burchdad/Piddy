import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Decisions() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const data = await fetchApi('/api/decisions');
        setDecisions(data);
      } catch (err) {
        console.error('Failed to fetch decisions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDecisions();
    const interval = setInterval(fetchDecisions, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="page">Loading decisions...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🧠 AI Decisions</h1>
      </div>

      <div className="decisions-list">
        {decisions.map((decision) => (
          <div key={decision.id} className="decision-card" onClick={() => setExpandedId(expandedId === decision.id ? null : decision.id)}>
            <div className="decision-header">
              <div className="decision-task">{decision.task}</div>
              <div className="decision-confidence">
                <span className="confidence-value">{(decision.confidence * 100).toFixed(0)}%</span>
                <div className="confidence-bar">
                  <div className="confidence-fill" style={{width: `${decision.confidence * 100}%`}}></div>
                </div>
              </div>
            </div>
            <div className="decision-action">{decision.action}</div>
            {expandedId === decision.id && (
              <div className="decision-expanded">
                <div className="reasoning-chain">
                  <h4>Reasoning Chain:</h4>
                  {decision.reasoning_chain.map((step, idx) => (
                    <div key={idx} className="reasoning-step">
                      <span className="step-num">{idx + 1}</span>
                      <span className="step-text">{step.thought}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Decisions;
