import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Security() {
  const [audit, setAudit] = useState(null);
  const [issues, setIssues] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchAll = async () => {
    try {
      const [auditData, issuesData] = await Promise.all([
        fetchApi('/api/security/audit').catch(() => null),
        fetchApi('/api/security/issues').catch(() => null),
      ]);
      let ad = auditData?.audit || auditData;
      if (Array.isArray(ad)) {
        ad = { is_production_safe: true, passed_checks: ad.length, failed_checks: 0, critical_failures: ad };
      }
      if (ad && typeof ad === 'object' && !Array.isArray(ad.critical_failures)) {
        ad.critical_failures = ad.critical_failures ? [ad.critical_failures] : [];
      }
      setAudit(ad || {});
      setIssues(issuesData);
    } catch (err) {
      console.error('Failed to fetch security:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, []);

  const rescan = async () => {
    setScanning(true);
    await fetchAll();
    setScanning(false);
  };

  if (loading) return <div className="page">Loading security audit...</div>;

  const totalChecks = (audit?.passed_checks || 0) + (audit?.failed_checks || 0);
  const score = totalChecks > 0 ? Math.round((audit.passed_checks / totalChecks) * 100) : 0;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🔒 Security Audit</h1>
        <button className="btn-secondary" onClick={rescan} disabled={scanning}>{scanning ? 'Scanning…' : 'Re-scan'}</button>
      </div>

      {/* Score + summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="metric-card">
          <div className="metric-value" style={{ color: score >= 80 ? '#51cf66' : score >= 50 ? '#ffd93d' : '#ff6b6b', fontSize: '2rem' }}>{score}%</div>
          <div className="metric-label">Security Score</div>
        </div>
        <div className="metric-card">
          <div className="metric-value" style={{ color: '#51cf66' }}>{audit?.passed_checks || 0}</div>
          <div className="metric-label">Passed</div>
        </div>
        <div className="metric-card">
          <div className="metric-value" style={{ color: '#ff6b6b' }}>{audit?.failed_checks || 0}</div>
          <div className="metric-label">Failed</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{audit?.is_production_safe ? '✅' : '⚠️'}</div>
          <div className="metric-label">Production</div>
        </div>
      </div>

      {audit && (
        <>
          <div className="security-summary">
            <div className={`security-card ${audit.is_production_safe ? 'safe' : 'unsafe'}`}>
              <div className="security-icon">{audit.is_production_safe ? '✓' : '⚠'}</div>
              <div className="security-title">{audit.is_production_safe ? 'Production Safe' : 'Issues Found'}</div>
              <div className="security-details">
                <div className="detail-row">
                  <span>Passed Checks:</span>
                  <strong>{audit.passed_checks}</strong>
                </div>
                <div className="detail-row">
                  <span>Failed Checks:</span>
                  <strong>{audit.failed_checks}</strong>
                </div>
              </div>
            </div>
          </div>

          {audit.critical_failures && audit.critical_failures.length > 0 && (
            <div className="critical-failures">
              <h3>🚨 Critical Issues</h3>
              <div className="failures-list">
                {audit.critical_failures.map((failure, idx) => (
                  <div key={idx} className="failure-item" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#ff6b6b' }}>●</span>
                    <strong>{typeof failure === 'string' ? failure : (failure.name || failure.description || JSON.stringify(failure))}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          {issues && issues.critical_failures && issues.critical_failures.length === 0 && audit.failed_checks === 0 && (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '3rem' }}>🛡️</div>
              <p>All security checks passed. No vulnerabilities detected.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Security;
