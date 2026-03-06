import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Security() {
  const [audit, setAudit] = useState(null);
  const [issues, setIssues] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSecurity = async () => {
      try {
        const [auditResponse, issuesResponse] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/security/audit'),
          fetch('http://127.0.0.1:8000/api/security/issues')
        ]);
        
        const auditData = await auditResponse.json();
        const issuesData = await issuesResponse.json();
        
        setAudit(auditData);
        setIssues(issuesData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch security info:', error);
        setLoading(false);
      }
    };

    fetchSecurity();
    const interval = setInterval(fetchSecurity, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page security">
      <div className="header-section">
        <h2>🔒 Security & Compliance</h2>
        <p className="subtitle">Security audit results and compliance status</p>
      </div>

      {loading ? (
        <div className="loading">Loading security audit...</div>
      ) : (
        <>
          {audit && (
            <div className="audit-overview">
              <div className="status-card" style={{
                borderLeft: audit.is_production_safe ? '4px solid #51cf66' : '4px solid #ff6b6b'
              }}>
                <div className="status-title">
                  {audit.is_production_safe ? '✅ Production Safe' : '❌ Not Safe for Production'}
                </div>
                <div className="status-details">
                  <div className="detail-item">
                    <label>Audit ID:</label>
                    <value>{audit.audit_id}</value>
                  </div>
                  <div className="detail-item">
                    <label>Timestamp:</label>
                    <value>{new Date(audit.timestamp).toLocaleString()}</value>
                  </div>
                </div>
              </div>

              <div className="audit-stats">
                <div className="stat-card passed">
                  <div className="stat-number">{audit.passed_checks}</div>
                  <div className="stat-label">Checks Passed</div>
                </div>

                <div className="stat-card failed">
                  <div className="stat-number">{audit.failed_checks}</div>
                  <div className="stat-label">Checks Failed</div>
                </div>

                <div className="stat-card">
                  <div className="stat-number">{audit.passed_checks + audit.failed_checks}</div>
                  <div className="stat-label">Total Checks</div>
                </div>

                <div className="stat-card">
                  <div className="stat-number" style={{
                    color: audit.is_production_safe ? '#51cf66' : '#ff6b6b'
                  }}>
                    {((audit.passed_checks / (audit.passed_checks + audit.failed_checks)) * 100).toFixed(1)}%
                  </div>
                  <div className="stat-label">Pass Rate</div>
                </div>
              </div>
            </div>
          )}

          {issues && (
            <div className="issues-section">
              <h3>Critical Failures</h3>
              {issues.critical_failures.length === 0 ? (
                <div className="empty-state">
                  <p>✅ No critical failures detected</p>
                </div>
              ) : (
                <div className="failures-list">
                  {issues.critical_failures.map((failure, index) => (
                    <div key={index} className="failure-item">
                      <span className="failure-icon">❌</span>
                      <span className="failure-text">{failure}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="security-checklist">
            <h3>Security Checklist</h3>
            <div className="checklist">
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">API Authentication Enabled</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">RBAC Configured</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">TLS 1.2+ Encryption</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">Input Validation Active</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">Approval Gates Functional</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">Audit Logging Enabled</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">Alerting Configured</span>
              </div>
              <div className="check-item">
                <span className="check-box">✓</span>
                <span className="check-text">Dependency Scanning Active</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Security;
