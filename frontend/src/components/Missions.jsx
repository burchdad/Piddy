import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Missions() {
  const [missions, setMissions] = useState(null);
  const [selectedMission, setSelectedMission] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/missions');
        const data = await response.json();
        setMissions(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch missions:', error);
        setLoading(false);
      }
    };

    fetchMissions();
    const interval = setInterval(fetchMissions, 20000);
    return () => clearInterval(interval);
  }, []);

  const filteredMissions = missions?.filter(m => 
    filterStatus === 'all' || m.status === filterStatus
  ) || [];

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return '#51cf66';
      case 'in_progress': return '#4299e1';
      case 'pending': return '#94a3b8';
      case 'failed': return '#ff6b6b';
      default: return '#6366f1';
    }
  };

  const getStageIcon = (stage) => {
    switch(stage) {
      case 'Goal': return '🎯';
      case 'Plan': return '📋';
      case 'Execute': return '⚙️';
      case 'Validate': return '✓';
      case 'PR': return '🔄';
      default: return '→';
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString();
  };

  const calculateDuration = (start, end) => {
    if (!start || !end) return 'N/A';
    const diff = new Date(end) - new Date(start);
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
  };

  return (
    <div className="page missions">
      <div className="header-section">
        <h2>🚀 Mission Timeline</h2>
        <p className="subtitle">Visualize AI mission progression from goal to deployment</p>
      </div>

      {loading ? (
        <div className="loading">Loading missions...</div>
      ) : (
        <>
          {/* Filter */}
          <div className="filter-group" style={{ marginBottom: '2rem' }}>
            <label style={{ marginRight: '1rem', color: 'var(--text-secondary)' }}>Filter by Status:</label>
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          {/* Missions */}
          <div className="missions-grid">
            {filteredMissions.map((mission, index) => (
              <div 
                key={index}
                className="mission-card"
                onClick={() => setSelectedMission(selectedMission?.id === mission.id ? null : mission)}
              >
                {/* Mission Header */}
                <div className="mission-header">
                  <div>
                    <div className="mission-name">{mission.name}</div>
                    <div className="mission-description">{mission.description}</div>
                  </div>
                  <div 
                    className="mission-status"
                    style={{
                      backgroundColor: getStatusColor(mission.status),
                      opacity: 0.8
                    }}
                  >
                    {mission.status.replace('_', ' ').toUpperCase()}
                  </div>
                </div>

                {/* Timeline Stages */}
                <div className="timeline-container">
                  {mission.stages.map((stage, stageIdx) => (
                    <div key={stageIdx} className="timeline-stage-group">
                      <div className="timeline-stage">
                        <div className={`stage-indicator ${stage.status}`}>
                          {getStageIcon(stage.name)}
                        </div>
                        <div className="stage-info">
                          <div className="stage-name">{stage.name}</div>
                          <div className="stage-status">{stage.status}</div>
                          {stage.start_time && (
                            <div className="stage-time">
                              Start: {formatTime(stage.start_time)}
                            </div>
                          )}
                          {stage.end_time && (
                            <div className="stage-duration">
                              Duration: {calculateDuration(stage.start_time, stage.end_time)}
                            </div>
                          )}
                        </div>
                      </div>
                      {stageIdx < mission.stages.length - 1 && (
                        <div className="timeline-connector" />
                      )}
                    </div>
                  ))}
                </div>

                {/* Quick Stats */}
                <div className="mission-stats">
                  <div className="mission-stat">
                    <span className="stat-label">Priority</span>
                    <span className="stat-value">{mission.priority}</span>
                  </div>
                  <div className="mission-stat">
                    <span className="stat-label">Agents</span>
                    <span className="stat-value">{mission.agents_involved.length}</span>
                  </div>
                  <div className="mission-stat">
                    <span className="stat-label">Progress</span>
                    <span className="stat-value">{mission.progress_percent}%</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${mission.progress_percent}%` }}
                  />
                </div>

                {/* Expandable Details */}
                {selectedMission?.id === mission.id && (
                  <div className="mission-details">
                    {/* Goal Details */}
                    <div className="detail-section">
                      <h4>🎯 Goal</h4>
                      <div className="goal-box">
                        <p>{mission.goal}</p>
                        <div className="goal-metrics">
                          <strong>Success Criteria:</strong>
                          <ul>
                            {mission.success_criteria.map((criterion, idx) => (
                              <li key={idx}>{criterion}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Plan Details */}
                    <div className="detail-section">
                      <h4>📋 Plan</h4>
                      <div className="plan-box">
                        <p><strong>Strategy:</strong> {mission.plan.strategy}</p>
                        <p><strong>Resource Allocation:</strong></p>
                        <ul>
                          {Object.entries(mission.plan.resources).map(([key, value]) => (
                            <li key={key}>{key}: {value}</li>
                          ))}
                        </ul>
                        <p><strong>Timeline:</strong> ~{mission.plan.estimated_duration}</p>
                      </div>
                    </div>

                    {/* Agents Involved */}
                    <div className="detail-section">
                      <h4>🤖 Agents Involved</h4>
                      <div className="agents-list">
                        {mission.agents_involved.map((agent, idx) => (
                          <div key={idx} className="agent-involvement">
                            <span className="agent-id">{agent.agent_id}</span>
                            <span className="agent-role">{agent.role}</span>
                            <span className="agent-status" style={{
                              color: agent.status === 'active' ? '#51cf66' : '#94a3b8'
                            }}>
                              {agent.status.toUpperCase()}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Stage Details */}
                    <div className="detail-section">
                      <h4>📍 Stage Details</h4>
                      {mission.stages.map((stage, idx) => (
                        <div key={idx} className="stage-detail">
                          <h5>{stage.name}</h5>
                          <p><strong>Status:</strong> {stage.status}</p>
                          <p><strong>Description:</strong> {stage.description}</p>
                          {stage.milestones && stage.milestones.length > 0 && (
                            <div>
                              <strong>Milestones Completed:</strong> {stage.milestones.length}
                              <ul>
                                {stage.milestones.map((milestone, mIdx) => (
                                  <li key={mIdx}>{milestone}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {stage.issues && stage.issues.length > 0 && (
                            <div style={{ marginTop: '0.5rem', color: '#ff6b6b' }}>
                              <strong>Issues:</strong>
                              <ul>
                                {stage.issues.map((issue, iIdx) => (
                                  <li key={iIdx}>{issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Overall Performance */}
                    <div className="detail-section">
                      <h4>📊 Performance</h4>
                      <div className="performance-box">
                        <p><strong>Efficiency Score:</strong> {(mission.efficiency_score * 100).toFixed(1)}%</p>
                        <p><strong>Quality Score:</strong> {(mission.quality_score * 100).toFixed(1)}%</p>
                        <p><strong>Risk Level:</strong> {mission.risk_level.toUpperCase()}</p>
                        {mission.notes && (
                          <p><strong>Notes:</strong> {mission.notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredMissions.length === 0 && (
            <div className="empty-state">
              <p>No missions found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Missions;
