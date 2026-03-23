import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

const ROLE_ICONS = {
  security_specialist: '🛡️',
  architect: '🏗️',
  backend_developer: '⚙️',
  code_reviewer: '🔍',
  devops_engineer: '🚀',
  data_engineer: '📊',
  coordinator: '🎯',
  performance_analyst: '⚡',
  tech_debt_hunter: '🧹',
  api_compatibility: '🔗',
  database_migration: '🗄️',
  architecture_reviewer: '📐',
  cost_optimizer: '💰',
  frontend_developer: '🎨',
  documentation: '📝',
  security_tooling: '🔧',
  security_monitoring: '📡',
  load_testing: '🏋️',
  data_security: '🔐',
  knowledge_monitor: '📚',
  task_automation: '🤖',
};

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await fetchApi('/api/agents');
        const agentsArray = Array.isArray(data) ? data : (data.agents || []);
        setAgents(agentsArray);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
        setAgents([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="page"><h2>Loading agents...</h2></div>;
  }

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="page">
      <h2>Agents</h2>
      <p className="agents-summary">
        {agents.length} agents registered &middot;{' '}
        {agents.filter(a => a.status === 'online').length} online
      </p>
      <div className="agents-grid">
        {!Array.isArray(agents) || agents.length === 0 ? (
          <p>No agents found</p>
        ) : (
          agents.map(agent => {
            const icon = ROLE_ICONS[agent.role] || '🤖';
            const reputation = ((agent.reputation ?? 0) * 100).toFixed(0);
            const isExpanded = expandedId === agent.id;

            return (
              <div
                key={agent.id}
                className={`agent-card ${isExpanded ? 'expanded' : ''}`}
                onClick={() => toggleExpand(agent.id)}
              >
                <div className="agent-header">
                  <div className="agent-name-row">
                    <span className="agent-icon">{icon}</span>
                    <h3>{agent.name}</h3>
                  </div>
                  <span className={`agent-status ${agent.status}`}>● {agent.status}</span>
                </div>

                <div className="agent-role-label">{(agent.role || '').replace(/_/g, ' ')}</div>

                <div className="agent-stats">
                  <div className="agent-stat">
                    <span className="agent-stat-label">Reputation</span>
                    <span className="agent-stat-value">{reputation}%</span>
                  </div>
                  <div className="agent-stat">
                    <span className="agent-stat-label">Completed</span>
                    <span className="agent-stat-value">{agent.completed_tasks ?? 0}</span>
                  </div>
                  <div className="agent-stat">
                    <span className="agent-stat-label">Failed</span>
                    <span className="agent-stat-value">{agent.failed_tasks ?? 0}</span>
                  </div>
                  <div className="agent-stat">
                    <span className="agent-stat-label">Task</span>
                    <span className="agent-stat-value">{agent.current_task_id ? 'Active' : 'Idle'}</span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="agent-expanded">
                    {agent.capabilities && agent.capabilities.length > 0 && (
                      <div className="agent-capabilities">
                        <strong>Capabilities</strong>
                        <div className="capability-tags">
                          {agent.capabilities.map((cap, i) => (
                            <span key={i} className="capability-tag">{cap.replace(/_/g, ' ')}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="agent-meta">
                      <div><strong>ID:</strong> {agent.id}</div>
                      {agent.last_activity && (
                        <div><strong>Last Active:</strong> {new Date(agent.last_activity).toLocaleString()}</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default Agents;
