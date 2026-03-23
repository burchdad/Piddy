import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Integrations() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState({});
  const [error, setError] = useState(null);

  const refresh = async () => {
    try {
      const data = await apiCall('/api/integrations/status');
      setStatus(data);
    } catch {
      setError('Could not reach backend');
    }
  };

  useEffect(() => { refresh(); }, []);

  const toggle = async (platform, action) => {
    setLoading(prev => ({ ...prev, [platform]: true }));
    try {
      await apiCall(`/api/integrations/${platform}/${action}`, { method: 'POST' });
      await refresh();
    } catch {
      setError(`Failed to ${action} ${platform}`);
    } finally {
      setLoading(prev => ({ ...prev, [platform]: false }));
    }
  };

  const channels = [
    {
      id: 'slack',
      name: 'Slack',
      icon: '💬',
      description: 'Team messaging via Slack Bot (Socket Mode)',
      managed: false, // Slack is started via start_piddy.py, not toggled here
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: '🎮',
      description: 'Discord server bot — DMs and @mentions',
      managed: true,
    },
    {
      id: 'telegram',
      name: 'Telegram',
      icon: '✈️',
      description: 'Telegram bot — commands and chat',
      managed: true,
    },
  ];

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>Channel Integrations</h2>
          <p className="doctor-subtitle">Manage Slack, Discord, and Telegram connections</p>
        </div>
        <button className="action-btn" onClick={refresh}>↻ Refresh</button>
      </div>

      {error && <div className="alert-error" style={{ margin: '12px 0', padding: '10px', background: '#2a1a1a', border: '1px solid #ff6b6b', borderRadius: 8, color: '#ff6b6b' }}>{error}</div>}

      <div className="doctor-checks" style={{ display: 'grid', gap: 16 }}>
        {channels.map(ch => {
          const info = status?.[ch.id] || {};
          const running = info.running || info.configured;
          const libOk = info.library_installed !== false;

          return (
            <div key={ch.id} className="check-card" style={{ padding: 20, borderRadius: 12, background: 'var(--card-bg, #1a1a2e)', border: '1px solid var(--border, #333)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ margin: 0 }}>{ch.icon} {ch.name}</h3>
                  <p style={{ margin: '4px 0 0', opacity: 0.7, fontSize: 14 }}>{ch.description}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: '50%', background: running ? '#4ade80' : '#666' }} />
                  <span style={{ fontSize: 13, color: running ? '#4ade80' : '#999' }}>{running ? 'Connected' : 'Offline'}</span>
                  {ch.managed && (
                    <button
                      className="action-btn"
                      disabled={loading[ch.id] || !libOk}
                      onClick={() => toggle(ch.id, running ? 'stop' : 'start')}
                      style={{ minWidth: 70 }}
                    >
                      {loading[ch.id] ? '…' : running ? 'Stop' : 'Start'}
                    </button>
                  )}
                </div>
              </div>

              {!libOk && (
                <p style={{ marginTop: 8, fontSize: 13, color: '#f59e0b' }}>
                  ⚠ Library not installed. Run: <code>pip install {ch.id === 'discord' ? 'discord.py' : 'python-telegram-bot'}</code>
                </p>
              )}

              {info.guilds > 0 && (
                <p style={{ marginTop: 6, fontSize: 13, opacity: 0.7 }}>Guilds: {info.guilds}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Integrations;
