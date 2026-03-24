import React, { useState, useEffect } from 'react';
import './styles/App.css';
import './styles/components.css';
import './styles/dashboard.css';
import './styles/setup.css';
import './styles/vscode-layout.css';
import { apiCall } from './utils/api';
import { isBackendReachable } from './utils/api';

// Layout components
import ActivityBar, { SECTIONS, BOTTOM_SECTIONS } from './components/ActivityBar';
import SidebarPanel from './components/SidebarPanel';
import StatusBar from './components/StatusBar';

// Page components
import Overview from './components/Overview';
import Chat from './components/Chat';
import Doctor from './components/Doctor';
import Skills from './components/Skills';
import Sessions from './components/Sessions';
import Agents from './components/Agents';
import Messages from './components/Messages';
import Logs from './components/Logs';
import Tests from './components/Tests';
import Metrics from './components/Metrics';
import Phases from './components/Phases';
import Security from './components/Security';
import Decisions from './components/Decisions';
import Missions from './components/Missions';
import DependencyGraph from './components/DependencyGraph';
import { DatabasePerformance } from './components/DatabasePerformance';
import Approvals from './components/Approvals';
import LiveActivity from './components/LiveActivity';
import Export from './components/Export';
import Scanner from './components/Scanner';
import Updater from './components/Updater';
import Integrations from './components/Integrations';
import BrowserTool from './components/BrowserTool';
import Productivity from './components/Productivity';
import ProjectWorkspace from './components/ProjectWorkspace';
import CodePanel from './components/CodePanel';
import { ToastProvider } from './components/Toast';
import Setup from './components/Setup';

// Map page ids to their parent section
const PAGE_TO_SECTION = {};
[...SECTIONS, ...BOTTOM_SECTIONS].forEach(section => {
  section.items.forEach(item => {
    PAGE_TO_SECTION[item.id] = section.id;
  });
});

function App() {
  const [activeSection, setActiveSection] = useState('work');
  const [activePage, setActivePage] = useState('agents');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatOpen, setChatOpen] = useState(true);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [needsSetup, setNeedsSetup] = useState(null);
  const [backendOnline, setBackendOnline] = useState(null);
  const [codeFiles, setCodeFiles] = useState([]);

  // Listen for Electron menu actions
  useEffect(() => {
    if (!window.piddyMenu) return;

    window.piddyMenu.onNavigate((page) => {
      handlePageChange(page);
    });

    window.piddyMenu.onAction((action) => {
      switch (action) {
        case 'toggle-sidebar':
          setSidebarOpen(prev => !prev);
          break;
        case 'toggle-chat':
          setChatOpen(prev => !prev);
          break;
        case 'open-chat':
          setChatOpen(true);
          break;
        case 'new-chat':
          setChatOpen(true);
          if (window.__piddyChat) window.__piddyChat.loadSession(null);
          break;
        case 'show-shortcuts':
          setShowShortcuts(prev => !prev);
          break;
      }
    });
  }, []); // runs once on mount

  // Check config status on mount
  useEffect(() => {
    const checkConfig = async () => {
      const reachable = await isBackendReachable();
      setBackendOnline(reachable);
      if (!reachable) {
        setNeedsSetup(false);
        return;
      }
      try {
        const data = await apiCall('/api/config/status');
        setNeedsSetup(!data.configured);
      } catch {
        setNeedsSetup(false);
      }
    };
    checkConfig();
  }, []);

  // Fetch system status periodically
  useEffect(() => {
    if (needsSetup !== false) return;

    const fetchStatus = async (retry = 0, maxRetries = 5) => {
      try {
        setError(null);
        const data = await apiCall('/api/system/overview');
        setSystemStatus({
          ...data,
          is_healthy: data.status === 'operational'
        });
        setLoading(false);
      } catch (err) {
        if (retry < maxRetries) {
          setTimeout(() => fetchStatus(retry + 1, maxRetries), 1000 * (retry + 1));
          return;
        }
        setError(err.message);
        setSystemStatus({ is_healthy: false, status: 'offline' });
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(() => fetchStatus(), 30000);
    return () => clearInterval(interval);
  }, [needsSetup]);

  // Handle activity bar section click
  const handleSectionChange = (sectionId) => {
    if (activeSection === sectionId && sidebarOpen) {
      // Same section clicked while open → toggle sidebar closed
      setSidebarOpen(false);
    } else {
      // New section or sidebar was closed → open and navigate
      setActiveSection(sectionId);
      setSidebarOpen(true);
      setCodeFiles([]);
      const allSections = [...SECTIONS, ...BOTTOM_SECTIONS];
      const section = allSections.find(s => s.id === sectionId);
      if (section) {
        setActivePage(section.defaultPage);
      }
    }
  };

  // Handle sidebar item click
  const handlePageChange = (pageId) => {
    setActivePage(pageId);
    // Auto-update section if navigating cross-section
    const section = PAGE_TO_SECTION[pageId];
    if (section && section !== activeSection) {
      setActiveSection(section);
    }
  };

  // Handle files created by Piddy (shows CodePanel in editor area)
  const handleFilesCreated = (files) => {
    if (files && files.length > 0) {
      setCodeFiles(files);
    }
  };

  const renderPage = () => {
    // If CodePanel has files open, show it in the editor area
    if (codeFiles.length > 0) {
      return <CodePanel files={codeFiles} onClose={() => setCodeFiles([])} />;
    }

    switch (activePage) {
      case 'overview':
        return <Overview systemStatus={systemStatus} />;
      case 'doctor':
        return <Doctor />;
      case 'skills':
        return <Skills />;
      case 'sessions':
        return (
          <Sessions
            onSelectSession={(sid) => {
              if (window.__piddyChat) window.__piddyChat.loadSession(sid);
              setChatOpen(true);
            }}
          />
        );
      case 'settings':
        return <Setup mode="settings" backendOnline={backendOnline} onComplete={() => { setNeedsSetup(false); setActivePage('overview'); }} />;
      case 'agents':
        return <Agents />;
      case 'messages':
        return <Messages />;
      case 'live-activity':
        return <LiveActivity />;
      case 'logs':
        return <Logs />;
      case 'tests':
        return <Tests />;
      case 'metrics':
        return <Metrics />;
      case 'phases':
        return <Phases />;
      case 'security':
        return <Security />;
      case 'decisions':
        return <Decisions />;
      case 'missions':
        return <Missions />;
      case 'dependencies':
        return <DependencyGraph />;
      case 'database':
        return <DatabasePerformance />;
      case 'approvals':
        return <Approvals />;
      case 'export':
        return <Export />;
      case 'scanner':
        return <Scanner />;
      case 'updater':
        return <Updater />;
      case 'integrations':
        return <Integrations />;
      case 'browser':
        return <BrowserTool />;
      case 'productivity':
        return <Productivity />;
      case 'projects':
        return <ProjectWorkspace />;
      default:
        return <Agents />;
    }
  };

  // Loading state
  if (needsSetup === null) {
    return (
      <div className="vscode-loading">
        <div className="spinner"></div>
        <p>Initializing Piddy...</p>
      </div>
    );
  }

  // Setup flow
  if (needsSetup) {
    return <ToastProvider><Setup backendOnline={backendOnline} onComplete={() => setNeedsSetup(false)} /></ToastProvider>;
  }

  // Detect Electron stream mode for chat badge
  const isElectron = !!(window.piddy?.streamManager || (typeof global !== 'undefined' && global.streamManager));

  return (
    <ToastProvider>
      <div className="vscode-layout">
        {/* ── Main Row: Activity Bar + Sidebar + Editor + Chat ── */}
        <div className="vscode-main">
          {/* Activity Bar (far left icons) */}
          <ActivityBar
            activeSection={activeSection}
            onSectionChange={handleSectionChange}
            chatOpen={chatOpen}
            onChatToggle={() => setChatOpen(!chatOpen)}
            activePage={activePage}
            onPageChange={(page) => { setCodeFiles([]); handlePageChange(page); }}
          />

          {/* Sidebar Panel (sub-navigation) */}
          <SidebarPanel
            activeSection={activeSection}
            activePage={activePage}
            onPageChange={(page) => { setCodeFiles([]); handlePageChange(page); }}
            isOpen={sidebarOpen}
          />

          {/* Main Editor Area */}
          <div className="editor-area">
            {backendOnline === false && (
              <div className="editor-offline-banner">
                <span>&#9888;</span>
                <span>
                  <strong>Backend offline.</strong> Start Piddy locally or use the Desktop app.
                </span>
              </div>
            )}
            <div className={`editor-content ${codeFiles.length > 0 ? 'editor-content-flush' : ''}`}>
              {loading ? (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>Connecting to Piddy...</p>
                </div>
              ) : (
                renderPage()
              )}
            </div>
          </div>

          {/* Chat Panel (right side) */}
          {chatOpen && (
            <div className="chat-panel-container">
              <div className="chat-panel-header">
                <div className="chat-panel-header-left">
                  <span className="chat-panel-header-title">Chat with Piddy</span>
                  {isElectron && <span className="chat-panel-header-badge">Live</span>}
                </div>
                <div className="chat-panel-header-actions">
                  <button className="chat-panel-btn" onClick={() => {
                    if (window.__piddyChat) window.__piddyChat.loadSession(null);
                  }} title="New Chat">+</button>
                  <button className="chat-panel-btn" onClick={() => handlePageChange('sessions')} title="History">🕘</button>
                  <button className="chat-panel-btn" onClick={() => setChatOpen(false)} title="Close">✕</button>
                </div>
              </div>
              <Chat onOpenSessions={() => { handlePageChange('sessions'); }} onFilesCreated={handleFilesCreated} />
            </div>
          )}
        </div>

        {/* Status Bar (bottom) */}
        <StatusBar activePage={activePage} backendOnline={backendOnline !== false} />

        {/* Keyboard Shortcuts Overlay */}
        {showShortcuts && (
          <div className="shortcuts-overlay" onClick={() => setShowShortcuts(false)}>
            <div className="shortcuts-modal" onClick={e => e.stopPropagation()}>
              <div className="shortcuts-header">
                <h2>Keyboard Shortcuts</h2>
                <button className="shortcuts-close" onClick={() => setShowShortcuts(false)}>✕</button>
              </div>
              <div className="shortcuts-grid">
                <div className="shortcuts-section">
                  <h3>Navigation</h3>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+1</span><span>Open Chat</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+2</span><span>Overview</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+3</span><span>Health</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+4</span><span>Skills</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+5</span><span>Agents</span></div>
                </div>
                <div className="shortcuts-section">
                  <h3>Panels</h3>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+B</span><span>Toggle Sidebar</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+J</span><span>Toggle Chat Panel</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+N</span><span>New Chat</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">F11</span><span>Fullscreen</span></div>
                </div>
                <div className="shortcuts-section">
                  <h3>General</h3>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+,</span><span>Settings</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+=</span><span>Zoom In</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+-</span><span>Zoom Out</span></div>
                  <div className="shortcut-row"><span className="shortcut-keys">Ctrl+Q</span><span>Quit</span></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ToastProvider>
  );
}

export default App;
