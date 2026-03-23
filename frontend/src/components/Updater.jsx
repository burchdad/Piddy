import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Updater() {
  const [checkResult, setCheckResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applyResult, setApplyResult] = useState(null);
  const [platformInfo, setPlatformInfo] = useState(null);

  const checkUpdates = async () => {
    setLoading(true);
    setApplyResult(null);
    try {
      const data = await apiCall('/api/update/check');
      setCheckResult(data);
    } catch {
      setCheckResult({ error: 'Could not reach backend' });
    } finally {
      setLoading(false);
    }
  };

  const applyUpdate = async () => {
    if (!window.confirm('Apply the update? Piddy will pull the latest code from GitHub.')) return;
    setApplying(true);
    try {
      const data = await apiCall('/api/update/apply', { method: 'POST' });
      setApplyResult(data);
      if (data.success) checkUpdates();
    } catch {
      setApplyResult({ error: 'Update failed' });
    } finally {
      setApplying(false);
    }
  };

  const loadPlatform = async () => {
    try {
      const data = await apiCall('/api/platform');
      setPlatformInfo(data);
    } catch { /* ignore */ }
  };

  useEffect(() => { checkUpdates(); loadPlatform(); }, []);

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>Updates & Platform</h2>
          <p className="doctor-subtitle">Auto-update from GitHub and cross-platform runtime detection</p>
        </div>
        <button className="chat-btn-secondary" onClick={checkUpdates} disabled={loading}>
          {loading ? 'Checking...' : 'Check for Updates'}
        </button>
      </div>

      {/* Update status */}
      <div className="doctor-checks">
        {checkResult && (
          <div className={`doctor-check ${checkResult.available ? 'doctor-warn' : checkResult.error ? 'doctor-error' : 'doctor-ok'}`}>
            <span className="doctor-check-icon">{checkResult.available ? '📦' : checkResult.error ? '❌' : '✅'}</span>
            <div className="doctor-check-body">
              <strong>{checkResult.available ? 'Update Available' : checkResult.error ? 'Error' : 'Up to Date'}</strong>
              <p>Current version: <strong>{checkResult.current_version || '?'}</strong></p>
              {checkResult.latest_version && <p>Latest: <strong>{checkResult.latest_version}</strong></p>}
              {checkResult.remote_sha && <p>Remote commit: <code>{checkResult.remote_sha}</code> (local: <code>{checkResult.local_sha}</code>)</p>}
              <p style={{ opacity: 0.7, fontSize: 13 }}>{checkResult.message || checkResult.error}</p>
              {checkResult.available && (
                <button
                  className="chat-btn-secondary"
                  style={{ marginTop: 12, background: 'var(--accent)', color: '#fff' }}
                  onClick={applyUpdate}
                  disabled={applying}
                >
                  {applying ? 'Applying...' : '⬇️ Install Update'}
                </button>
              )}
            </div>
          </div>
        )}

        {applyResult && (
          <div className={`doctor-check ${applyResult.success ? 'doctor-ok' : 'doctor-error'}`}>
            <span className="doctor-check-icon">{applyResult.success ? '✅' : '❌'}</span>
            <div className="doctor-check-body">
              <strong>{applyResult.success ? 'Update Applied' : 'Update Failed'}</strong>
              <p>{applyResult.message || applyResult.error}</p>
              {applyResult.new_version && <p>New version: {applyResult.new_version}</p>}
            </div>
          </div>
        )}

        {!checkResult?.internet && checkResult && !checkResult.error && (
          <div className="doctor-check doctor-warn">
            <span className="doctor-check-icon">📴</span>
            <div className="doctor-check-body">
              <strong>Offline Mode</strong>
              <p>No internet connection detected. Piddy is running fully offline with local runtimes and Ollama.</p>
            </div>
          </div>
        )}
      </div>

      {/* Platform info */}
      {platformInfo && (
        <>
          <h3 style={{ marginTop: 32, marginBottom: 12 }}>Cross-Platform Runtime Detection</h3>
          <div className="doctor-checks">
            <div className="doctor-check doctor-ok">
              <span className="doctor-check-icon">🖥️</span>
              <div className="doctor-check-body">
                <strong>Platform</strong>
                <p>{platformInfo.os} ({platformInfo.arch}) — {platformInfo.machine}</p>
                <p style={{ opacity: 0.7, fontSize: 13 }}>Hostname: {platformInfo.hostname} | Tag: {platformInfo.platform_tag}</p>
              </div>
            </div>
            {['python', 'node', 'ollama'].map(rt => {
              const info = platformInfo[rt];
              if (!info) return null;
              const found = !!info.path;
              return (
                <div key={rt} className={`doctor-check ${found ? 'doctor-ok' : 'doctor-warn'}`}>
                  <span className="doctor-check-icon">{found ? '✅' : '⚠️'}</span>
                  <div className="doctor-check-body">
                    <strong>{rt.charAt(0).toUpperCase() + rt.slice(1)}</strong>
                    {found ? (
                      <>
                        <p>{info.version || 'Detected'}</p>
                        <p style={{ opacity: 0.6, fontSize: 13 }}>{info.embedded ? '📦 Embedded' : '🌐 System'} — {info.path}</p>
                      </>
                    ) : (
                      <p style={{ opacity: 0.7 }}>Not found</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default Updater;
