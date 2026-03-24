import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Doctor() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastRun, setLastRun] = useState(null);

  const runCheck = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/api/doctor');
      setReport(data);
      setLastRun(new Date());
    } catch {
      setReport({ status: 'error', checks: [], summary: 'Could not reach backend' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { runCheck(); }, []);

  const statusIcon = (s) => {
    if (s === 'ok') return '✅';
    if (s === 'warn') return '⚠️';
    if (s === 'skip') return '⏭️';
    return '❌';
  };

  const statusClass = (s) => {
    if (s === 'ok') return 'doctor-ok';
    if (s === 'warn') return 'doctor-warn';
    if (s === 'skip') return 'doctor-skip';
    return 'doctor-error';
  };

  const overallStatus = report?.status || 'checking';
  const checks = report?.checks || [];
  const okCount = checks.filter(c => c.status === 'ok').length;
  const warnCount = checks.filter(c => c.status === 'warn').length;
  const errorCount = checks.filter(c => c.status === 'error').length;
  const skipCount = checks.filter(c => c.status === 'skip').length;

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>System Health</h2>
          <p className="doctor-subtitle">
            {lastRun ? `Last checked ${lastRun.toLocaleTimeString()}` : 'Running diagnostics...'}
          </p>
        </div>
        <button className="chat-btn-secondary" onClick={runCheck} disabled={loading}>
          {loading ? 'Checking...' : 'Re-check'}
        </button>
      </div>

      {/* Summary cards */}
      <div className="doctor-summary">
        <div className="doctor-summary-card doctor-ok">
          <div className="doctor-summary-num">{okCount}</div>
          <div className="doctor-summary-label">Healthy</div>
        </div>
        <div className="doctor-summary-card doctor-warn">
          <div className="doctor-summary-num">{warnCount}</div>
          <div className="doctor-summary-label">Warnings</div>
        </div>
        <div className="doctor-summary-card doctor-error">
          <div className="doctor-summary-num">{errorCount}</div>
          <div className="doctor-summary-label">Errors</div>
        </div>
        <div className="doctor-summary-card doctor-skip">
          <div className="doctor-summary-num">{skipCount}</div>
          <div className="doctor-summary-label">Skipped</div>
        </div>
        <div className="doctor-summary-card doctor-total">
          <div className="doctor-summary-num">{checks.length}</div>
          <div className="doctor-summary-label">Total Checks</div>
        </div>
      </div>

      {/* Overall status bar */}
      {!loading && (
        <div className={`doctor-overall ${statusClass(overallStatus)}`}>
          <span className="doctor-overall-icon">
            {overallStatus === 'ok' ? '🟢' : overallStatus === 'warn' ? '🟡' : '🔴'}
          </span>
          <span>
            {overallStatus === 'ok' && 'All systems operational'}
            {overallStatus === 'warn' && 'Some warnings detected — system is functional'}
            {overallStatus === 'error' && 'Issues detected — some features may not work'}
          </span>
        </div>
      )}

      {/* Check list */}
      <div className="doctor-checks">
        {loading && checks.length === 0 ? (
          <div className="doctor-loading">
            <div className="spinner" />
            <p>Running {10} health checks...</p>
          </div>
        ) : (
          checks.map((check, i) => (
            <div key={i} className={`doctor-check ${statusClass(check.status)}`}>
              <div className="doctor-check-icon">{statusIcon(check.status)}</div>
              <div className="doctor-check-body">
                <div className="doctor-check-name">{check.name}</div>
                <div className="doctor-check-message">{check.message}</div>
                {check.version && <span className="doctor-check-detail">v{check.version}</span>}
                {check.free_gb != null && <span className="doctor-check-detail">{check.free_gb} GB free</span>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Doctor;
