import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Decisions() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const data = await fetchApi('/api/decisions');
        setDecisions(Array.isArray(data) ? data : (data.decisions || []));
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

  const filtered = decisions.filter(d => {
    const matchSearch = !search || (d.task || '').toLowerCase().includes(search.toLowerCase()) || (d.action || '').toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || d.status === statusFilter;
    return matchSearch && matchStatus;
  });

  // Confidence distribution
  const highConf = decisions.filter(d => (d.confidence ?? 0) >= 0.8).length;
  const medConf = decisions.filter(d => (d.confidence ?? 0) >= 0.5 && (d.confidence ?? 0) < 0.8).length;
  const lowConf = decisions.filter(d => (d.confidence ?? 0) < 0.5).length;
  const avgConf = decisions.length ? (decisions.reduce((s, d) => s + (d.confidence ?? 0), 0) / decisions.length * 100).toFixed(0) : 0;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🧠 AI Decisions</h1>
      </div>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        <div className="metric-card"><div className="metric-value">{decisions.length}</div><div className="metric-label">Total</div></div>
        <div className="metric-card"><div className="metric-value">{avgConf}%</div><div className="metric-label">Avg Confidence</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: '#51cf66' }}>{highConf}</div><div className="metric-label">High (&ge;80%)</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: '#ffd93d' }}>{medConf}</div><div className="metric-label">Medium</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: '#ff6b6b' }}>{lowConf}</div><div className="metric-label">Low (&lt;50%)</div></div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <input type="text" placeholder="Search decisions…" value={search} onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 180, padding: '0.4rem 0.75rem', borderRadius: '0.4rem', border: '1px solid var(--border-color)', background: 'var(--bg-card)', color: 'var(--text-primary)' }} />
        {['all', 'pending', 'approved', 'rejected', 'executed'].map(s => (
          <button key={s} className={statusFilter === s ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
            onClick={() => setStatusFilter(s)}>{s === 'all' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}</button>
        ))}
      </div>

      <div className="decisions-list">
        {Array.isArray(filtered) && filtered.map((decision) => (
          <div key={decision.id} className="decision-card" onClick={() => setExpandedId(expandedId === decision.id ? null : decision.id)}>
            <div className="decision-header">
              <div className="decision-task">{decision.task}</div>
              <div className="decision-confidence">
                <span className="confidence-value">{((decision.confidence ?? 0) * 100).toFixed(0)}%</span>
                <div className="confidence-bar">
                  <div className="confidence-fill" style={{width: `${(decision.confidence ?? 0) * 100}%`}}></div>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <div className="decision-action">{decision.action}</div>
              {decision.status && <span style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem', borderRadius: '0.25rem', background: 'var(--bg-secondary)', color: 'var(--text-secondary)' }}>{decision.status}</span>}
            </div>
            {expandedId === decision.id && (
              <div className="decision-expanded">
                <div className="reasoning-chain">
                  <h4>Reasoning Chain:</h4>
                  {decision.reasoning_chain && Array.isArray(decision.reasoning_chain) && decision.reasoning_chain.map((step, idx) => (
                    <div key={idx} className="reasoning-step">
                      <span className="step-num">{idx + 1}</span>
                      <span className="step-text">{step.thought || step}</span>
                    </div>
                  ))}
                </div>
                {decision.factors && Array.isArray(decision.factors) && decision.factors.length > 0 && (
                  <div style={{ marginTop: '0.75rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem' }}>Factors:</h4>
                    {decision.factors.map((f, i) => (
                      <div key={i} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                        • {f.name || f.factor || JSON.stringify(f)}: <strong>{f.weight ?? f.value ?? ''}</strong>
                      </div>
                    ))}
                  </div>
                )}
                {decision.timestamp && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    {new Date(decision.timestamp).toLocaleString()}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
            {decisions.length === 0 ? 'No decisions recorded yet.' : 'No decisions match your filters.'}
          </div>
        )}
      </div>
    </div>
  );
}

export default Decisions;
