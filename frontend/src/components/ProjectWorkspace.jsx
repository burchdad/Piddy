import React, { useState, useEffect, useCallback } from 'react';
import { apiCall } from '../utils/api';
import '../styles/workspace.css';

/**
 * VS Code-style Project Workspace Viewer
 * ├── File Explorer (left)
 * ├── Code Viewer (center) with tabs
 * └── Info/Terminal Panel (bottom)
 */

// ─── File icon mapping ───
const FILE_ICONS = {
  py: '🐍', js: '📜', jsx: '⚛️', ts: '🔷', tsx: '⚛️',
  java: '☕', c: '🔵', cpp: '🔵', cs: '🟣', go: '🔹',
  rs: '🦀', rb: '💎', php: '🐘', swift: '🍎', kt: '🟠',
  html: '🌐', css: '🎨', scss: '🎨', json: '📋', yaml: '📄',
  yml: '📄', xml: '📄', md: '📝', txt: '📄', sh: '⬛',
  bat: '⬛', ps1: '⬛', sql: '🗃️', toml: '📄', ini: '📄',
  dockerfile: '🐳', makefile: '⚙️', gitignore: '📄',
};

const getFileIcon = (name, ext) => {
  const lower = name.toLowerCase();
  if (lower === 'dockerfile') return '🐳';
  if (lower === 'makefile') return '⚙️';
  if (lower === 'readme.md') return '📖';
  if (lower === 'requirements.txt') return '📦';
  if (lower === 'package.json') return '📦';
  if (lower === '.gitignore') return '🙈';
  return FILE_ICONS[ext] || '📄';
};

// ─── File Tree Node ───
function TreeNode({ node, depth, selectedPath, onSelect, expandedDirs, onToggleDir }) {
  const isDir = node.type === 'directory';
  const isExpanded = expandedDirs.has(node.path);
  const isSelected = selectedPath === node.path;

  const handleClick = () => {
    if (isDir) {
      onToggleDir(node.path);
    } else {
      onSelect(node);
    }
  };

  return (
    <>
      <div
        className={`ws-tree-node ${isSelected ? 'selected' : ''} ${isDir ? 'directory' : 'file'}`}
        style={{ paddingLeft: `${12 + depth * 16}px` }}
        onClick={handleClick}
        title={node.path}
      >
        {isDir ? (
          <span className="ws-tree-chevron">{isExpanded ? '▾' : '▸'}</span>
        ) : (
          <span className="ws-tree-chevron" style={{ visibility: 'hidden' }}>▸</span>
        )}
        <span className="ws-tree-icon">
          {isDir ? (isExpanded ? '📂' : '📁') : getFileIcon(node.name, node.extension)}
        </span>
        <span className="ws-tree-name">{node.name}</span>
        {!isDir && node.size != null && (
          <span className="ws-tree-size">{formatSize(node.size)}</span>
        )}
      </div>
      {isDir && isExpanded && node.children && node.children.map(child => (
        <TreeNode
          key={child.path}
          node={child}
          depth={depth + 1}
          selectedPath={selectedPath}
          onSelect={onSelect}
          expandedDirs={expandedDirs}
          onToggleDir={onToggleDir}
        />
      ))}
    </>
  );
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

// ─── Simple syntax highlighter (no external deps) ───
function highlightCode(code, language) {
  if (!code) return '';

  // Escape HTML
  let html = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Token-based: collect spans, replace with placeholders, then restore.
  // This prevents regex from matching inside previously-inserted HTML attributes.
  const tokens = [];
  const tok = (cls, text) => {
    const id = tokens.length;
    tokens.push({ cls, text });
    return `\x00${id}\x00`;
  };

  // Language-specific highlighting
  if (['python', 'py'].includes(language)) {
    html = html.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, (m) => tok('string', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/(#.*$)/gm, (m) => tok('comment', m));
    html = html.replace(/\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|yield|lambda|and|or|not|in|is|True|False|None|raise|pass|break|continue|global|nonlocal|assert|async|await)\b/g, (m) => tok('keyword', m));
    html = html.replace(/(@\w+)/g, (m) => tok('decorator', m));
    html = html.replace(/\b(\d+\.?\d*)\b/g, (m) => tok('number', m));
    html = html.replace(/\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|enumerate|zip|map|filter|sorted|reversed|open|super|self)\b/g, (m) => tok('builtin', m));
  } else if (['javascript', 'js', 'jsx', 'typescript', 'ts', 'tsx'].includes(language)) {
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
  } else if (['css', 'scss', 'less'].includes(language)) {
    html = html.replace(/(\/\*[\s\S]*?\*\/)/g, (m) => tok('comment', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/(#[0-9a-fA-F]{3,8})\b/g, (m) => tok('number', m));
    html = html.replace(/(\d+\.?\d*)(px|em|rem|%|vh|vw|s|ms|deg|fr)?/g, (m) => tok('number', m));
  } else if (['json'].includes(language)) {
    html = html.replace(/("(?:[^"\\]|\\.)*")(\s*:)/g, (_, key, colon) => tok('builtin', key) + colon);
    html = html.replace(/:\s*("(?:[^"\\]|\\.)*")/g, (m, val) => ': ' + tok('string', val));
    html = html.replace(/\b(true|false|null)\b/g, (m) => tok('keyword', m));
    html = html.replace(/\b(\d+\.?\d*)\b/g, (m) => tok('number', m));
  } else if (['bash', 'sh'].includes(language)) {
    html = html.replace(/(#.*$)/gm, (m) => tok('comment', m));
    html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, (m) => tok('string', m));
    html = html.replace(/\b(if|then|else|elif|fi|for|do|done|while|until|case|esac|function|return|exit|echo|export|source|local|readonly|shift|set|unset)\b/g, (m) => tok('keyword', m));
  } else if (['markdown', 'md'].includes(language)) {
    html = html.replace(/^(#{1,6}\s.*$)/gm, (m) => tok('keyword', m));
    html = html.replace(/(\*\*.*?\*\*)/g, (m) => tok('builtin', m));
    html = html.replace(/(`[^`]+`)/g, (m) => tok('string', m));
    html = html.replace(/(```[\s\S]*?```)/g, (m) => tok('comment', m));
  }

  // Restore tokens → actual <span> tags
  html = html.replace(/\x00(\d+)\x00/g, (_, id) => {
    const t = tokens[parseInt(id)];
    return `<span class="hl-${t.cls}">${t.text}</span>`;
  });

  return html;
}

// ─── Main ProjectWorkspace Component ───
function ProjectWorkspace() {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [tree, setTree] = useState([]);
  const [openTabs, setOpenTabs] = useState([]);
  const [activeTab, setActiveTab] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fileLoading, setFileLoading] = useState(false);
  const [expandedDirs, setExpandedDirs] = useState(new Set());
  const [bottomPanel, setBottomPanel] = useState('info'); // 'info' | 'output'
  const [outputLog, setOutputLog] = useState([]);

  // Load project list
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const data = await apiCall('/api/projects');
        setProjects(data.projects || []);
      } catch (err) {
        console.error('Failed to load projects:', err);
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, []);

  // Load file tree when project changes
  useEffect(() => {
    if (!activeProject) return;
    const loadTree = async () => {
      try {
        const data = await apiCall('/api/projects/tree', {
          method: 'POST',
          data: { project_name: activeProject },
        });
        setTree(data.tree || []);
        // Auto-expand first level
        const firstDirs = (data.tree || []).filter(n => n.type === 'directory').map(n => n.path);
        setExpandedDirs(new Set(firstDirs));
        addLog('info', `Loaded project: ${activeProject}`);
      } catch (err) {
        console.error('Failed to load tree:', err);
        addLog('error', `Failed to load project tree: ${err.message}`);
      }
    };
    loadTree();
  }, [activeProject]);

  const addLog = useCallback((type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setOutputLog(prev => [...prev.slice(-100), { type, message, timestamp }]);
  }, []);

  // Open a file
  const handleFileSelect = async (node) => {
    // Check if already open
    const existing = openTabs.find(t => t.path === node.path);
    if (existing) {
      setActiveTab(node.path);
      return;
    }

    setFileLoading(true);
    try {
      const filePath = activeProject ? `${activeProject}/${node.path}` : node.path;
      const data = await apiCall('/api/projects/file', {
        method: 'POST',
        data: { file_path: filePath },
      });

      if (data.error) {
        addLog('error', data.error);
        return;
      }

      const tab = {
        path: node.path,
        name: node.name,
        extension: data.extension,
        language: data.language,
        content: data.content,
        size: data.size,
        lines: data.lines,
      };

      setOpenTabs(prev => [...prev, tab]);
      setActiveTab(node.path);
      setFileContent(tab);
      addLog('info', `Opened: ${node.path} (${data.lines} lines, ${formatSize(data.size)})`);
    } catch (err) {
      addLog('error', `Failed to open file: ${err.message}`);
    } finally {
      setFileLoading(false);
    }
  };

  // Switch tab
  const handleTabClick = (path) => {
    setActiveTab(path);
    const tab = openTabs.find(t => t.path === path);
    if (tab) setFileContent(tab);
  };

  // Close tab
  const handleTabClose = (e, path) => {
    e.stopPropagation();
    const newTabs = openTabs.filter(t => t.path !== path);
    setOpenTabs(newTabs);
    if (activeTab === path) {
      const last = newTabs[newTabs.length - 1];
      setActiveTab(last?.path || null);
      setFileContent(last || null);
    }
  };

  // Toggle directory expand/collapse
  const handleToggleDir = (path) => {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  // Back to project list
  const handleBackToList = () => {
    setActiveProject(null);
    setTree([]);
    setOpenTabs([]);
    setActiveTab(null);
    setFileContent(null);
    setOutputLog([]);
  };

  // ─── Render: Project List ───
  if (!activeProject) {
    return (
      <div className="ws-container">
        <div className="ws-project-list">
          <div className="ws-project-list-header">
            <h2>📁 Projects</h2>
            <p className="ws-subtitle">{projects.length} project{projects.length !== 1 ? 's' : ''} in workspace</p>
          </div>

          {loading ? (
            <div className="ws-loading"><div className="spinner" /><p>Loading projects...</p></div>
          ) : projects.length === 0 ? (
            <div className="ws-empty">
              <div className="ws-empty-icon">📂</div>
              <h3>No projects yet</h3>
              <p>Ask Piddy to build something! Created projects will appear here.</p>
            </div>
          ) : (
            <div className="ws-project-grid">
              {projects.map(project => (
                <div
                  key={project.name}
                  className="ws-project-card"
                  onClick={() => setActiveProject(project.name)}
                >
                  <div className="ws-project-card-icon">📁</div>
                  <div className="ws-project-card-info">
                    <div className="ws-project-card-name">{project.name}</div>
                    <div className="ws-project-card-meta">
                      {project.file_count} file{project.file_count !== 1 ? 's' : ''} · {formatSize(project.total_size)}
                    </div>
                    <div className="ws-project-card-time">
                      {new Date(project.modified).toLocaleDateString()}
                    </div>
                  </div>
                  <span className="ws-project-card-arrow">→</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ─── Render: IDE Workspace ───
  const activeFileContent = fileContent || (activeTab ? openTabs.find(t => t.path === activeTab) : null);

  return (
    <div className="ws-container">
      <div className="ws-ide">
        {/* ── File Explorer (left) ── */}
        <div className="ws-explorer">
          <div className="ws-explorer-header">
            <button className="ws-explorer-back" onClick={handleBackToList} title="Back to projects">←</button>
            <span className="ws-explorer-title">{activeProject.toUpperCase()}</span>
          </div>
          <div className="ws-explorer-tree">
            {tree.length === 0 ? (
              <div className="ws-tree-empty">No files</div>
            ) : (
              tree.map(node => (
                <TreeNode
                  key={node.path}
                  node={node}
                  depth={0}
                  selectedPath={activeTab}
                  onSelect={handleFileSelect}
                  expandedDirs={expandedDirs}
                  onToggleDir={handleToggleDir}
                />
              ))
            )}
          </div>
        </div>

        {/* ── Main Editor Area ── */}
        <div className="ws-editor-area">
          {/* Tab Bar */}
          <div className="ws-tab-bar">
            {openTabs.map(tab => (
              <div
                key={tab.path}
                className={`ws-tab ${activeTab === tab.path ? 'active' : ''}`}
                onClick={() => handleTabClick(tab.path)}
              >
                <span className="ws-tab-icon">{getFileIcon(tab.name, tab.extension)}</span>
                <span className="ws-tab-name">{tab.name}</span>
                <button className="ws-tab-close" onClick={(e) => handleTabClose(e, tab.path)}>×</button>
              </div>
            ))}
          </div>

          {/* Code Viewer */}
          <div className="ws-code-area">
            {fileLoading ? (
              <div className="ws-loading"><div className="spinner" /><p>Loading file...</p></div>
            ) : activeFileContent ? (
              <div className="ws-code-viewer">
                {/* Breadcrumb */}
                <div className="ws-breadcrumb">
                  <span className="ws-breadcrumb-project">{activeProject}</span>
                  <span className="ws-breadcrumb-sep">/</span>
                  {activeFileContent.path.split('/').map((part, i, arr) => (
                    <React.Fragment key={i}>
                      <span className={i === arr.length - 1 ? 'ws-breadcrumb-file' : 'ws-breadcrumb-dir'}>{part}</span>
                      {i < arr.length - 1 && <span className="ws-breadcrumb-sep">/</span>}
                    </React.Fragment>
                  ))}
                  <span className="ws-breadcrumb-lang">{activeFileContent.language}</span>
                </div>

                {/* Code with line numbers */}
                <div className="ws-code-scroll">
                  <table className="ws-code-table">
                    <tbody>
                      {(activeFileContent.content || '').split('\n').map((line, i) => (
                        <tr key={i} className="ws-code-line">
                          <td className="ws-line-number">{i + 1}</td>
                          <td
                            className="ws-line-content"
                            dangerouslySetInnerHTML={{
                              __html: highlightCode(line, activeFileContent.language),
                            }}
                          />
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="ws-welcome">
                <div className="ws-welcome-icon">📂</div>
                <h3>{activeProject}</h3>
                <p>Select a file from the explorer to view its contents</p>
                <div className="ws-welcome-stats">
                  {tree.length > 0 && (
                    <span>{countFiles(tree)} files in project</span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* ── Bottom Panel (Terminal / Info) ── */}
          <div className="ws-bottom-panel">
            <div className="ws-bottom-tabs">
              <button
                className={`ws-bottom-tab ${bottomPanel === 'info' ? 'active' : ''}`}
                onClick={() => setBottomPanel('info')}
              >
                ℹ️ File Info
              </button>
              <button
                className={`ws-bottom-tab ${bottomPanel === 'output' ? 'active' : ''}`}
                onClick={() => setBottomPanel('output')}
              >
                ⬛ Output
                {outputLog.length > 0 && (
                  <span className="ws-bottom-badge">{outputLog.length}</span>
                )}
              </button>
            </div>

            <div className="ws-bottom-content">
              {bottomPanel === 'info' ? (
                <div className="ws-file-info">
                  {activeFileContent ? (
                    <>
                      <div className="ws-info-row">
                        <span className="ws-info-label">File</span>
                        <span className="ws-info-value">{activeFileContent.name}</span>
                      </div>
                      <div className="ws-info-row">
                        <span className="ws-info-label">Path</span>
                        <span className="ws-info-value">{activeProject}/{activeFileContent.path}</span>
                      </div>
                      <div className="ws-info-row">
                        <span className="ws-info-label">Language</span>
                        <span className="ws-info-value">{activeFileContent.language}</span>
                      </div>
                      <div className="ws-info-row">
                        <span className="ws-info-label">Size</span>
                        <span className="ws-info-value">{formatSize(activeFileContent.size)}</span>
                      </div>
                      <div className="ws-info-row">
                        <span className="ws-info-label">Lines</span>
                        <span className="ws-info-value">{activeFileContent.lines}</span>
                      </div>
                    </>
                  ) : (
                    <div className="ws-info-empty">No file selected</div>
                  )}
                </div>
              ) : (
                <div className="ws-output-log">
                  {outputLog.length === 0 ? (
                    <div className="ws-output-empty">No output yet</div>
                  ) : (
                    outputLog.map((entry, i) => (
                      <div key={i} className={`ws-output-entry ${entry.type}`}>
                        <span className="ws-output-time">[{entry.timestamp}]</span>
                        <span className="ws-output-msg">{entry.message}</span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function countFiles(tree) {
  let count = 0;
  for (const node of tree) {
    if (node.type === 'file') count++;
    else if (node.children) count += countFiles(node.children);
  }
  return count;
}

export default ProjectWorkspace;
