import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Metrics() {
  const [metrics, setMetrics] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [metricsResponse, analyticsResponse] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/metrics/performance'),
          fetch('http://127.0.0.1:8000/api/analytics/agent-reputation')
        ]);
        
        const metricsData = await metricsResponse.json();
        const analyticsData = await analyticsResponse.json();
        
        setMetrics(metricsData);
        setAnalytics(analyticsData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    const icons = {
      ok: '✅',
      warning: '⚠️',
      critical: '❌'
    };
    return icons[status] || '❓';
  };

  const getMetricPercentage = (value, threshold) => {
    if (!threshold) return (value / 100) * 100;
    return (value / threshold) * 100;
  };

  return (
    <div className="page metrics">
      <div className="header-section">
        <h2>📊 Performance Metrics</h2>
        <p className="subtitle">Real-time system performance monitoring</p>
      </div>

      {loading ? (
        <div className="loading">Loading metrics...</div>
      ) : (
        <>
          <div className="metrics-section">
            <h3>System Metrics</h3>
            <div className="metrics-grid">
              {metrics.map((metric) => (
                <div key={metric.metric_name} className={`metric-card ${metric.status}`}>
                  <div className="metric-header">
                    <span className="metric-icon">{getStatusIcon(metric.status)}</span>
                    <span className="metric-name">{metric.metric_name}</span>
                  </div>

                  <div className="metric-display">
                    <div className="metric-value">
                      {metric.value.toFixed(1)}<span className="unit">{metric.unit}</span>
                    </div>
                    {metric.threshold && (
                      <div className="metric-threshold">
                        Threshold: {metric.threshold}{metric.unit}
                      </div>
                    )}
                  </div>

                  <div className="metric-bar">
                    <div
                      className="metric-fill"
                      style={{
                        width: `${Math.min(getMetricPercentage(metric.value, metric.threshold), 100)}%`,
                        backgroundColor: metric.status === 'ok' ? '#51cf66' : metric.status === 'warning' ? '#ffa500' : '#ff6b6b'
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {analytics && (
            <div className="analytics-section">
              <h3>Agent Reputation Analytics</h3>
              <div className="reputation-grid">
                {analytics.agents.map((agent) => (
                  <div key={agent.agent_id} className="reputation-card">
                    <div className="agent-name">{agent.agent_id}</div>
                    <div className="agent-role">{agent.role}</div>

                    <div className="reputation-stat">
                      <label>Reputation Score:</label>
                      <div className="score-display">
                        {agent.reputation_score.toFixed(2)}
                        <div className="score-bar">
                          <div className="score-fill" style={{ width: `${(agent.reputation_score / 2) * 100}%` }}></div>
                        </div>
                      </div>
                    </div>

                    <div className="reputation-stat">
                      <label>Success Rate:</label>
                      <div className="rate-display">
                        {agent.success_rate.toFixed(1)}%
                        <div className="rate-bar">
                          <div className="rate-fill" style={{ width: `${agent.success_rate}%` }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Metrics;
