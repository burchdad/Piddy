import React, { useState, useEffect, useRef } from 'react';
import '../styles/codepanel.css';

/**
 * VS Code-style Code Panel — shows files being created by Piddy in real time.
 * Tabs at the top, syntax-highlighted code in the center, minimap gutter.
 */

// ─── File icon mapping ───
const EXT_ICONS = {
  py: '🐍', js: '📜', jsx: '⚛️', ts: '🔷', tsx: '⚛️',
  java: '☕', c: '🔵', cpp: '🔵', go: '🔹', rs: '🦀',
  rb: '💎', php: '🐘', html: '🌐', css: '🎨', scss: '🎨',
  json: '📋', yaml: '📄', yml: '📄', md: '📝', txt: '📄',
  sh: '⬛', bat: '⬛', sql: '🗃️', toml: '📄', dockerfile: '🐳',
};

const LANG_MAP = {
  py: 'python', js: 'javascript', jsx: 'javascript', ts: 'typescript',
  tsx: 'typescript', html: 'html', css: 'css', scss: 'css', json: 'json',
  md: 'markdown', sh: 'bash', bat: 'bash', sql: 'sql', yml: 'yaml',
  yaml: 'yaml', xml: 'html', rs: 'rust', go: 'go', rb: 'ruby',
  java: 'java', cpp: 'cpp', c: 'c', php: 'php', toml: 'toml',
};

function getIcon(filename) {
  const lower = filename.toLowerCase();
  if (lower === 'dockerfile') return '🐳';
  if (lower === 'makefile') return '⚙️';
  if (lower === 'readme.md') return '📖';
  if (lower === 'requirements.txt') return '📦';
  if (lower === 'package.json') return '📦';
  const ext = filename.includes('.') ? filename.split('.').pop() : '';
  return EXT_ICONS[ext] || '📄';
}

function getLanguage(filename) {
  const ext = filename.includes('.') ? filename.split('.').pop().toLowerCase() : '';
  return LANG_MAP[ext] || 'text';
}

// ─── Syntax highlighter (token-based to avoid self-matching) ───
function highlightCode(code, language) {
  if (!code) return '';
  let html = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Token-based: collect spans, replace with placeholders, then restore.
  // This prevents regex from matching inside previously-inserted HTML attributes.
  const tokens = [];
  const tok = (cls, text) => {
    const id = tokens.length;
    tokens.push({ cls, text });
    return `\x00${id}\x00`;
  };

  if (['python', 'py'].includes(language)) {
    html = html.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, (m) => tok('string', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/(#.*$)/gm, (m) => tok('comment', m));
    html = html.replace(/\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|yield|lambda|and|or|not|in|is|True|False|None|raise|pass|break|continue|global|nonlocal|assert|async|await)\b/g, (m) => tok('keyword', m));
    html = html.replace(/(@\w+)/g, (m) => tok('decorator', m));
    html = html.replace(/\b(\d+\.?\d*)\b/g, (m) => tok('number', m));
    html = html.replace(/\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|enumerate|zip|map|filter|sorted|reversed|open|super|self)\b/g, (m) => tok('builtin', m));
  } else if (['javascript', 'typescript', 'js', 'jsx', 'ts', 'tsx'].includes(language)) {
    html = html.replace(/(\/\/.*$)/gm, (m) => tok('comment', m));
    html = html.replace(/(\/\*[\s\S]*?\*\/)/g, (m) => tok('comment', m));
    html = html.replace(/(`(?:[^`\\]|\\.)*`)/g, (m) => tok('string', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/\b(const|let|var|function|return|if|else|for|while|do|switch|case|break|continue|class|extends|import|export|from|default|new|this|super|try|catch|finally|throw|async|await|yield|typeof|instanceof|void|delete|in|of|true|false|null|undefined)\b/g, (m) => tok('keyword', m));
    html = html.replace(/\b(\d+\.?\d*)\b/g, (m) => tok('number', m));
    html = html.replace(/\b(console|require|module|process|window|document|Math|JSON|Promise|Array|Object|String|Number|Boolean|Map|Set|Symbol|Error|RegExp)\b/g, (m) => tok('builtin', m));
  } else if (['html', 'xml'].includes(language)) {
    html = html.replace(/(&lt;!--[\s\S]*?--&gt;)/g, (m) => tok('comment', m));
    html = html.replace(/(&lt;\/?)([\w-]+)/g, (_, pre, tag) => pre + tok('keyword', tag));
    html = html.replace(/([\w-]+)(=)("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (_, attr, eq, val) => tok('builtin', attr) + eq + tok('string', val));
  } else if (['css', 'scss'].includes(language)) {
    html = html.replace(/(\/\*[\s\S]*?\*\/)/g, (m) => tok('comment', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/(#[0-9a-fA-F]{3,8})\b/g, (m) => tok('number', m));
    html = html.replace(/(\d+\.?\d*)(px|em|rem|%|vh|vw|s|ms|deg|fr)?/g, (m) => tok('number', m));
  } else if (language === 'json') {
    html = html.replace(/("(?:[^"\\]|\\.)*")(\s*:)/g, (_, key, colon) => tok('builtin', key) + colon);
    html = html.replace(/:\s*("(?:[^"\\]|\\.)*")/g, (m, val) => ': ' + tok('string', val));
    html = html.replace(/\b(true|false|null)\b/g, (m) => tok('keyword', m));
    html = html.replace(/\b(\d+\.?\d*)\b/g, (m) => tok('number', m));
  } else if (['bash', 'sh'].includes(language)) {
    html = html.replace(/(#.*$)/gm, (m) => tok('comment', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/\b(if|then|else|elif|fi|for|do|done|while|case|esac|function|return|exit|echo|export|source|local)\b/g, (m) => tok('keyword', m));
  }

  // Restore tokens → actual <span> tags
  html = html.replace(/\x00(\d+)\x00/g, (_, id) => {
    const t = tokens[parseInt(id)];
    return `<span class="hl-${t.cls}">${t.text}</span>`;
  });

  return html;
}

/**
 * CodePanel component
 * Props:
 *   files: Array of { path, content, success, language, size, verification? }
 *   onClose: callback when panel is dismissed
 */
function CodePanel({ files, onClose }) {
  const [activeTab, setActiveTab] = useState(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const codeRef = useRef(null);

  // Auto-select first tab, and auto-select new tabs as they arrive
  useEffect(() => {
    if (files.length > 0) {
      const last = files[files.length - 1];
      setActiveTab(last.path);
    }
  }, [files.length]);

  // Scroll to top when switching tabs
  useEffect(() => {
    if (codeRef.current) codeRef.current.scrollTop = 0;
  }, [activeTab]);

  const activeFile = files.find(f => f.path === activeTab);
  const filename = activeFile ? activeFile.path.split('/').pop() : '';
  const language = activeFile ? getLanguage(filename) : 'text';
  const lines = activeFile?.content?.split('\n') || [];

  // Extract verification data (attached by backend to each file)
  const verification = files.find(f => f.verification)?.verification || null;
  const activeFileIssues = verification?.issues?.filter(
    iss => activeFile && (iss.file === activeFile.path || activeFile.path.endsWith(iss.file))
  ) || [];
  const issueLineSet = new Set(activeFileIssues.filter(i => i.line).map(i => i.line));

  // Auto-open diagnostics when issues are found
  useEffect(() => {
    if (verification && !verification.passed) setShowDiagnostics(true);
  }, [verification?.passed]);

  if (files.length === 0) {
    return (
      <div className="code-panel">
        <div className="code-panel-empty">
          <div className="code-panel-empty-icon">🎯</div>
          <h3>Piddy Editor</h3>
          <p>Files will appear here when Piddy creates them.</p>
          <p className="code-panel-empty-hint">Ask Piddy to build a project to get started.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="code-panel">
      {/* Tab bar */}
      <div className="code-panel-tabs">
        <div className="code-panel-tabs-scroll">
          {files.map(f => {
            const name = f.path.split('/').pop();
            const isActive = f.path === activeTab;
            return (
              <button
                key={f.path}
                className={`code-panel-tab ${isActive ? 'active' : ''} ${f.success === false ? 'error' : ''}`}
                onClick={() => setActiveTab(f.path)}
                title={f.path}
              >
                <span className="code-panel-tab-icon">{getIcon(name)}</span>
                <span className="code-panel-tab-name">{name}</span>
                {f.success === false && <span className="code-panel-tab-error">!</span>}
              </button>
            );
          })}
        </div>
        <div className="code-panel-tabs-actions">
          {verification && (
            <button
              className={`code-panel-verify-badge ${verification.passed ? 'passed' : 'failed'}`}
              onClick={() => setShowDiagnostics(d => !d)}
              title={verification.summary}
            >
              {verification.passed ? '✅' : '⚠️'}
              {' '}{verification.error_count > 0 ? `${verification.error_count}E` : ''}
              {verification.warning_count > 0 ? ` ${verification.warning_count}W` : ''}
              {verification.passed && '0 issues'}
            </button>
          )}
          <span className="code-panel-file-count">
            {files.filter(f => f.success !== false).length}/{files.length} files
          </span>
          {onClose && (
            <button className="code-panel-close" onClick={onClose} title="Close all">✕</button>
          )}
        </div>
      </div>

      {/* Breadcrumb / path */}
      {activeFile && (
        <div className="code-panel-breadcrumb">
          <span className="code-panel-breadcrumb-icon">{activeFile.success !== false ? '✅' : '❌'}</span>
          <span className="code-panel-breadcrumb-path">{activeFile.path}</span>
          {activeFile.size != null && (
            <span className="code-panel-breadcrumb-size">{activeFile.size}B</span>
          )}
          <span className="code-panel-breadcrumb-lang">{language}</span>
        </div>
      )}

      {/* Diagnostics panel */}
      {showDiagnostics && verification && verification.issues?.length > 0 && (
        <div className="code-panel-diagnostics">
          <div className="code-panel-diagnostics-header">
            <span>Problems</span>
            <span className="code-panel-diagnostics-count">
              {verification.error_count > 0 && <span className="diag-errors">{verification.error_count} errors</span>}
              {verification.error_count > 0 && verification.warning_count > 0 && ', '}
              {verification.warning_count > 0 && <span className="diag-warnings">{verification.warning_count} warnings</span>}
            </span>
            <button className="code-panel-diagnostics-close" onClick={() => setShowDiagnostics(false)}>✕</button>
          </div>
          <div className="code-panel-diagnostics-list">
            {verification.issues.map((iss, idx) => (
              <div key={idx} className={`code-panel-issue ${iss.severity}`}>
                <span className="code-panel-issue-icon">{iss.severity === 'error' ? '🔴' : '🟡'}</span>
                <span className="code-panel-issue-file">{iss.file}</span>
                {iss.line && <span className="code-panel-issue-line">:{iss.line}</span>}
                <span className="code-panel-issue-code">[{iss.code}]</span>
                <span className="code-panel-issue-msg">{iss.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Code area */}
      {activeFile && activeFile.content ? (
        <div className="code-panel-editor" ref={codeRef}>
          <div className="code-panel-gutter">
            {lines.map((_, i) => {
              const lineNo = i + 1;
              const hasIssue = issueLineSet.has(lineNo);
              const severity = hasIssue
                ? activeFileIssues.find(iss => iss.line === lineNo)?.severity || 'warning'
                : null;
              return (
                <div
                  key={i}
                  className={`code-panel-line-num${severity === 'error' ? ' line-error' : ''}${severity === 'warning' ? ' line-warning' : ''}`}
                  title={hasIssue ? activeFileIssues.filter(iss => iss.line === lineNo).map(iss => iss.message).join('; ') : undefined}
                >
                  {lineNo}
                </div>
              );
            })}
          </div>
          <pre className="code-panel-code">
            <code dangerouslySetInnerHTML={{
              __html: highlightCode(activeFile.content, language)
            }} />
          </pre>
        </div>
      ) : activeFile ? (
        <div className="code-panel-error-view">
          <span>❌</span>
          <p>Failed to create: {activeFile.path}</p>
          {activeFile.error && <p className="code-panel-error-detail">{activeFile.error}</p>}
        </div>
      ) : null}
    </div>
  );
}

export default CodePanel;
