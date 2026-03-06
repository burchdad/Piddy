import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/agents');
        const data = await response.json();
        setAgents(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
        setLoading(false);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page agents">
      <div className="header-section">
        <h2>🤖 Agent Status</h2>
        <p className="subtitle">Real-time autonomous agent monitoring</p>
      </div>

      {loading ? (
        <div className="loading">Loading agents...</div>
      ) : (
        <div className="agents-grid">
          {agents.map((agent) => (
            <div
              key={agent.agent_id}
              className={`agent-card ${agent.status === 'active' ? 'active' : 'inactive'}`}
              onClick={() => setSelectedAgent(selectedAgent?.agent_id === agent.agent_id ? null : agent)}
            >
              <div className="agent-header">
                <h3>{agent.agent_id}</h3>
                <span className={`status-badge ${agent.status}`}>●</span>
              </div>

              <div className="agent-role">Role: <strong>{agent.role}</strong></div>

              <div className="agent-metrics">
                <div className="metric-item">
                  <span className="label">Reputation:</span>
                  <span className="value">{agent.reputation_score.toFixed(2)}</span>
                  <div className="reputation-bar">
                    <div className="reputation-fill" style={{ width: `${(agent.reputation_score / 2) * 100}%` }}></div>
                  </div>
                </div>

                <div className="metric-item">
                  <span className="label">Decisions:</span>
                  <span className="value">{agent.total_decisions}</span>
                </div>

                <div className="metric-item">
                  <span className="label">Success Rate:</span>
                  <span className="value">{((agent.correct_decisions / agent.total_decisions) * 100).toFixed(1)}%</span>
                </div>

                <div className="metric-item">
                  <span className="label">Messages:</span>
                  <span className="value">{agent.messages_pending}</span>
                </div>
              </div>

              {selectedAgent?.agent_id === agent.agent_id && (
                <div className="agent-details">
                  <div className="detail-item">
                    <label>Status:</label>
                    <value>{agent.status}</value>
                  </div>
                  <div className="detail-item">
                    <label>Last Activity:</label>
                    <value>{new Date(agent.last_activity).toLocaleTimeString()}</value>
                  </div>
                  <div className="detail-item">
                    <label>Correct Decisions:</label>
                    <value>{agent.correct_decisions} / {agent.total_decisions}</value>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Agents;
