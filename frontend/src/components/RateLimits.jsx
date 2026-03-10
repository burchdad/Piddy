import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';

export function RateLimits() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await fetchApi('/api/rate-limits/dashboard');
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  if (loading) return <div className="loading">Loading rate limit data...</div>;

  return (
    <div className="rate-limits-container">
      <div className="section-header">
        <h1>🚦 Rate Limit Monitoring</h1>
        <div className="header-controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto Refresh
          </label>
          <span className="last-updated">
            Last updated: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
          </span>
        </div>
      </div>

      {error && <div className="error-box">Error: {error}</div>}

      {/* Overall Health Status */}
      <div className="health-card status-card">
        <h2>System Health</h2>
        <div className="health-status">
          <div className={`status-indicator ${data?.health?.status?.toLowerCase() || 'unknown'}`}>
            {data?.health?.status?.toUpperCase() || 'UNKNOWN'}
          </div>
          <div className="health-details">
            <p>Providers Available: <strong>{data?.health?.healthy_providers}/{data?.health?.total_providers}</strong></p>
            <p>Queue Length: <strong>{data?.queue_length} requests</strong></p>
          </div>
        </div>
      </div>

      {/* Provider Status Grid */}
      <div className="providers-grid">
        <h2>Provider Status</h2>
        <div className="grid">
          {data?.providers && Object.entries(data.providers).map(([name, metrics]) => (
            <div key={name} className={`provider-card ${getProviderStatusClass(metrics)}`}>
              <div className="provider-name">
                <span className={`status-dot ${getStatusDot(metrics)}`}></span>
                <span>{formatProviderName(name)}</span>
              </div>
              
              <div className="provider-metrics">
                <div className="metric">
                  <span className="label">Throughput:</span>
                  <span className="value">{metrics.throughput_per_min?.toFixed(1) || 0}/min</span>
                </div>
                
                <div className="metric">
                  <span className="label">Success Rate:</span>
                  <span className={`value ${metrics.success_rate < 90 ? 'warning' : ''}`}>
                    {metrics.success_rate?.toFixed(1) || 0}%
                  </span>
                </div>
                
                <div className="metric">
                  <span className="label">Errors:</span>
                  <span className="value">{metrics.total_errors || 0}</span>
                </div>

                {metrics.is_rate_limited && (
                  <div className="metric alert">
                    <span className="label">Rate Limited:</span>
                    <span className="value">{metrics.time_until_available?.toFixed(1)}s</span>
                  </div>
                )}

                {metrics.is_in_recovery && (
                  <div className="metric warning">
                    <span className="label">⚠️ Recovery Mode</span>
                  </div>
                )}
              </div>

              {metrics.last_error && (
                <div className="last-error">
                  <strong>Last Error:</strong> {metrics.last_error}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {data?.recommendations && data.recommendations.length > 0 && (
        <div className="recommendations-card">
          <h2>📋 Recommendations</h2>
          <div className="recommendations-list">
            {data.recommendations.map((rec, idx) => (
              <div key={idx} className={`recommendation ${rec.severity}`}>
                <div className="recommendation-header">
                  <span className={`severity-badge ${rec.severity}`}>{rec.severity.toUpperCase()}</span>
                  <span className="provider">{rec.provider}</span>
                </div>
                <p className="message">{rec.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Configuration */}
      <div className="config-card">
        <h2>⚙️ Configuration</h2>
        <div className="config-grid">
          <div className="config-item">
            <span className="label">Requests/Minute:</span>
            <span className="value">{data?.config?.requests_per_minute || 'N/A'}</span>
          </div>
          <div className="config-item">
            <span className="label">Requests/Hour:</span>
            <span className="value">{data?.config?.requests_per_hour || 'N/A'}</span>
          </div>
          <div className="config-item">
            <span className="label">Initial Backoff:</span>
            <span className="value">{data?.config?.initial_backoff_seconds || 'N/A'}s</span>
          </div>
          <div className="config-item">
            <span className="label">Max Backoff:</span>
            <span className="value">{data?.config?.max_backoff_seconds || 'N/A'}s</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatProviderName(name) {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getProviderStatusClass(metrics) {
  if (metrics.is_rate_limited) return 'rate-limited';
  if (metrics.is_in_recovery) return 'recovering';
  if (metrics.success_rate < 90) return 'warning';
  return 'healthy';
}

function getStatusDot(metrics) {
  if (metrics.is_rate_limited) return 'rate-limited';
  if (metrics.is_in_recovery) return 'recovering';
  if (metrics.success_rate < 90) return 'warning';
  return 'healthy';
}
