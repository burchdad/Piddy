import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Phases() {
  const [phases, setPhases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPhases = async () => {
      try {
        const data = await fetchApi('/api/phases');
        setPhases(data);
      } catch (err) {
        console.error('Failed to fetch phases:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPhases();
    const interval = setInterval(fetchPhases, 10000);
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

  if (loading) return <div className="page">Loading phases...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🚀 Deployment Phases</h1>
      </div>

      <div className="phases-timeline">
        {phases.map((phase, idx) => (
          <div key={phase.phase_id} className="phase-item">
            <div className="phase-connector" style={{backgroundColor: getStatusColor(phase.status)}}></div>
            <div className="phase-content">
              <div className="phase-header">
                <h3>{phase.phase_name}</h3>
                <span className="phase-status" style={{backgroundColor: getStatusColor(phase.status)}}>
                  {phase.status.toUpperCase()}
                </span>
              </div>
              <div className="phase-progress">
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: `${phase.progress_percent}%`}}></div>
                </div>
                <span className="progress-text">{phase.progress_percent}%</span>
              </div>
              <div className="phase-timestamp">{new Date(phase.timestamp).toLocaleString()}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Phases;
