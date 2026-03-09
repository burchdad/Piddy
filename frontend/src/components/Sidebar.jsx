import React, { useState } from 'react';
import '../styles/components.css';

function Sidebar({ currentPage, onPageChange }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const menuItems = [
    { id: 'overview', icon: '📊', label: 'Overview', page: 'overview' },
    { id: 'agents', icon: '🤖', label: 'Agents', page: 'agents' },
    { id: 'messages', icon: '💬', label: 'Messages', page: 'messages' },
    { id: 'logs', icon: '📝', label: 'Logs', page: 'logs' },
    { id: 'tests', icon: '✅', label: 'Tests', page: 'tests' },
    { id: 'metrics', icon: '📈', label: 'Metrics', page: 'metrics' },
    { id: 'phases', icon: '🚀', label: 'Phases', page: 'phases' },
    { id: 'security', icon: '🔒', label: 'Security', page: 'security' },
    { id: 'rate-limits', icon: '🚦', label: 'Rate Limits', page: 'rate-limits' },
    { id: 'decisions', icon: '🧠', label: 'Decisions', page: 'decisions' },
    { id: 'missions', icon: '🎯', label: 'Missions', page: 'missions' },
    { id: 'dependencies', icon: '📊', label: 'Graph', page: 'dependencies' },
    { id: 'replay', icon: '🎬', label: 'Replay', page: 'replay' },
    { id: 'database', icon: '🗄️', label: 'Database', page: 'database' },
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          {!isCollapsed && (
            <>
              <span className="brand-icon">🎯</span>
              <span className="brand-text">Piddy</span>
            </>
          )}
        </div>
        <button 
          className="collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${currentPage === item.page ? 'active' : ''}`}
            onClick={() => onPageChange(item.page)}
            title={item.label}
          >
            <span className="nav-icon">{item.icon}</span>
            {!isCollapsed && <span className="nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          {!isCollapsed && <span className="status-text">Connected</span>}
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
