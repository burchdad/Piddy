import React from 'react';
import '../styles/components.css';

function Overview({ systemStatus }) {
  if (!systemStatus) {
    return <div className="page">Loading system status...</div>;
  }

  const metrics = systemStatus.metrics;

  return (
    <div className="page overview">
      <div className="header-section">
        <h2>System Overview</h2>
        <p className="timestamp">{new Date(systemStatus.timestamp).toLocaleString()}</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Agents Online</div>
          <div className="metric-value">{metrics.agents_online}</div>
          <div className="metric-sub">/ {metrics.agents_online + metrics.agents_offline} Total</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Recent Messages</div>
          <div className="metric-value">{metrics.recent_messages}</div>
          <div className="metric-sub">Last 24 hours</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Phases In Progress</div>
          <div className="metric-value">{metrics.phases_in_progress}</div>
          <div className="metric-sub">Running</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Security Issues</div>
          <div className="metric-value" style={{ color: metrics.security_issues > 0 ? '#ff6b6b' : '#51cf66' }}>
            {metrics.security_issues}
          </div>
          <div className="metric-sub">Critical</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Performance Warnings</div>
          <div className="metric-value" style={{ color: metrics.performance_warnings > 0 ? '#ffa500' : '#51cf66' }}>
            {metrics.performance_warnings}
          </div>
          <div className="metric-sub">Alerts</div>
        </div>

        <div className="metric-card">
          <div className="metric-card-split">
            <div>
              <div className="metric-label">Tests Passed</div>
              <div className="metric-value" style={{ color: '#51cf66' }}>{metrics.tests_passed}</div>
            </div>
            <div className="divider"></div>
            <div>
              <div className="metric-label">Tests Failed</div>
              <div className="metric-value" style={{ color: metrics.tests_failed > 0 ? '#ff6b6b' : '#51cf66' }}>
                {metrics.tests_failed}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="system-info">
        <h3>System Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <label>Version:</label>
            <value>{systemStatus.system.version}</value>
          </div>
          <div className="info-item">
            <label>Environment:</label>
            <value>{systemStatus.system.environment}</value>
          </div>
          <div className="info-item">
            <label>Uptime:</label>
            <value>{Math.floor(systemStatus.system.uptime_seconds / 3600)}h {Math.floor((systemStatus.system.uptime_seconds % 3600) / 60)}m</value>
          </div>
          <div className="info-item">
            <label>Status:</label>
            <value className={`status-${systemStatus.system.status}`}>{systemStatus.system.status.toUpperCase()}</value>
          </div>
        </div>
      </div>

      <div className="quick-stats">
        <h3>Quick Stats</h3>
        <div className="stats-row">
          <div className="stat-item">
            <span className="stat-icon">👥</span>
            <span className="stat-text">{metrics.agents_online} Active Agents</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">💬</span>
            <span className="stat-text">{metrics.recent_messages} Messages</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">⚙️</span>
            <span className="stat-text">{metrics.phases_in_progress} Phases Running</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">✅</span>
            <span className="stat-text">{metrics.tests_passed} Tests Passing</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Overview;
