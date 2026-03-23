import React, { useState } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

const EXPORT_ITEMS = [
  { id: 'conversations', label: 'Conversations', icon: '💬', desc: 'All chat sessions and messages', endpoint: '/api/export/conversations' },
  { id: 'knowledge-base', label: 'Knowledge Base', icon: '📚', desc: 'Library catalog (books, courses, skills, etc.)', endpoint: '/api/export/knowledge-base' },
  { id: 'agent-state', label: 'Agent State', icon: '🤖', desc: 'Agent data, decisions, missions, approvals', endpoint: '/api/export/agent-state' },
  { id: 'settings', label: 'Settings', icon: '⚙️', desc: 'Current configuration (no secrets)', endpoint: '/api/export/settings' },
];

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function Export() {
  const [downloading, setDownloading] = useState({});
  const [results, setResults] = useState({});

  const handleExport = async (item) => {
    setDownloading(p => ({ ...p, [item.id]: true }));
    try {
      const data = await fetchApi(item.endpoint);
      const ts = new Date().toISOString().slice(0, 10);
      downloadJson(data, `piddy-${item.id}-${ts}.json`);
      setResults(p => ({ ...p, [item.id]: { ok: true } }));
    } catch (err) {
      setResults(p => ({ ...p, [item.id]: { ok: false, error: err.message } }));
    } finally {
      setDownloading(p => ({ ...p, [item.id]: false }));
    }
  };

  const handleExportAll = async () => {
    for (const item of EXPORT_ITEMS) {
      await handleExport(item);
    }
  };

  return (
    <div className="page">
      <div className="section-header">
        <h1>📦 Export &amp; Backup</h1>
        <button className="btn-primary" onClick={handleExportAll}>Export All</button>
      </div>
      <p className="export-desc">Download your Piddy data as JSON files. All exports stay on your machine.</p>

      <div className="export-grid">
        {EXPORT_ITEMS.map(item => (
          <div key={item.id} className="export-card">
            <div className="export-card-icon">{item.icon}</div>
            <div className="export-card-body">
              <h3>{item.label}</h3>
              <p>{item.desc}</p>
            </div>
            <button
              className="btn-secondary"
              disabled={downloading[item.id]}
              onClick={() => handleExport(item)}
            >
              {downloading[item.id] ? 'Exporting…' : 'Download'}
            </button>
            {results[item.id] && (
              <div className={`export-result ${results[item.id].ok ? 'success' : 'error'}`}>
                {results[item.id].ok ? '✓ Saved' : results[item.id].error}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
