import React from 'react';
import { SECTIONS, BOTTOM_SECTIONS } from './ActivityBar';

/**
 * VS Code-style Sidebar Panel — shows sub-navigation items for the active section.
 * Sits between the Activity Bar and the main editor area.
 */
function SidebarPanel({ activeSection, activePage, onPageChange, isOpen }) {
  if (!isOpen) return null;

  const allSections = [...SECTIONS, ...BOTTOM_SECTIONS];
  const section = allSections.find(s => s.id === activeSection);
  if (!section) return null;

  return (
    <div className="sidebar-panel">
      <div className="sidebar-panel-header">
        <span className="sidebar-panel-title">{section.label.toUpperCase()}</span>
      </div>
      <nav className="sidebar-panel-nav">
        {section.items.map(item => (
          <button
            key={item.id}
            className={`sidebar-panel-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onPageChange(item.id)}
          >
            <span className="sidebar-panel-item-icon">{item.icon}</span>
            <span className="sidebar-panel-item-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

export default SidebarPanel;
