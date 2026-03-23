import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';

function Skills() {
  const [skills, setSkills] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  const loadSkills = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/api/skills');
      setSkills(data.skills || []);
    } catch {
      setSkills([]);
    } finally {
      setLoading(false);
    }
  };

  const reloadSkills = async () => {
    setLoading(true);
    try {
      await apiCall('/api/skills/reload', { method: 'POST' });
      await loadSkills();
    } catch {
      setLoading(false);
    }
  };

  useEffect(() => { loadSkills(); }, []);

  const filtered = skills.filter(s => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      (s.name || '').toLowerCase().includes(q) ||
      (s.description || '').toLowerCase().includes(q) ||
      (s.tags || []).some(t => t.toLowerCase().includes(q))
    );
  });

  return (
    <div className="skills-page">
      <div className="skills-header">
        <div>
          <h2>Skills & Plugins</h2>
          <p className="skills-subtitle">{skills.length} skills loaded from library/skills/</p>
        </div>
        <button className="chat-btn-secondary" onClick={reloadSkills} disabled={loading}>
          {loading ? 'Loading...' : 'Reload'}
        </button>
      </div>

      {/* Search */}
      <div className="skills-search">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search skills by name, description, or tag..."
          className="skills-search-input"
        />
      </div>

      {/* Grid */}
      {loading && skills.length === 0 ? (
        <div className="doctor-loading"><div className="spinner" /><p>Loading skills...</p></div>
      ) : filtered.length === 0 ? (
        <div className="skills-empty">
          <p>No skills found{search ? ` matching "${search}"` : ''}.</p>
          <p className="skills-hint">Add SKILL.md files to library/skills/ to create new skills.</p>
        </div>
      ) : (
        <div className="skills-grid">
          {filtered.map((skill, i) => (
            <div
              key={skill.name || i}
              className={`skill-card ${expanded === i ? 'expanded' : ''}`}
              onClick={() => setExpanded(expanded === i ? null : i)}
            >
              <div className="skill-card-header">
                <span className="skill-card-icon">
                  {skill.tags?.includes('security') ? '🔒' :
                   skill.tags?.includes('database') ? '🗄️' :
                   skill.tags?.includes('api') ? '🔌' :
                   skill.tags?.includes('frontend') ? '🎨' : '⚡'}
                </span>
                <div>
                  <div className="skill-card-name">{skill.name}</div>
                  <div className="skill-card-version">{skill.version || '1.0'}</div>
                </div>
              </div>
              <p className="skill-card-desc">{skill.description}</p>
              {skill.tags && skill.tags.length > 0 && (
                <div className="skill-card-tags">
                  {skill.tags.map(t => <span key={t} className="skill-tag">{t}</span>)}
                </div>
              )}
              {expanded === i && skill.capabilities && (
                <div className="skill-card-details">
                  <h4>Capabilities</h4>
                  <ul>
                    {skill.capabilities.map((c, j) => <li key={j}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Skills;
