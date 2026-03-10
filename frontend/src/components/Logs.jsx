import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await fetchApi('/api/logs?limit=100');
        // Handle both array and object responses
        setLogs(Array.isArray(data) ? data : (data.logs || []));
      } catch (err) {
        console.error('Failed to fetch logs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = (Array.isArray(logs) ? logs : [])
    .filter(log => filter === 'all' || log.level === filter)
    .filter(log => searchTerm === '' || log.message.toLowerCase().includes(searchTerm.toLowerCase()));

  const getLevelColor = (level) => {
    switch(level) {
      case 'INFO': return '#4299e1';
      case 'WARNING': return '#ffd93d';
      case 'ERROR': return '#ff6b6b';
      case 'DEBUG': return '#cbd5e1';
      default: return '#cbd5e1';
    }
  };

  const getLevelIcon = (level) => {
    switch(level) {
      case 'INFO': return 'ℹ';
      case 'WARNING': return '⚠';
      case 'ERROR': return '✕';
      case 'DEBUG': return '🐛';
      default: return '•';
    }
  };

  if (loading) return <div className="page">Loading logs...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>📝 System Logs</h1>
      </div>

      <div className="log-controls">
        <input
          type="text"
          placeholder="Search logs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <div className="log-filters">
          <button className={`filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>All</button>
          <button className={`filter-btn ${filter === 'INFO' ? 'active' : ''}`} onClick={() => setFilter('INFO')}>Info</button>
          <button className={`filter-btn ${filter === 'WARNING' ? 'active' : ''}`} onClick={() => setFilter('WARNING')}>Warning</button>
          <button className={`filter-btn ${filter === 'ERROR' ? 'active' : ''}`} onClick={() => setFilter('ERROR')}>Error</button>
          <button className={`filter-btn ${filter === 'DEBUG' ? 'active' : ''}`} onClick={() => setFilter('DEBUG')}>Debug</button>
        </div>
      </div>

      <div className="logs-container">
        {Array.isArray(filteredLogs) && filteredLogs.map((log, idx) => (
          <div key={idx} className="log-entry" style={{borderLeftColor: getLevelColor(log.level)}}>
            <div className="log-level" style={{backgroundColor: getLevelColor(log.level)}}>
              {getLevelIcon(log.level)}
            </div>
            <div className="log-content">
              <div className="log-header">
                <span className="log-source">{log.source}</span>
                <span className="log-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="log-message">{log.message}</div>
              {log.details && <div className="log-details">{JSON.stringify(log.details, null, 2)}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Logs;
