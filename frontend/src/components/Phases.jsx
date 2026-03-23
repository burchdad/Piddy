import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

const PHASE_DESCRIPTIONS = {
  'phase_1': 'Core agent framework and communication layer',
  'phase_2': 'Multi-agent coordination and task routing',
  'phase_3': 'Transparency dashboard and decision logging',
  'phase_4': 'Security audit and production readiness',
  'phase_5': 'Performance optimization and caching',
};

function Phases() {
  const [phases, setPhases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchPhases = async () => {
      try {
        const data = await fetchApi('/api/phases');
        setPhases(Array.isArray(data) ? data : (data.phases || []));
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

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'pending': return '⏳';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  if (loading) return <div className="page">Loading phases...</div>;

  const filtered = filter === 'all' ? phases : phases.filter(p => p.status === filter);
  const completed = phases.filter(p => p.status === 'completed').length;
  const inProgress = phases.filter(p => p.status === 'in_progress').length;
  const totalProgress = phases.length ? Math.round(phases.reduce((s, p) => s + (p.progress_percent || 0), 0) / phases.length) : 0;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🚀 Deployment Phases</h1>
      </div>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="metric-card"><div className="metric-value">{phases.length}</div><div className="metric-label">Total Phases</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: '#51cf66' }}>{completed}</div><div className="metric-label">Completed</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: '#4299e1' }}>{inProgress}</div><div className="metric-label">In Progress</div></div>
        <div className="metric-card"><div className="metric-value">{totalProgress}%</div><div className="metric-label">Overall</div></div>
      </div>

      {/* Filter buttons */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        {['all', 'completed', 'in_progress', 'pending', 'failed'].map(f => (
          <button key={f} className={filter === f ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
            onClick={() => setFilter(f)}>{f === 'all' ? 'All' : f.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</button>
        ))}
      </div>

      {/* Timeline */}
      <div className="phases-timeline">
        {Array.isArray(filtered) && filtered.map((phase, idx) => (
          <div key={phase.phase_id} className="phase-item">
            <div className="phase-connector" style={{backgroundColor: getStatusColor(phase.status)}}></div>
            <div className="phase-content">
              <div className="phase-header">
                <h3>{getStatusIcon(phase.status)} {phase.phase_name}</h3>
                <span className="phase-status" style={{backgroundColor: getStatusColor(phase.status)}}>
                  {phase.status.toUpperCase()}
                </span>
              </div>
              {PHASE_DESCRIPTIONS[phase.phase_id] && (
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.25rem 0 0.5rem' }}>
                  {PHASE_DESCRIPTIONS[phase.phase_id]}
                </p>
              )}
              <div className="phase-progress">
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: `${phase.progress_percent}%`}}></div>
                </div>
                <span className="progress-text">{phase.progress_percent}%</span>
              </div>
              <div className="phase-timestamp">{new Date(phase.timestamp).toLocaleString()}</div>
              {phase.details && Object.keys(phase.details).length > 0 && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {Object.entries(phase.details).map(([k, v]) => (
                    <span key={k} style={{ marginRight: '1rem' }}>{k}: <strong>{String(v)}</strong></span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Phases;
