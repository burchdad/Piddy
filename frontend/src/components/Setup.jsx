import React, { useState, useEffect } from 'react';

const PROVIDERS = [
  {
    key: 'ANTHROPIC_API_KEY',
    label: 'Anthropic (Claude)',
    placeholder: 'sk-ant-...',
    required: true,
    provider: 'anthropic',
    description: 'Primary AI provider — powers all Piddy agents',
  },
  {
    key: 'OPENAI_API_KEY',
    label: 'OpenAI (GPT)',
    placeholder: 'sk-...',
    required: false,
    provider: 'openai',
    description: 'Optional fallback provider',
  },
  {
    key: 'SLACK_BOT_TOKEN',
    label: 'Slack Bot Token',
    placeholder: 'xoxb-...',
    required: false,
    description: 'Enable Slack /nova commands',
  },
  {
    key: 'GITHUB_TOKEN',
    label: 'GitHub Token',
    placeholder: 'ghp_...',
    required: false,
    description: 'PR creation, code review integration',
  },
];

function SettingsPanel({ apiUrl }) {
  const [settings, setSettings] = useState(null);
  const [models, setModels] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const base = apiUrl || '';

  useEffect(() => {
    fetch(`${base}/api/settings`).then(r => r.json()).then(setSettings).catch(() => {});
    fetch(`${base}/api/settings/ollama-models`).then(r => r.json()).then(d => setModels(d.models || [])).catch(() => {});
  }, [base]);

  const update = (key, val) => { setSettings(s => ({ ...s, [key]: val })); setSaved(false); };

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${base}/api/settings`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(settings) });
      setSaved(true);
    } catch { /* silently fail */ }
    setSaving(false);
  };

  if (!settings) return <p style={{ color: 'var(--text-secondary)' }}>Loading settings…</p>;

  return (
    <div>
      <div className="settings-section">
        <h3>🌐 Network</h3>
        <div className="setting-row">
          <div><div className="setting-label">Local-Only Mode</div><div className="setting-desc">When enabled, never call cloud APIs — Ollama only</div></div>
          <label className="toggle"><input type="checkbox" checked={settings.local_only} onChange={e => update('local_only', e.target.checked)} /><span className="toggle-slider"></span></label>
        </div>
      </div>

      <div className="settings-section">
        <h3>🦙 Ollama (Local LLM)</h3>
        <div className="setting-row">
          <div><div className="setting-label">Enabled</div></div>
          <label className="toggle"><input type="checkbox" checked={settings.ollama_enabled} onChange={e => update('ollama_enabled', e.target.checked)} /><span className="toggle-slider"></span></label>
        </div>
        <div className="setting-row">
          <div><div className="setting-label">Model</div><div className="setting-desc">Available on your Ollama instance</div></div>
          <select className="select-input" value={settings.ollama_model} onChange={e => update('ollama_model', e.target.value)}>
            {models.length === 0 && <option value={settings.ollama_model}>{settings.ollama_model}</option>}
            {models.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div className="setting-row">
          <div><div className="setting-label">Base URL</div></div>
          <input type="text" className="select-input" style={{ width: 200 }} value={settings.ollama_base_url} onChange={e => update('ollama_base_url', e.target.value)} />
        </div>
      </div>

      <div className="settings-section">
        <h3>🤖 Agent Configuration</h3>
        <div className="setting-row">
          <div><div className="setting-label">Temperature: {settings.agent_temperature}</div><div className="setting-desc">Higher = more creative, lower = more precise</div></div>
          <input type="range" className="range-input" min="0" max="1" step="0.1" value={settings.agent_temperature} onChange={e => update('agent_temperature', parseFloat(e.target.value))} />
        </div>
        <div className="setting-row">
          <div><div className="setting-label">Max Tokens</div></div>
          <input type="number" className="select-input" style={{ width: 100 }} value={settings.agent_max_tokens} onChange={e => update('agent_max_tokens', parseInt(e.target.value) || 4096)} />
        </div>
        <div className="setting-row">
          <div><div className="setting-label">Cloud Model</div></div>
          <select className="select-input" value={settings.agent_model} onChange={e => update('agent_model', e.target.value)}>
            <option value="claude-opus-4-1-20250805">claude-opus-4-1-20250805</option>
            <option value="claude-sonnet-4-20250514">claude-sonnet-4-20250514</option>
            <option value="gpt-4o">gpt-4o</option>
          </select>
        </div>
      </div>

      <button className="btn-primary" disabled={saving} onClick={handleSave} style={{ marginTop: '0.5rem' }}>
        {saving ? 'Saving…' : saved ? '✓ Saved' : 'Save Settings'}
      </button>
    </div>
  );
}

export default function Setup({ apiUrl, onComplete, mode }) {
  const [values, setValues] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // If onComplete is provided but we're accessed via sidebar (not the blocking overlay)
  // we show a full settings page with keys + config
  const isSettingsPage = !document.querySelector('.setup-overlay') || false;

  const handleChange = (key, val) => {
    setValues(prev => ({ ...prev, [key]: val }));
    setTestResults(prev => { const n = { ...prev }; delete n[key]; return n; });
  };

  const testKey = async (provider, key, value) => {
    if (!value?.trim()) return;
    setTesting(prev => ({ ...prev, [key]: true }));
    try {
      const url = apiUrl ? `${apiUrl}/api/config/test` : '/api/config/test';
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, key: value }),
      });
      const data = await resp.json();
      setTestResults(prev => ({ ...prev, [key]: data }));
    } catch {
      setTestResults(prev => ({ ...prev, [key]: { valid: false, error: 'Network error' } }));
    } finally {
      setTesting(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleSave = async () => {
    if (!values.ANTHROPIC_API_KEY?.trim()) {
      setError('Anthropic API key is required to run Piddy.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const url = apiUrl ? `${apiUrl}/api/config/save` : '/api/config/save';
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await resp.json();
      if (data.status === 'saved' || data.configured) {
        onComplete();
      } else {
        setError('Keys saved but minimum configuration not met. Please add an Anthropic key.');
      }
    } catch (e) {
      setError(`Failed to save — is the backend running? (${e.message})`);
    } finally {
      setSaving(false);
    }
  };

  const canSave = values.ANTHROPIC_API_KEY?.trim();

  // Render the key-entry card (used in both overlay and settings page)
  const keysCard = (
    <>
      <div className="setup-fields">
        {PROVIDERS.map(p => (
          <div key={p.key} className="setup-field">
            <label>
              {p.label}
              {p.required && <span className="required-badge">Required</span>}
              {!p.required && <span className="optional-badge">Optional</span>}
            </label>
            <p className="field-desc">{p.description}</p>
            <div className="field-row">
              <input
                type="password"
                placeholder={p.placeholder}
                value={values[p.key] || ''}
                onChange={e => handleChange(p.key, e.target.value)}
                className={testResults[p.key]?.valid === true ? 'input-valid' : testResults[p.key]?.valid === false ? 'input-invalid' : ''}
              />
              {p.provider && (
                <button
                  className="test-btn"
                  disabled={!values[p.key]?.trim() || testing[p.key]}
                  onClick={() => testKey(p.provider, p.key, values[p.key])}
                >
                  {testing[p.key] ? '...' : 'Test'}
                </button>
              )}
            </div>
            {testResults[p.key] && (
              <span className={`test-result ${testResults[p.key].valid ? 'valid' : 'invalid'}`}>
                {testResults[p.key].valid ? '✓ Valid' : `✗ ${testResults[p.key].error || 'Invalid'}`}
              </span>
            )}
          </div>
        ))}
      </div>
      {error && <div className="setup-error">{error}</div>}
      <div className="setup-actions">
        <button className="save-btn" disabled={!canSave || saving} onClick={handleSave}>
          {saving ? 'Saving...' : 'Save & Launch Piddy'}
        </button>
      </div>
      <p className="setup-footer">🔐 Keys are Fernet-encrypted at rest in <code>config/keys.enc</code></p>
    </>
  );

  // Settings page (sidebar navigation)
  if (mode === 'settings') {
    return (
      <div className="page">
        <div className="section-header"><h1>⚙️ Settings</h1></div>
        <div className="settings-section">
          <h3>🔑 API Keys</h3>
          {keysCard}
        </div>
        <SettingsPanel apiUrl={apiUrl} />
      </div>
    );
  }

  // Full-page onboarding wizard (first-run)
  return <OnboardingWizard apiUrl={apiUrl} keysCard={keysCard} onComplete={onComplete} />;
}

function OnboardingWizard({ apiUrl, keysCard, onComplete }) {
  const [step, setStep] = useState(0);
  const [checks, setChecks] = useState(null);
  const base = apiUrl || '';

  const runChecks = async () => {
    try {
      const resp = await fetch(`${base}/api/doctor`);
      const data = await resp.json();
      setChecks(data);
    } catch {
      setChecks({ checks: [], summary: { ok: 0, warnings: 0, errors: 0 } });
    }
  };

  useEffect(() => { if (step === 1) runChecks(); }, [step]);

  const steps = [
    { title: 'API Keys', icon: '🔑' },
    { title: 'System Check', icon: '🩺' },
    { title: 'Ready!', icon: '🚀' },
  ];

  return (
    <div className="setup-overlay">
      <div className="setup-card" style={{ maxWidth: 560 }}>
        {/* Step indicators */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '1.5rem' }}>
          {steps.map((s, i) => (
            <div key={i} style={{ textAlign: 'center', opacity: i <= step ? 1 : 0.4 }}>
              <div style={{ fontSize: '1.5rem' }}>{s.icon}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{s.title}</div>
            </div>
          ))}
        </div>

        {step === 0 && (
          <>
            <div className="setup-header">
              <div className="setup-logo">🎯</div>
              <h1>Welcome to Piddy</h1>
              <p className="setup-subtitle">AI Backend Developer Agent</p>
              <p className="setup-desc">Configure your API keys to get started. Keys are encrypted and stored locally.</p>
            </div>
            {keysCard}
            <button className="btn-secondary" style={{ marginTop: '0.5rem', width: '100%' }} onClick={() => setStep(1)}>
              Skip — I'll configure later →
            </button>
          </>
        )}

        {step === 1 && (
          <>
            <h2 style={{ margin: 0, color: 'var(--text-primary)' }}>🩺 System Health Check</h2>
            <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 1rem' }}>Verifying your Piddy installation…</p>
            {!checks ? (
              <p style={{ color: 'var(--text-secondary)' }}>Running checks…</p>
            ) : (
              <div style={{ maxHeight: 280, overflow: 'auto' }}>
                {checks.checks?.map((c, i) => (
                  <div key={i} style={{ display: 'flex', gap: '0.5rem', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                    <span>{c.status === 'ok' ? '✅' : c.status === 'warn' ? '⚠️' : '❌'}</span>
                    <span style={{ color: 'var(--text-primary)', flex: 1 }}>{c.name}</span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{c.message || c.version || ''}</span>
                  </div>
                ))}
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.75rem' }}>
                  {checks.summary?.ok || 0} OK · {checks.summary?.warnings || 0} Warnings · {checks.summary?.errors || 0} Errors
                </p>
              </div>
            )}
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
              <button className="btn-secondary" style={{ flex: 1 }} onClick={() => setStep(0)}>← Back</button>
              <button className="btn-primary" style={{ flex: 1 }} onClick={() => setStep(2)}>Next →</button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
              <div style={{ fontSize: '3rem' }}>🎉</div>
              <h2 style={{ color: 'var(--text-primary)', margin: '0.5rem 0' }}>You're All Set!</h2>
              <p style={{ color: 'var(--text-secondary)' }}>Here's what Piddy can do:</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', margin: '1rem 0' }}>
              {[
                { icon: '💬', text: 'Chat with AI agents' },
                { icon: '🤖', text: '21 specialized agents' },
                { icon: '⚡', text: '56 built-in skills' },
                { icon: '📚', text: 'Knowledge library' },
                { icon: '🩺', text: 'Self-diagnosis' },
                { icon: '🔒', text: 'Security monitoring' },
              ].map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                  <span>{f.icon}</span><span>{f.text}</span>
                </div>
              ))}
            </div>
            <button className="btn-primary" style={{ width: '100%', marginTop: '0.75rem' }} onClick={onComplete}>
              Launch Piddy 🚀
            </button>
          </>
        )}
      </div>
    </div>
  );
}
