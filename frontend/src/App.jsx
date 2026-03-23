import React, { useState, useEffect } from 'react';
import './styles/App.css';
import './styles/components.css';
import './styles/dashboard.css';
import './styles/setup.css';
import { apiCall } from './utils/api';
import { isBackendReachable } from './utils/api';

// Import components
import Sidebar from './components/Sidebar';
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
import { ToastProvider } from './components/Toast';
import Setup from './components/Setup';

function App() {
  const [activePage, setActivePage] = useState('chat');
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [needsSetup, setNeedsSetup] = useState(null); // null = checking, true/false
  const [backendOnline, setBackendOnline] = useState(null); // null = checking

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
        // If config endpoint fails, skip setup check and show dashboard
        setNeedsSetup(false);
      }
    };
    checkConfig();
  }, []);

  // Fetch system status on mount (only after setup done)
  useEffect(() => {
    if (needsSetup !== false) return; // Wait until setup check is done and keys exist

    const fetchStatus = async (retry = 0, maxRetries = 5) => {
      try {
        setError(null);
        console.log('📡 Fetching system status...');
        
        const data = await apiCall('/api/system/overview');
        console.log('✅ System status fetched:', data);
        
        // Add is_healthy based on status
        setSystemStatus({
          ...data,
          is_healthy: data.status === 'operational'
        });
        setLoading(false);
      } catch (error) {
        console.error(`❌ Attempt ${retry + 1}/${maxRetries + 1} - Failed to fetch system status:`, error.message);
        
        // Retry if we haven't exceeded maxRetries (for connection errors and server errors)
        if (retry < maxRetries) {
          const delayMs = 1000 * (retry + 1); // 1s, 2s, 3s, 4s, 5s
          console.log(`⏳ Retrying in ${delayMs}ms...`);
          setTimeout(() => fetchStatus(retry + 1, maxRetries), delayMs);
          return;
        }
        
        // All retries exhausted - show error but still display page
        setError(error.message);
        setSystemStatus({ is_healthy: false, status: 'offline' });
        setLoading(false);
      }
    };

    fetchStatus();
    // Poll every 30 seconds
    const interval = setInterval(() => fetchStatus(), 30000);
    return () => clearInterval(interval);
  }, [needsSetup]);

  const renderPage = () => {
    switch (activePage) {
      case 'chat':
        return <Chat onOpenSessions={() => setActivePage('sessions')} />;
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
              // Load session into chat
              if (window.__piddyChat) window.__piddyChat.loadSession(sid);
              setActivePage('chat');
            }}
          />
        );
      case 'settings':
        return <Setup mode="settings" backendOnline={backendOnline} onComplete={() => { setNeedsSetup(false); setActivePage('chat'); }} />;
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
      default:
        return <Chat onOpenSessions={() => setActivePage('sessions')} />;
    }
  };

  // Show onboarding if keys not configured
  if (needsSetup === null) {
    // Still checking config status
    return (
      <div className="app" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="loading">
          <div className="spinner"></div>
          <p>Initializing Piddy...</p>
        </div>
      </div>
    );
  }

  if (needsSetup) {
    return <ToastProvider><Setup backendOnline={backendOnline} onComplete={() => setNeedsSetup(false)} /></ToastProvider>;
  }

  return (
    <ToastProvider>
    <div className="app">
      <Sidebar currentPage={activePage} onPageChange={setActivePage} />
      <div className="main-content">
        {backendOnline === false && (
          <div style={{
            background: '#2d2000', borderBottom: '1px solid #665200',
            padding: '0.5rem 1rem', fontSize: '0.85rem', color: '#ffc107',
            display: 'flex', alignItems: 'center', gap: '0.5rem',
          }}>
            <span>&#9888;</span>
            <span>
              <strong>Backend offline.</strong> Start Piddy locally (<code>python piddy.py serve</code>) or use the Desktop app to enable full functionality.
            </span>
          </div>
        )}
        <div className="page-container">
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
    </div>
    </ToastProvider>
  );
}

export default App;
