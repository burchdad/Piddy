import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await fetchApi('/api/agents');
        const agentsArray = Array.isArray(data) ? data : (data.agents || []);
        setAgents(agentsArray);
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  if (loading) {
    return <div className="page"><h2>Loading agents...</h2></div>;
  }

  return (
    <div className="page">
      <h2>Agents</h2>
      <div className="agents-grid">
        {agents.length === 0 ? (
          <p>No agents found</p>
        ) : (
          agents.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <h3>{agent.name}</h3>
                <span className={`agent-status ${agent.status}`}>● {agent.status}</span>
              </div>
              <div className="agent-details">
                <div><strong>Reputation:</strong> {(agent.reputation * 100).toFixed(0)}%</div>
                <div><strong>ID:</strong> {agent.id}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Agents;
