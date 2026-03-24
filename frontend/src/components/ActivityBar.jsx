import React from 'react';

/**
 * VS Code-style Activity Bar — thin vertical icon strip on the far left.
 * Each icon represents a section. Clicking toggles the sidebar panel.
 */

export const SECTIONS = [
  {
    id: 'health',
    icon: '🩺',
    label: 'Health',
    items: [
      { id: 'doctor', icon: '🩺', label: 'System Health' },
    ],
    defaultPage: 'doctor',
  },
  {
    id: 'skills',
    icon: '⚡',
    label: 'Skills',
    items: [
      { id: 'skills', icon: '⚡', label: 'Skills Library' },
    ],
    defaultPage: 'skills',
  },
  {
    id: 'projects',
    icon: '📁',
    label: 'Projects',
    items: [
      { id: 'projects', icon: '📁', label: 'Workspace' },
    ],
    defaultPage: 'projects',
  },
  {
    id: 'work',
    icon: '🤖',
    label: 'Agents & Work',
    items: [
      { id: 'agents', icon: '🤖', label: 'Agents' },
      { id: 'missions', icon: '🎯', label: 'Missions' },
      { id: 'live-activity', icon: '📡', label: 'Activity' },
      { id: 'decisions', icon: '🧠', label: 'Decisions' },
    ],
    defaultPage: 'agents',
  },
  {
    id: 'tools',
    icon: '🔧',
    label: 'Tools',
    items: [
      { id: 'scanner', icon: '🔍', label: 'Scanner' },
      { id: 'updater', icon: '⬆️', label: 'Updates' },
      { id: 'messages', icon: '✉️', label: 'Messages' },
      { id: 'logs', icon: '📝', label: 'Logs' },
      { id: 'tests', icon: '✅', label: 'Tests' },
      { id: 'metrics', icon: '📈', label: 'Metrics' },
      { id: 'approvals', icon: '📋', label: 'Approvals' },
      { id: 'phases', icon: '🚀', label: 'Phases' },
      { id: 'security', icon: '🔒', label: 'Security' },
      { id: 'database', icon: '🗄️', label: 'Database' },
      { id: 'dependencies', icon: '🔗', label: 'Graph' },
    ],
    defaultPage: 'scanner',
  },
  {
    id: 'connect',
    icon: '🔌',
    label: 'Connect',
    items: [
      { id: 'integrations', icon: '🔌', label: 'Channels' },
      { id: 'browser', icon: '🌐', label: 'Browser' },
      { id: 'productivity', icon: '📅', label: 'Productivity' },
    ],
    defaultPage: 'integrations',
  },
];

export const BOTTOM_SECTIONS = [
  {
    id: 'settings',
    icon: '⚙️',
    label: 'Settings',
    items: [{ id: 'settings', icon: '⚙️', label: 'Settings' }],
    defaultPage: 'settings',
  },
];

function ActivityBar({ activeSection, onSectionChange, chatOpen, onChatToggle, activePage, onPageChange }) {
  return (
    <div className="activity-bar">
      <div className="activity-bar-top">
        {/* Brand icon */}
        <div className="activity-bar-brand" title="Piddy">
          🎯
        </div>

        {/* Main section icons */}
        {SECTIONS.map(section => (
          <button
            key={section.id}
            className={`activity-bar-icon ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => onSectionChange(section.id)}
            title={section.label}
          >
            <span className="activity-bar-icon-emoji">{section.icon}</span>
            {activeSection === section.id && <div className="activity-bar-indicator" />}
          </button>
        ))}
      </div>

      <div className="activity-bar-bottom">
        {/* History */}
        <button
          className={`activity-bar-icon ${activePage === 'sessions' ? 'active' : ''}`}
          onClick={() => onPageChange('sessions')}
          title="History"
        >
          <span className="activity-bar-icon-emoji">🕘</span>
          {activePage === 'sessions' && <div className="activity-bar-indicator" />}
        </button>

        {/* Export */}
        <button
          className={`activity-bar-icon ${activePage === 'export' ? 'active' : ''}`}
          onClick={() => onPageChange('export')}
          title="Export"
        >
          <span className="activity-bar-icon-emoji">📦</span>
          {activePage === 'export' && <div className="activity-bar-indicator" />}
        </button>

        {/* Chat toggle */}
        <button
          className={`activity-bar-icon ${chatOpen ? 'active' : ''}`}
          onClick={onChatToggle}
          title={chatOpen ? 'Close Chat' : 'Open Chat'}
        >
          <span className="activity-bar-icon-emoji">💬</span>
          {chatOpen && <div className="activity-bar-indicator" />}
        </button>

        {/* Bottom section icons (Settings) */}
        {BOTTOM_SECTIONS.map(section => (
          <button
            key={section.id}
            className={`activity-bar-icon ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => onSectionChange(section.id)}
            title={section.label}
          >
            <span className="activity-bar-icon-emoji">{section.icon}</span>
            {activeSection === section.id && <div className="activity-bar-indicator" />}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ActivityBar;
