import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Scanner() {
  const [tab, setTab] = useState('host');
  const [hostData, setHostData] = useState(null);
  const [repoData, setRepoData] = useState(null);
  const [programsData, setProgramsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [repoPath, setRepoPath] = useState('');
  const [error, setError] = useState(null);

  const scanHost = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiCall('/api/scan/host');
      setHostData(data);
    } catch (e) {
      setError('Could not reach backend');
    } finally {
      setLoading(false);
    }
  };

  const scanRepo = async () => {
    if (!repoPath.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiCall('/api/scan/repo', { method: 'POST', data: { path: repoPath.trim() } });
      setRepoData(data);
    } catch (e) {
      setError('Could not analyze repo');
    } finally {
      setLoading(false);
    }
  };

  const scanPrograms = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiCall('/api/scan/programs');
      setProgramsData(data);
    } catch (e) {
      setError('Could not scan programs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { scanHost(); }, []);

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>Universal Scanner</h2>
          <p className="doctor-subtitle">Scan your host machine, any repo, or installed programs</p>
        </div>
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {[
          { id: 'host', label: '🖥️ Host Machine' },
          { id: 'repo', label: '📂 Repository' },
          { id: 'programs', label: '📋 Programs' },
        ].map(t => (
          <button
            key={t.id}
            className={`chat-btn-secondary ${tab === t.id ? 'active' : ''}`}
            style={tab === t.id ? { background: 'var(--accent)', color: '#fff' } : {}}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && <div className="doctor-summary-card doctor-error" style={{ marginBottom: 16 }}>{error}</div>}

      {/* HOST TAB */}
      {tab === 'host' && (
        <div>
          <button className="chat-btn-secondary" onClick={scanHost} disabled={loading} style={{ marginBottom: 16 }}>
            {loading ? 'Scanning...' : 'Re-scan Host'}
          </button>
          {hostData && (
            <div className="doctor-checks">
              {/* OS Info */}
              <div className="doctor-check doctor-ok">
                <span className="doctor-check-icon">🖥️</span>
                <div className="doctor-check-body">
                  <strong>Operating System</strong>
                  <p>{hostData.os?.platform} {hostData.os?.release} ({hostData.os?.arch})</p>
                  <p style={{ opacity: 0.7, fontSize: 13 }}>Hostname: {hostData.os?.hostname}</p>
                </div>
              </div>
              {/* Hardware */}
              <div className="doctor-check doctor-ok">
                <span className="doctor-check-icon">⚙️</span>
                <div className="doctor-check-body">
                  <strong>Hardware</strong>
                  <p>{hostData.hardware?.cpu_cores} CPU cores — {hostData.hardware?.processor}</p>
                  <p>{hostData.hardware?.ram_gb} GB RAM</p>
                </div>
              </div>
              {/* Network */}
              <div className={`doctor-check ${hostData.network?.internet_available ? 'doctor-ok' : 'doctor-warn'}`}>
                <span className="doctor-check-icon">{hostData.network?.internet_available ? '🌐' : '📴'}</span>
                <div className="doctor-check-body">
                  <strong>Network</strong>
                  <p>{hostData.network?.internet_available ? 'Internet connected' : 'Offline — running in local mode'}</p>
                </div>
              </div>
              {/* Runtimes */}
              {hostData.runtimes && Object.keys(hostData.runtimes).length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">🔧</span>
                  <div className="doctor-check-body">
                    <strong>Detected Runtimes ({Object.keys(hostData.runtimes).length})</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 4, marginTop: 8 }}>
                      {Object.entries(hostData.runtimes).map(([name, info]) => (
                        <span key={name} style={{ fontSize: 13 }}>
                          ✓ <strong>{name}</strong> {(info.version || '').slice(0, 30)}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              {/* Disk */}
              {hostData.disk && hostData.disk.length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">💾</span>
                  <div className="doctor-check-body">
                    <strong>Disk</strong>
                    {hostData.disk.map((d, i) => (
                      <p key={i}>{d.mount} — {d.free_gb} GB free / {d.total_gb} GB total ({d.used_pct}% used)</p>
                    ))}
                  </div>
                </div>
              )}
              {/* Dev Tools */}
              {hostData.installed_tools && hostData.installed_tools.length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">🛠️</span>
                  <div className="doctor-check-body">
                    <strong>Dev Tools ({hostData.installed_tools.length})</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 4, marginTop: 8 }}>
                      {hostData.installed_tools.map(t => (
                        <span key={t.name} style={{ fontSize: 13 }}>✓ {t.name} <span style={{ opacity: 0.6 }}>({t.category})</span></span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* REPO TAB */}
      {tab === 'repo' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <input
              type="text"
              value={repoPath}
              onChange={e => setRepoPath(e.target.value)}
              placeholder="Enter local repo path (e.g. C:\Projects\my-app)"
              style={{ flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)' }}
              onKeyDown={e => e.key === 'Enter' && scanRepo()}
            />
            <button className="chat-btn-secondary" onClick={scanRepo} disabled={loading || !repoPath.trim()}>
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
          {repoData && !repoData.error && (
            <div className="doctor-checks">
              {/* Languages */}
              {repoData.languages && Object.keys(repoData.languages).length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">📝</span>
                  <div className="doctor-check-body">
                    <strong>Languages</strong>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                      {Object.entries(repoData.languages).map(([lang, count]) => (
                        <span key={lang} style={{ padding: '2px 10px', borderRadius: 12, background: 'var(--surface)', fontSize: 13 }}>
                          {lang}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              {/* Git */}
              {repoData.git && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">🔀</span>
                  <div className="doctor-check-body">
                    <strong>Git</strong>
                    <p>Branch: {repoData.git.branch} — Last commit: {repoData.git.last_commit}</p>
                    <p>{repoData.git.clean ? '✅ Clean working tree' : `⚠️ ${repoData.git.uncommitted_changes} uncommitted changes`}</p>
                  </div>
                </div>
              )}
              {/* Dependencies */}
              {repoData.dependencies && Object.keys(repoData.dependencies).length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">📦</span>
                  <div className="doctor-check-body">
                    <strong>Dependencies</strong>
                    <p>Manifests: {Object.keys(repoData.dependencies).join(', ')}</p>
                  </div>
                </div>
              )}
              {/* Issues */}
              {repoData.issues && repoData.issues.length > 0 && (
                <div className="doctor-check doctor-warn">
                  <span className="doctor-check-icon">⚠️</span>
                  <div className="doctor-check-body">
                    <strong>Issues ({repoData.issues.length})</strong>
                    {repoData.issues.map((iss, i) => (
                      <p key={i}>{iss.severity === 'error' ? '❌' : iss.severity === 'warn' ? '⚠️' : 'ℹ️'} {iss.msg}</p>
                    ))}
                  </div>
                </div>
              )}
              {/* Recommendations */}
              {repoData.recommendations && repoData.recommendations.length > 0 && (
                <div className="doctor-check doctor-ok">
                  <span className="doctor-check-icon">💡</span>
                  <div className="doctor-check-body">
                    <strong>Recommendations</strong>
                    {repoData.recommendations.map((r, i) => <p key={i}>💡 {r}</p>)}
                  </div>
                </div>
              )}
            </div>
          )}
          {repoData?.error && (
            <div className="doctor-summary-card doctor-error">{repoData.error}</div>
          )}
        </div>
      )}

      {/* PROGRAMS TAB */}
      {tab === 'programs' && (
        <div>
          <button className="chat-btn-secondary" onClick={scanPrograms} disabled={loading} style={{ marginBottom: 16 }}>
            {loading ? 'Scanning...' : 'Scan Installed Programs'}
          </button>
          {programsData && (
            <div>
              <p style={{ marginBottom: 12, opacity: 0.7 }}>Found {programsData.length} programs</p>
              <div className="doctor-checks">
                {programsData.slice(0, 100).map((p, i) => (
                  <div key={i} className="doctor-check doctor-ok" style={{ padding: '8px 16px' }}>
                    <span className="doctor-check-icon">📦</span>
                    <div className="doctor-check-body">
                      <strong>{p.name}</strong>
                      {p.version && <span style={{ opacity: 0.6, marginLeft: 8, fontSize: 13 }}>v{p.version}</span>}
                    </div>
                  </div>
                ))}
                {programsData.length > 100 && (
                  <p style={{ textAlign: 'center', opacity: 0.5, padding: 16 }}>… and {programsData.length - 100} more</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Scanner;
