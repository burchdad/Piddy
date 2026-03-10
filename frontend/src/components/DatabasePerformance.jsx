import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

export function DatabasePerformance() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await fetchApi('/api/autonomous/database/performance');
        setData(result.database || {});
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="page">Loading database metrics...</div>;
  if (error) return <div className="page error-box">Error: {error}</div>;

  const metrics = data || {};

  return (
    <div className="page">
      <div className="section-header">
        <h1>🗄️ Database Performance</h1>
      </div>

      {/* Overall Status */}
      <div className="db-status-cards">
        <div className="db-status-card">
          <div className="status-label">Database Size</div>
          <div className="status-value">{metrics.size_mb?.toFixed(2) || 'N/A'} MB</div>
        </div>
        <div className="db-status-card">
          <div className="status-label">Total Tables</div>
          <div className="status-value">{metrics.table_count || 0}</div>
        </div>
        <div className="db-status-card">
          <div className="status-label">Total Rows</div>
          <div className="status-value">{(metrics.total_rows || 0).toLocaleString()}</div>
        </div>
        <div className="db-status-card">
          <div className="status-label">Health</div>
          <div className="status-value" style={{ color: metrics.health?.status === 'healthy' ? '#51cf66' : '#ff6b6b' }}>
            {metrics.health?.status?.toUpperCase() || 'UNKNOWN'}
          </div>
        </div>
      </div>

      {/* Tables Details */}
      {metrics.tables && metrics.tables.length > 0 && (
        <div className="db-tables-section">
          <h2>📊 Table Statistics</h2>
          <div className="db-tables-grid">
            {metrics.tables.map((table, idx) => (
              <div key={idx} className="db-table-card">
                <div className="table-name">{table.name}</div>
                <div className="table-stats">
                  <div className="stat">
                    <span className="label">Rows:</span>
                    <span className="value">{(table.row_count || 0).toLocaleString()}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Size:</span>
                    <span className="value">{(table.size_mb || 0).toFixed(2)} MB</span>
                  </div>
                  <div className="stat">
                    <span className="label">Indexes:</span>
                    <span className="value">{table.index_count || 0}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Recommendations */}
      {metrics.recommendations && metrics.recommendations.length > 0 && (
        <div className="db-recommendations-section">
          <h2>💡 Optimization Recommendations</h2>
          <div className="recommendations-list">
            {metrics.recommendations.map((rec, idx) => (
              <div key={idx} className={`recommendation-item ${rec.priority || 'info'}`}>
                <div className="rec-header">
                  <span className="rec-title">{rec.title}</span>
                  <span className={`rec-priority ${rec.priority || 'info'}`}>
                    {rec.priority?.toUpperCase() || 'INFO'}
                  </span>
                </div>
                <div className="rec-description">{rec.description}</div>
                {rec.action && (
                  <div className="rec-action">
                    <strong>Recommended Action:</strong> {rec.action}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Query Performance */}
      {metrics.slow_queries && metrics.slow_queries.length > 0 && (
        <div className="db-queries-section">
          <h2>🐌 Slow Queries</h2>
          <div className="queries-list">
            {metrics.slow_queries.map((query, idx) => (
              <div key={idx} className="query-card">
                <div className="query-header">
                  <span className="query-time">{query.duration_ms?.toFixed(2) || 'N/A'} ms</span>
                  <span className="query-count">{query.execution_count || 1}x executed</span>
                </div>
                <div className="query-sql">{query.query}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cache Stats */}
      {metrics.cache_stats && (
        <div className="db-cache-section">
          <h2>⚡ Cache Statistics</h2>
          <div className="cache-stats-grid">
            <div className="cache-stat">
              <div className="stat-label">Hit Rate</div>
              <div className="stat-value">{(metrics.cache_stats.hit_rate || 0).toFixed(1)}%</div>
            </div>
            <div className="cache-stat">
              <div className="stat-label">Total Queries</div>
              <div className="stat-value">{(metrics.cache_stats.total_queries || 0).toLocaleString()}</div>
            </div>
            <div className="cache-stat">
              <div className="stat-label">Cache Hits</div>
              <div className="stat-value">{(metrics.cache_stats.hits || 0).toLocaleString()}</div>
            </div>
            <div className="cache-stat">
              <div className="stat-label">Cache Misses</div>
              <div className="stat-value">{(metrics.cache_stats.misses || 0).toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}

      {/* Backup Info */}
      {metrics.last_backup && (
        <div className="db-backup-section">
          <h2>💾 Backup Status</h2>
          <div className="backup-card">
            <div className="backup-stat">
              <span className="label">Last Backup:</span>
              <span className="value">{new Date(metrics.last_backup).toLocaleString()}</span>
            </div>
            {metrics.backup_size_mb && (
              <div className="backup-stat">
                <span className="label">Backup Size:</span>
                <span className="value">{metrics.backup_size_mb.toFixed(2)} MB</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Timestamps */}
      <div className="db-footer">
        <small>Last updated: {new Date().toLocaleTimeString()}</small>
      </div>
    </div>
  );
}
