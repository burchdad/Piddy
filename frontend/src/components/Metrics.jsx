import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Metrics() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await fetchApi('/api/metrics/performance');
        const metricsArray = Array.isArray(data) ? data : (data.metrics || []);
        setMetrics(metricsArray);
        if (metricsArray.length > 0) setSelectedMetric(metricsArray[0]);
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'ok': return '#51cf66';
      case 'warning': return '#ffd93d';
      case 'critical': return '#ff6b6b';
      default: return '#cbd5e1';
    }
  };

  if (loading) return <div className="page">Loading metrics...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>📈 Performance Metrics</h1>
      </div>

      <div className="metrics-grid">
        {Array.isArray(metrics) && metrics.map((metric) => (
          <div key={metric.metric_name} className="metric-card" style={{ borderLeftColor: getStatusColor(metric.status) }}>
            <div className="metric-header">
              <div className="metric-name">{metric.metric_name}</div>
              <div className={`metric-status ${metric.status}`}>{metric.status.toUpperCase()}</div>
            </div>
            <div className="metric-value">{(metric.value ?? 0).toFixed(2)} {metric.unit}</div>
            {metric.threshold && (
              <div className="metric-threshold">Threshold: {(metric.threshold ?? 0).toFixed(2)}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Metrics;
