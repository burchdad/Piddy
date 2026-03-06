import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Phases() {
  const [phases, setPhases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPhases = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/phases');
        const data = await response.json();
        setPhases(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch phases:', error);
        setLoading(false);
      }
    };

    fetchPhases();
    const interval = setInterval(fetchPhases, 20000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    const icons = {
      pending: '⏳',
      in_progress: '⚙️',
      completed: '✅',
      failed: '❌'
    };
    return icons[status] || '❓';
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#868e96',
      in_progress: '#4dabf7',
      completed: '#51cf66',
      failed: '#ff6b6b'
    };
    return colors[status] || '#333';
  };

  return (
    <div className="page phases">
      <div className="header-section">
        <h2>⚙️ Phase Status</h2>
        <p className="subtitle">Deployment and feature phase tracking</p>
      </div>

      {loading ? (
        <div className="loading">Loading phases...</div>
      ) : (
        <div className="phases-list">
          {phases.map((phase) => (
            <div key={phase.phase_id} className={`phase-card ${phase.status}`}>
              <div className="phase-header">
                <div className="phase-title">
                  <span className="status-icon" style={{ color: getStatusColor(phase.status) }}>
                    {getStatusIcon(phase.status)}
                  </span>
                  <div className="phase-info">
                    <h3>{phase.phase_name}</h3>
                    <span className="phase-id">{phase.phase_id}</span>
                  </div>
                </div>
                <div className="phase-status">
                  <span style={{ color: getStatusColor(phase.status) }}>
                    {phase.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="phase-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${phase.progress_percent}%`,
                      backgroundColor: getStatusColor(phase.status)
                    }}
                  ></div>
                </div>
                <span className="progress-text">{phase.progress_percent}% Complete</span>
              </div>

              {phase.details && (
                <div className="phase-details">
                  <pre>{JSON.stringify(phase.details, null, 2)}</pre>
                </div>
              )}

              <div className="phase-timestamp">
                Last updated: {new Date(phase.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Phases;
