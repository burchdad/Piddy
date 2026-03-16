import React, { useState, useEffect } from 'react';
import './styles/App.css';
import './styles/components.css';

// Import components
import Sidebar from './components/Sidebar';
import Overview from './components/Overview';
import Agents from './components/Agents';
import Messages from './components/Messages';
import Logs from './components/Logs';
import Tests from './components/Tests';
import Metrics from './components/Metrics';
import Phases from './components/Phases';
import Security from './components/Security';
import { RateLimits } from './components/RateLimits';
import Decisions from './components/Decisions';
import Missions from './components/Missions';
import DependencyGraph from './components/DependencyGraph';
import MissionReplay from './components/MissionReplay';
import { DatabasePerformance } from './components/DatabasePerformance';
import Approvals from './components/Approvals';

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch system status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setError(null);
        
        // Get API URL - check if running in Electron, otherwise use env var or relative path
        let apiUrl = '';
        if (window.piddy && window.piddy.backendUrl) {
          // Running in Electron desktop app
          apiUrl = window.piddy.backendUrl;
          console.log('🖥️ Using Electron backend URL:', apiUrl);
        } else {
          // Running in browser or vite dev server
          apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          console.log('🌐 Using web backend URL:', apiUrl);
        }
        
        const url = `${apiUrl}/api/system/overview`;
        console.log('📡 Fetching status from:', url);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ System status fetched:', data);
        
        // Add is_healthy based on status
        setSystemStatus({
          ...data,
          is_healthy: data.status === 'operational'
        });
        setLoading(false);
      } catch (error) {
        console.error('❌ Failed to fetch system status:', error);
        setError(error.message);
        // Still show the page even if fetch fails
        setSystemStatus({ is_healthy: false, status: 'offline' });
        setLoading(false);
      }
    };

    fetchStatus();
    // Poll every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview systemStatus={systemStatus} />;
      case 'agents':
        return <Agents />;
      case 'messages':
        return <Messages />;
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
      case 'rate-limits':
        return <RateLimits />;
      case 'decisions':
        return <Decisions />;
      case 'missions':
        return <Missions />;
      case 'dependencies':
        return <DependencyGraph />;
      case 'replay':
        return <MissionReplay />;
      case 'database':
        return <DatabasePerformance />;
      case 'approvals':
        return <Approvals />;
      default:
        return <Overview systemStatus={systemStatus} />;
    }
  };

  return (
    <div className="app">
      <Sidebar currentPage={activePage} onPageChange={setActivePage} />
      <div className="main-content">
        <div className="header">
          <h1>🎯 Piddy Dashboard</h1>
          <div className="status-indicator">
            {systemStatus?.is_healthy ? (
              <span className="status-healthy">● System Healthy</span>
            ) : (
              <span className="status-warning">● System Warning</span>
            )}
            {error && <span className="status-error"> Error: {error}</span>}
          </div>
        </div>
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
  );
}

export default App;
