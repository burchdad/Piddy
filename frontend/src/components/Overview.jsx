import React from 'react';
import '../styles/components.css';

function Overview({ systemStatus }) {
  if (!systemStatus) {
    return <div className="page"><h2>Loading...</h2></div>;
  }

  return (
    <div className="page overview">
      <div className="header-section">
        <h2>System Overview</h2>
        <p className="timestamp">{new Date(systemStatus.last_updated).toLocaleString()}</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">System Status</div>
          <div className="metric-value" style={{ color: systemStatus.status === 'operational' ? '#51cf66' : '#ff6b6b' }}>
            {systemStatus.status}
          </div>
          <div className="metric-sub">Current state</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Agents Online</div>
          <div className="metric-value">{systemStatus.agents_online}</div>
          <div className="metric-sub">Available agents</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Active Missions</div>
          <div className="metric-value">{systemStatus.missions_active}</div>
          <div className="metric-sub">In progress</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Pending Decisions</div>
          <div className="metric-value">{systemStatus.decisions_pending}</div>
          <div className="metric-sub">Awaiting approval</div>
        </div>
      </div>

      <div className="status-section">
        <h3>System Health</h3>
        <div className="health-indicator">
          <div className="indicator-item">
            <span className="indicator-dot" style={{ backgroundColor: '#51cf66' }}></span>
            <span>All systems operational</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Overview;
