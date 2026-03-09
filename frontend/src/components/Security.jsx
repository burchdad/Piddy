import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Security() {
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSecurity = async () => {
      try {
        const response = await fetch('/api/security/audit');
        const data = await response.json();
        setAudit(data);
      } catch (err) {
        console.error('Failed to fetch security audit:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSecurity();
    const interval = setInterval(fetchSecurity, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="page">Loading security audit...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🔒 Security Audit</h1>
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
                  <div key={idx} className="failure-item">{failure}</div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Security;
