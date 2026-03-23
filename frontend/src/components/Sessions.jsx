import React, { useState, useEffect, useCallback } from 'react';
import { apiCall } from '../utils/api';

function Sessions({ onSelectSession }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiCall('/api/sessions');
      setSessions(data.sessions || []);
    } catch {
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const deleteSession = async (id, e) => {
    e.stopPropagation();
    try {
      await apiCall(`/api/sessions/${id}`, { method: 'DELETE' });
      setSessions(prev => prev.filter(s => s.session_id !== id));
    } catch { /* ignore */ }
  };

  const timeAgo = (ts) => {
    const diff = (Date.now() - new Date(ts).getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="sessions-page">
      <div className="sessions-header">
        <div>
          <h2>Chat History</h2>
          <p className="sessions-subtitle">{sessions.length} conversations</p>
        </div>
        <button className="chat-btn-secondary" onClick={load} disabled={loading}>
          Refresh
        </button>
      </div>

      {loading && sessions.length === 0 ? (
        <div className="doctor-loading"><div className="spinner" /><p>Loading sessions...</p></div>
      ) : sessions.length === 0 ? (
        <div className="sessions-empty">
          <div className="sessions-empty-icon">💬</div>
          <p>No conversations yet.</p>
          <p className="sessions-hint">Start a chat with Piddy to create your first session.</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map(s => (
            <div
              key={s.session_id}
              className="session-card"
              onClick={() => onSelectSession && onSelectSession(s.session_id)}
            >
              <div className="session-card-body">
                <div className="session-card-title">{s.title || 'Untitled'}</div>
                <div className="session-card-meta">
                  <span>{s.message_count || 0} messages</span>
                  <span className="session-card-dot">·</span>
                  <span>{timeAgo(s.updated_at || s.created_at)}</span>
                </div>
              </div>
              <button
                className="session-delete-btn"
                onClick={(e) => deleteSession(s.session_id, e)}
                title="Delete"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Sessions;
