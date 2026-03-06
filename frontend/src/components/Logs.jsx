import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/logs?limit=100');
        const data = await response.json();
        setLogs(data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch logs:', error);
        setLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(l => l.level === filter);

  const levels = [...new Set(logs.map(l => l.level))];

  const getLevelIcon = (level) => {
    const icons = {
      INFO: 'ℹ️',
      WARNING: '⚠️',
      ERROR: '❌',
      DEBUG: '🐛'
    };
    return icons[level] || '📝';
  };

  const getLevelColor = (level) => {
    const colors = {
      INFO: '#4dabf7',
      WARNING: '#ffa500',
      ERROR: '#ff6b6b',
      DEBUG: '#9c36b5'
    };
    return colors[level] || '#333';
  };

  return (
    <div className="page logs">
      <div className="header-section">
        <h2>📋 System Logs</h2>
        <p className="subtitle">Real-time system and component logging</p>
      </div>

      <div className="controls">
        <div className="filter-group">
          <label>Filter by Level:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Levels</option>
            {levels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>
        <p className="log-count">Total: {filteredLogs.length} entries</p>
      </div>

      {loading ? (
        <div className="loading">Loading logs...</div>
      ) : (
        <div className="log-viewer">
          {filteredLogs.map((log, index) => (
            <div key={index} className="log-entry">
              <div className="log-header">
                <span className="log-level" style={{ color: getLevelColor(log.level) }}>
                  {getLevelIcon(log.level)} {log.level}
                </span>
                <span className="log-source">{log.source}</span>
                <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
              </div>
              <div className="log-message">{log.message}</div>
              {log.details && (
                <div className="log-details">
                  <pre>{JSON.stringify(log.details, null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="log-summary">
        <h3>Log Summary</h3>
        <div className="summary-grid">
          {levels.map(level => (
            <div key={level} className="summary-item">
              <span className="level-icon" style={{ color: getLevelColor(level) }}>
                {getLevelIcon(level)} {level}
              </span>
              <span className="count">{logs.filter(l => l.level === level).length}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Logs;
