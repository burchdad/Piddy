import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Sidebar({ currentPage, onPageChange }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const sections = [
    {
      label: 'Home',
      items: [
        { id: 'chat',     icon: '💬', label: 'Chat',     page: 'chat' },
        { id: 'overview',  icon: '📊', label: 'Overview', page: 'overview' },
        { id: 'doctor',   icon: '🩺', label: 'Health',   page: 'doctor' },
        { id: 'settings',  icon: '⚙️', label: 'Settings', page: 'settings' },
        { id: 'export',    icon: '📦', label: 'Export',   page: 'export' },
        { id: 'scanner',   icon: '🔍', label: 'Scanner',  page: 'scanner' },
        { id: 'updater',   icon: '⬆️', label: 'Updates',  page: 'updater' },
        { id: 'integrations', icon: '🔌', label: 'Channels', page: 'integrations' },
        { id: 'browser',   icon: '🌐', label: 'Browser',  page: 'browser' },
        { id: 'productivity', icon: '📅', label: 'Productivity', page: 'productivity' },
      ],
    },
    {
      label: 'Work',
      items: [
        { id: 'skills',        icon: '⚡', label: 'Skills',   page: 'skills' },
        { id: 'sessions',      icon: '🕘', label: 'History',  page: 'sessions' },
        { id: 'agents',        icon: '🤖', label: 'Agents',   page: 'agents' },
        { id: 'missions',      icon: '🎯', label: 'Missions', page: 'missions' },
        { id: 'live-activity', icon: '📡', label: 'Activity', page: 'live-activity' },
      ],
    },
  ];

  const toolsItems = [
    { id: 'messages',     icon: '✉️', label: 'Messages',    page: 'messages' },
    { id: 'logs',         icon: '📝', label: 'Logs',        page: 'logs' },
    { id: 'tests',        icon: '✅', label: 'Tests',       page: 'tests' },
    { id: 'metrics',      icon: '📈', label: 'Metrics',     page: 'metrics' },
    { id: 'approvals',    icon: '📋', label: 'Approvals',   page: 'approvals' },
    { id: 'decisions',    icon: '🧠', label: 'Decisions',   page: 'decisions' },
    { id: 'phases',       icon: '🚀', label: 'Phases',      page: 'phases' },
    { id: 'security',     icon: '🔒', label: 'Security',    page: 'security' },
    { id: 'database',     icon: '🗄️', label: 'Database',    page: 'database' },
    { id: 'dependencies', icon: '🔗', label: 'Graph',       page: 'dependencies' },
  ];

  // Auto-open tools section if one of its pages is active
  const toolsActive = toolsItems.some(t => t.page === currentPage);

  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);
    window.addEventListener('online', goOnline);
    window.addEventListener('offline', goOffline);
    return () => { window.removeEventListener('online', goOnline); window.removeEventListener('offline', goOffline); };
  }, []);

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
        {/* Home + Work sections */}
        {sections.map((section) => (
          <div key={section.label} className="sidebar-section">
            {!isCollapsed && <div className="sidebar-section-label">{section.label}</div>}
            {section.items.map((item) => (
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
          </div>
        ))}

        {/* Tools — collapsible */}
        <div className="sidebar-section">
          {!isCollapsed ? (
            <button
              className="sidebar-section-toggle"
              onClick={() => setToolsOpen(!toolsOpen)}
            >
              <span className="sidebar-section-label" style={{ padding: 0 }}>Tools</span>
              <span className={`toggle-arrow ${toolsOpen || toolsActive ? 'open' : ''}`}>›</span>
            </button>
          ) : (
            <div className="sidebar-section-label">•</div>
          )}
          {(toolsOpen || toolsActive || isCollapsed) && toolsItems.map((item) => (
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
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="status-dot" style={isOnline ? {} : { background: '#f59e0b' }}></span>
          {!isCollapsed && <span className="status-text">{isOnline ? 'Online' : 'Offline — Local Only'}</span>}
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
