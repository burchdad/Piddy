import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';
import PiddyAvatar from './PiddyAvatar';

function Home({ systemStatus, onNavigate }) {
  const [recentActivity, setRecentActivity] = useState([]);
  const [healthSummary, setHealthSummary] = useState(null);
  const [missions, setMissions] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [healthData, missionsData, activityData] = await Promise.allSettled([
          apiCall('/api/doctor'),
          apiCall('/api/missions'),
          apiCall('/api/live-activity'),
        ]);
        if (healthData.status === 'fulfilled') setHealthSummary(healthData.value);
        if (missionsData.status === 'fulfilled') {
          const m = missionsData.value?.missions || missionsData.value || [];
          setMissions(Array.isArray(m) ? m.slice(0, 5) : []);
        }
        if (activityData.status === 'fulfilled') {
          const a = activityData.value?.events || activityData.value || [];
          setRecentActivity(Array.isArray(a) ? a.slice(0, 6) : []);
        }
      } catch {}
    };
    load();
  }, []);

  const s = systemStatus || {};
  const uptime = s.uptime_seconds ? formatUptime(s.uptime_seconds) : '—';
  const healthChecks = healthSummary?.checks || [];
  const okCount = healthChecks.filter(c => c.status === 'ok').length;
  const warnCount = healthChecks.filter(c => c.status === 'warn').length;
  const errCount = healthChecks.filter(c => c.status === 'error').length;

  return (
    <div className="home-page">
      {/* Hero greeting */}
      <div className="home-hero">
        <div className="home-hero-text">
          <PiddyAvatar size="xl" glow className="home-hero-avatar" />
          <h1 className="home-title">
            Welcome to <span className="home-brand">Piddy</span>
          </h1>
          <p className="home-subtitle">Your AI backend developer is online and ready to build.</p>
        </div>
        <div className="home-status-pill" data-status={s.status === 'operational' ? 'ok' : 'warn'}>
          <span className="home-status-dot" />
          {s.status === 'operational' ? 'All Systems Operational' : s.status || 'Connecting...'}
        </div>
      </div>

      {/* Stat cards */}
      <div className="home-stats">
        <StatCard icon="🤖" label="Agents Online" value={s.agents_online ?? '—'} sub={`${s.agents_total ?? 0} registered`} onClick={() => onNavigate('agents')} />
        <StatCard icon="🎯" label="Active Missions" value={s.missions_active ?? 0} sub="in progress" onClick={() => onNavigate('missions')} />
        <StatCard icon="🧠" label="Pending Decisions" value={s.decisions_pending ?? 0} sub="awaiting review" onClick={() => onNavigate('decisions')} />
        <StatCard icon="⏱️" label="Uptime" value={uptime} sub="since last restart" />
      </div>

      {/* Quick actions */}
      <div className="home-section">
        <h2 className="home-section-title">Quick Actions</h2>
        <div className="home-actions">
          <ActionCard icon="💬" title="Start Chat" desc="Ask Piddy to build something" onClick={() => {
            if (window.__piddyChat) window.__piddyChat.focus?.();
          }} />
          <ActionCard icon="🩺" title="System Health" desc="Run diagnostics check" onClick={() => onNavigate('doctor')} />
          <ActionCard icon="📁" title="Projects" desc="Browse your workspace" onClick={() => onNavigate('projects')} />
          <ActionCard icon="⚡" title="Skills Library" desc="View all capabilities" onClick={() => onNavigate('skills')} />
          <ActionCard icon="🔍" title="Scanner" desc="Scan host environment" onClick={() => onNavigate('scanner')} />
          <ActionCard icon="⚙️" title="Settings" desc="Configure API keys & models" onClick={() => onNavigate('settings')} />
        </div>
      </div>

      {/* Two-column: Health + Activity */}
      <div className="home-grid-2">
        {/* Health summary */}
        <div className="home-card">
          <div className="home-card-header">
            <h3>System Health</h3>
            <button className="home-card-link" onClick={() => onNavigate('doctor')}>View All →</button>
          </div>
          {healthChecks.length > 0 ? (
            <>
              <div className="home-health-bar">
                <span className="home-health-tag ok">{okCount} passing</span>
                {warnCount > 0 && <span className="home-health-tag warn">{warnCount} warning{warnCount > 1 ? 's' : ''}</span>}
                {errCount > 0 && <span className="home-health-tag err">{errCount} error{errCount > 1 ? 's' : ''}</span>}
              </div>
              <div className="home-health-list">
                {healthChecks.filter(c => c.status !== 'ok' && c.status !== 'skip').slice(0, 4).map((c, i) => (
                  <div key={i} className="home-health-item">
                    <span className={`home-health-dot ${c.status}`} />
                    <span className="home-health-name">{c.name}</span>
                    <span className="home-health-msg">{c.message}</span>
                  </div>
                ))}
                {healthChecks.filter(c => c.status !== 'ok' && c.status !== 'skip').length === 0 && (
                  <p className="home-muted">All checks passing — no issues detected.</p>
                )}
              </div>
            </>
          ) : (
            <p className="home-muted">Loading health data...</p>
          )}
        </div>

        {/* Recent activity */}
        <div className="home-card">
          <div className="home-card-header">
            <h3>Recent Activity</h3>
            <button className="home-card-link" onClick={() => onNavigate('live-activity')}>View All →</button>
          </div>
          {recentActivity.length > 0 ? (
            <div className="home-activity-list">
              {recentActivity.map((evt, i) => (
                <div key={i} className="home-activity-item">
                  <span className="home-activity-icon">{evt.icon || '📌'}</span>
                  <div className="home-activity-body">
                    <span className="home-activity-text">{evt.title || evt.message || evt.event || 'Event'}</span>
                    {evt.timestamp && (
                      <span className="home-activity-time">{new Date(evt.timestamp).toLocaleTimeString()}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="home-muted">No recent activity yet. Start a chat or run a mission!</p>
          )}
        </div>
      </div>

      {/* Active missions */}
      {missions.length > 0 && (
        <div className="home-section">
          <div className="home-card-header" style={{ marginBottom: 12 }}>
            <h2 className="home-section-title" style={{ margin: 0 }}>Active Missions</h2>
            <button className="home-card-link" onClick={() => onNavigate('missions')}>View All →</button>
          </div>
          <div className="home-missions">
            {missions.map((m, i) => (
              <div key={i} className="home-mission-card" onClick={() => onNavigate('missions')}>
                <div className="home-mission-name">{m.name || m.title || `Mission ${i + 1}`}</div>
                <div className="home-mission-status" data-status={m.status}>{m.status || 'active'}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value, sub, onClick }) {
  return (
    <div className="home-stat-card" onClick={onClick} style={onClick ? { cursor: 'pointer' } : {}}>
      <div className="home-stat-icon">{icon}</div>
      <div className="home-stat-value">{value}</div>
      <div className="home-stat-label">{label}</div>
      <div className="home-stat-sub">{sub}</div>
    </div>
  );
}

function ActionCard({ icon, title, desc, onClick }) {
  return (
    <button className="home-action-card" onClick={onClick}>
      <span className="home-action-icon">{icon}</span>
      <span className="home-action-title">{title}</span>
      <span className="home-action-desc">{desc}</span>
    </button>
  );
}

function formatUptime(seconds) {
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export default Home;
