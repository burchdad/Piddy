import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

/**
 * VS Code-style Status Bar — bottom strip showing system state at a glance.
 */
function StatusBar({ activePage, backendOnline }) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [agentCount, setAgentCount] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);
    window.addEventListener('online', goOnline);
    window.addEventListener('offline', goOffline);
    return () => {
      window.removeEventListener('online', goOnline);
      window.removeEventListener('offline', goOffline);
    };
  }, []);

  // Poll lightweight status info
  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const data = await apiCall('/api/system/overview');
        if (data.agents_online != null) setAgentCount(data.agents_online);
        if (data.status) setHealthStatus(data.status);
      } catch { /* silent */ }
    };
    fetchInfo();
    const interval = setInterval(fetchInfo, 30000);
    return () => clearInterval(interval);
  }, []);

  // Map page id to display name
  const pageNames = {
    overview: 'Overview', doctor: 'Health', skills: 'Skills',
    agents: 'Agents', missions: 'Missions', 'live-activity': 'Activity',
    decisions: 'Decisions', sessions: 'History', export: 'Export',
    scanner: 'Scanner', updater: 'Updates', messages: 'Messages',
    logs: 'Logs', tests: 'Tests', metrics: 'Metrics',
    approvals: 'Approvals', phases: 'Phases', security: 'Security',
    database: 'Database', dependencies: 'Graph', integrations: 'Channels',
    browser: 'Browser', productivity: 'Productivity', settings: 'Settings',
    chat: 'Chat',
  };

  return (
    <div className="status-bar">
      <div className="status-bar-left">
        {/* Connection status */}
        <div className="status-bar-item" title={backendOnline ? 'Backend connected' : 'Backend offline'}>
          <span className={`status-bar-dot ${backendOnline ? 'connected' : 'disconnected'}`} />
          <span>{backendOnline ? 'Connected' : 'Offline'}</span>
        </div>

        {/* Network */}
        {!isOnline && (
          <div className="status-bar-item status-bar-warning" title="No internet connection">
            <span>⚠ No Internet</span>
          </div>
        )}

        {/* Agent count */}
        {agentCount != null && (
          <div className="status-bar-item" title={`${agentCount} agents online`}>
            <span>🤖 {agentCount} agents</span>
          </div>
        )}
      </div>

      <div className="status-bar-center">
        {/* Current page */}
        <div className="status-bar-item">
          <span>{pageNames[activePage] || activePage}</span>
        </div>
      </div>

      <div className="status-bar-right">
        {/* Health */}
        {healthStatus && (
          <div className={`status-bar-item status-bar-health ${healthStatus}`} title={`System: ${healthStatus}`}>
            <span className={`status-bar-health-dot ${healthStatus}`} />
            <span>{healthStatus === 'operational' ? 'Healthy' : healthStatus}</span>
          </div>
        )}

        {/* Model */}
        <div className="status-bar-item" title="Local AI Model">
          <span>🧠 Ollama</span>
        </div>
      </div>
    </div>
  );
}

export default StatusBar;
