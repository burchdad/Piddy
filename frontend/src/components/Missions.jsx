import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Missions() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const data = await fetchApi('/api/missions');
        setMissions(Array.isArray(data) ? data : (data.missions || []));
      } catch (err) {
        console.error('Failed to fetch missions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMissions();
    const interval = setInterval(fetchMissions, 15000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return '#51cf66';
      case 'in_progress': return '#4299e1';
      case 'pending': return '#cbd5e1';
      case 'failed': return '#ff6b6b';
      default: return '#ffd93d';
    }
  };

  if (loading) return <div className="page">Loading missions...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🎯 Active Missions</h1>
      </div>

      <div className="missions-list">
        {Array.isArray(missions) && missions.map((mission) => (
          <div key={mission.id} className="mission-card" onClick={() => setExpandedId(expandedId === mission.id ? null : mission.id)}>
            <div className="mission-header">
              <div className="mission-info">
                <h3>{mission.name}</h3>
                <p>{mission.description}</p>
              </div>
              <div className={`mission-status ${mission.status}`} style={{backgroundColor: getStatusColor(mission.status)}}>
                {mission.status.toUpperCase()}
              </div>
            </div>
            
            <div className="mission-metrics">
              <div className="metric">
                <span className="label">Progress:</span>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: `${mission.progress_percent || 0}%`}}></div>
                </div>
                <span className="value">{mission.progress_percent || 0}%</span>
              </div>
              <div className="metric">
                <span className="label">Quality Score:</span>
                <span className="value">{(mission.quality_score ?? 0).toFixed(2)}</span>
              </div>
              <div className="metric">
                <span className="label">Efficiency Score:</span>
                <span className="value">{(mission.efficiency_score ?? 0).toFixed(2)}</span>
              </div>
            </div>

            {expandedId === mission.id && (
              <div className="mission-expanded">
                <div className="mission-details">
                  <div className="detail-section">
                    <h4>Goal</h4>
                    <p>{mission.goal}</p>
                  </div>
                  <div className="detail-section">
                    <h4>Agents Involved</h4>
                    <div className="agents-list">
                      {mission.agents_involved && mission.agents_involved.map((agent, idx) => (
                        <span key={idx} className="agent-tag">{agent.name || agent}</span>
                      ))}
                    </div>
                  </div>
                  <div className="detail-section">
                    <h4>Success Criteria</h4>
                    <ul className="criteria-list">
                      {mission.success_criteria && mission.success_criteria.map((criterion, idx) => (
                        <li key={idx}>{criterion}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Missions;
