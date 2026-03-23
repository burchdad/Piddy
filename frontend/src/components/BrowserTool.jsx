import React, { useState } from 'react';
import { apiCall } from '../utils/api';

function BrowserTool() {
  const [status, setStatus] = useState({ running: false, library_installed: false, current_url: null });
  const [url, setUrl] = useState('');
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [screenshot, setScreenshot] = useState(null);

  const refresh = async () => {
    try {
      const data = await apiCall('/api/browser/status');
      setStatus(data);
    } catch {
      setError('Could not reach backend');
    }
  };

  useState(() => { refresh(); });

  const doAction = async (action, params = {}) => {
    setLoading(true);
    setError(null);
    setOutput(null);
    setScreenshot(null);
    try {
      const data = await apiCall(`/api/browser/${action}`, { method: 'POST', data: params });
      if (data.data_base64) {
        setScreenshot(data.data_base64);
      } else {
        setOutput(data);
      }
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="doctor-page">
      <div className="doctor-header">
        <div>
          <h2>Browser Automation</h2>
          <p className="doctor-subtitle">Navigate, screenshot, and extract content from any webpage</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {!status.running ? (
            <button className="action-btn" onClick={() => doAction('launch')} disabled={loading}>
              ▶ Launch Browser
            </button>
          ) : (
            <button className="action-btn" onClick={() => doAction('close')} disabled={loading} style={{ background: '#dc2626' }}>
              ■ Close Browser
            </button>
          )}
        </div>
      </div>

      {!status.library_installed && (
        <div style={{ margin: '12px 0', padding: 12, background: '#2a1a0a', border: '1px solid #f59e0b', borderRadius: 8, color: '#f59e0b', fontSize: 14 }}>
          ⚠ Playwright not installed. Run: <code>pip install playwright && python -m playwright install chromium</code>
        </div>
      )}

      {error && <div style={{ margin: '12px 0', padding: 10, background: '#2a1a1a', border: '1px solid #ff6b6b', borderRadius: 8, color: '#ff6b6b' }}>{error}</div>}

      {status.running && (
        <>
          {status.current_url && (
            <p style={{ fontSize: 13, opacity: 0.7, margin: '8px 0' }}>Current URL: {status.current_url}</p>
          )}

          <div style={{ display: 'flex', gap: 8, margin: '16px 0' }}>
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://example.com"
              style={{ flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border, #333)', background: 'var(--input-bg, #0d0d1a)', color: 'inherit', fontSize: 14 }}
              onKeyDown={e => e.key === 'Enter' && url && doAction('action', { action: 'navigate', url })}
            />
            <button className="action-btn" onClick={() => doAction('action', { action: 'navigate', url })} disabled={!url || loading}>
              Go
            </button>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
            <button className="action-btn" onClick={() => doAction('action', { action: 'screenshot' })} disabled={loading}>📸 Screenshot</button>
            <button className="action-btn" onClick={() => doAction('action', { action: 'extract_text' })} disabled={loading}>📄 Extract Text</button>
            <button className="action-btn" onClick={() => doAction('action', { action: 'extract_links' })} disabled={loading}>🔗 Extract Links</button>
          </div>
        </>
      )}

      {loading && <p style={{ opacity: 0.6 }}>Working…</p>}

      {screenshot && (
        <div style={{ margin: '16px 0' }}>
          <h3>Screenshot</h3>
          <img src={`data:image/png;base64,${screenshot}`} alt="Browser screenshot" style={{ maxWidth: '100%', borderRadius: 8, border: '1px solid var(--border, #333)' }} />
        </div>
      )}

      {output && (
        <div style={{ margin: '16px 0' }}>
          <h3>Result</h3>
          <pre style={{ background: 'var(--card-bg, #1a1a2e)', padding: 16, borderRadius: 8, overflow: 'auto', maxHeight: 400, fontSize: 13, whiteSpace: 'pre-wrap' }}>
            {typeof output === 'string' ? output : JSON.stringify(output, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default BrowserTool;
