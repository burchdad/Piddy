import React, { useState, useEffect } from 'react';
import './App.css';

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
import Decisions from './components/Decisions';
import Missions from './components/Missions';
import DependencyGraph from './components/DependencyGraph';
import MissionReplay from './components/MissionReplay';

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch system status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/system/overview');
        const data = await response.json();
        setSystemStatus(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
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
      case 'decisions':
        return <Decisions />;
      case 'missions':
        return <Missions />;
      case 'dependencies':
        return <DependencyGraph />;
      case 'replay':
        return <MissionReplay />;
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
          </div>
        </div>
        {loading ? <div className="loading">Loading...</div> : renderPage()}
      </div>
    </div>
  );
}

export default App;
