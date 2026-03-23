import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Productivity() {
  const [status, setStatus] = useState(null);
  const [calEvents, setCalEvents] = useState(null);
  const [jiraIssues, setJiraIssues] = useState(null);
  const [notionPages, setNotionPages] = useState(null);
  const [loading, setLoading] = useState({});
  const [error, setError] = useState(null);

  const refresh = async () => {
    try {
      const data = await apiCall('/api/productivity/status');
      setStatus(data);
    } catch {
      setError('Could not reach backend');
    }
  };

  useEffect(() => { refresh(); }, []);

  const loadCalendar = async () => {
    setLoading(p => ({ ...p, cal: true }));
    try {
      const data = await apiCall('/api/productivity/calendar/events');
      setCalEvents(data);
    } catch { setError('Calendar fetch failed'); }
    finally { setLoading(p => ({ ...p, cal: false })); }
  };

  const loadJira = async () => {
    setLoading(p => ({ ...p, jira: true }));
    try {
      const data = await apiCall('/api/productivity/jira/issues');
      setJiraIssues(data);
    } catch { setError('Jira fetch failed'); }
    finally { setLoading(p => ({ ...p, jira: false })); }
  };

  const loadNotion = async () => {
    setLoading(p => ({ ...p, notion: true }));
    try {
      const data = await apiCall('/api/productivity/notion/search');
      setNotionPages(data);
    } catch { setError('Notion fetch failed'); }
    finally { setLoading(p => ({ ...p, notion: false })); }
  };

  const connectors = [
    {
      id: 'google_calendar',
      name: 'Google Calendar',
      icon: '📅',
      description: 'View upcoming events',
      onLoad: loadCalendar,
      data: calEvents,
      loadingKey: 'cal',
      renderData: (d) => {
        if (d?.error) return <p style={{ color: '#ff6b6b' }}>{d.error}</p>;
        const events = d?.events || [];
        if (!events.length) return <p style={{ opacity: 0.6 }}>No upcoming events</p>;
        return (
          <div style={{ display: 'grid', gap: 8 }}>
            {events.map((e, i) => (
              <div key={i} style={{ padding: 10, background: 'rgba(255,255,255,0.04)', borderRadius: 8, fontSize: 13 }}>
                <strong>{e.summary}</strong>
                <br />
                <span style={{ opacity: 0.6 }}>{e.start} → {e.end}</span>
                {e.location && <span style={{ opacity: 0.5, marginLeft: 8 }}>📍 {e.location}</span>}
              </div>
            ))}
          </div>
        );
      },
    },
    {
      id: 'jira',
      name: 'Jira',
      icon: '🎫',
      description: 'View assigned issues',
      onLoad: loadJira,
      data: jiraIssues,
      loadingKey: 'jira',
      renderData: (d) => {
        if (d?.error) return <p style={{ color: '#ff6b6b' }}>{d.error}</p>;
        const issues = d?.issues || [];
        if (!issues.length) return <p style={{ opacity: 0.6 }}>No issues found</p>;
        return (
          <div style={{ display: 'grid', gap: 8 }}>
            {issues.map((iss, i) => (
              <div key={i} style={{ padding: 10, background: 'rgba(255,255,255,0.04)', borderRadius: 8, fontSize: 13, display: 'flex', gap: 12, alignItems: 'center' }}>
                <span style={{ fontWeight: 600, minWidth: 80 }}>{iss.key}</span>
                <span style={{ flex: 1 }}>{iss.summary}</span>
                <span style={{ padding: '2px 8px', borderRadius: 4, background: 'rgba(74,222,128,0.15)', color: '#4ade80', fontSize: 12 }}>{iss.status}</span>
              </div>
            ))}
          </div>
        );
      },
    },
    {
      id: 'notion',
      name: 'Notion',
      icon: '📝',
      description: 'Search pages and databases',
      onLoad: loadNotion,
      data: notionPages,
      loadingKey: 'notion',
      renderData: (d) => {
        if (d?.error) return <p style={{ color: '#ff6b6b' }}>{d.error}</p>;
        const pages = d?.pages || [];
        if (!pages.length) return <p style={{ opacity: 0.6 }}>No pages found</p>;
        return (
          <div style={{ display: 'grid', gap: 8 }}>
            {pages.map((p, i) => (
              <div key={i} style={{ padding: 10, background: 'rgba(255,255,255,0.04)', borderRadius: 8, fontSize: 13, display: 'flex', justifyContent: 'space-between' }}>
                <span>{p.title || '(untitled)'}</span>
                <span style={{ opacity: 0.5, fontSize: 12 }}>{p.type}</span>
              </div>
            ))}
          </div>
        );
      },
    },
  ];

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>Productivity Connectors</h2>
          <p className="doctor-subtitle">Google Calendar, Jira, and Notion integrations</p>
        </div>
        <button className="action-btn" onClick={refresh}>↻ Refresh</button>
      </div>

      {error && <div style={{ margin: '12px 0', padding: 10, background: '#2a1a1a', border: '1px solid #ff6b6b', borderRadius: 8, color: '#ff6b6b' }}>{error}</div>}

      <div style={{ display: 'grid', gap: 20 }}>
        {connectors.map(c => {
          const info = status?.[c.id] || {};
          const configured = info.configured;
          return (
            <div key={c.id} style={{ padding: 20, borderRadius: 12, background: 'var(--card-bg, #1a1a2e)', border: '1px solid var(--border, #333)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <div>
                  <h3 style={{ margin: 0 }}>{c.icon} {c.name}</h3>
                  <p style={{ margin: '4px 0 0', opacity: 0.7, fontSize: 14 }}>{c.description}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 13, color: configured ? '#4ade80' : '#999' }}>
                    {configured ? '✅ Configured' : '❌ Not configured'}
                  </span>
                  {configured && (
                    <button className="action-btn" onClick={c.onLoad} disabled={loading[c.loadingKey]}>
                      {loading[c.loadingKey] ? '…' : 'Load'}
                    </button>
                  )}
                </div>
              </div>

              {!configured && (
                <p style={{ fontSize: 13, opacity: 0.6 }}>Add token in Settings → .env to enable this connector.</p>
              )}

              {c.data && (
                <div style={{ marginTop: 12 }}>
                  {c.renderData(c.data)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Productivity;
