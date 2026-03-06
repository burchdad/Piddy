import React, { useState, useEffect, useRef } from 'react';
import '../styles/components.css';

function DependencyGraph() {
  const [graph, setGraph] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/graph/dependencies');
        const data = await response.json();
        setGraph(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch dependency graph:', error);
        setLoading(false);
      }
    };

    fetchGraph();
    const interval = setInterval(fetchGraph, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredNodes = graph?.nodes.filter(n =>
    filterType === 'all' || n.type === filterType
  ) || [];

  const nodeColors = {
    function: '#6366f1',
    module: '#8b5cf6',
    service: '#4299e1',
    external: '#94a3b8',
  };

  const getNodeColor = (type) => nodeColors[type] || '#6366f1';

  return (
    <div className="page dependency-graph">
      <div className="header-section">
        <h2>📊 Dependency Graph Viewer</h2>
        <p className="subtitle">Visualize function→module→service relationships and call dependencies</p>
      </div>

      {loading ? (
        <div className="loading">Loading dependency graph...</div>
      ) : (
        <>
          {/* Filter */}
          <div className="filter-group" style={{ marginBottom: '2rem' }}>
            <label style={{ marginRight: '1rem', color: 'var(--text-secondary)' }}>Filter by Type:</label>
            <select 
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Types</option>
              <option value="function">Functions</option>
              <option value="module">Modules</option>
              <option value="service">Services</option>
              <option value="external">External</option>
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
            {/* Graph Visualization */}
            <div className="graph-container" style={{
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              minHeight: '600px',
              position: 'relative'
            }}>
              <svg 
                ref={canvasRef}
                width="100%"
                height="600"
                style={{ border: '1px solid var(--border-color)', borderRadius: '0.5rem' }}
              >
                {/* Render edges first (so they appear behind nodes) */}
                {graph?.edges.map((edge, idx) => {
                  const fromNode = graph.nodes.find(n => n.id === edge.from);
                  const toNode = graph.nodes.find(n => n.id === edge.to);
                  if (!fromNode || !toNode) return null;

                  return (
                    <g key={`edge-${idx}`}>
                      <line
                        x1={fromNode.x}
                        y1={fromNode.y}
                        x2={toNode.x}
                        y2={toNode.y}
                        stroke={edge.weight > 5 ? '#ff6b6b' : '#4a5568'}
                        strokeWidth={edge.weight > 5 ? 2 : 1}
                        strokeDasharray={edge.type === 'async' ? '5,5' : '0'}
                        opacity="0.6"
                      />
                      {/* Edge label */}
                      <text
                        x={(fromNode.x + toNode.x) / 2}
                        y={(fromNode.y + toNode.y) / 2}
                        fill="#94a3b8"
                        fontSize="10"
                        textAnchor="middle"
                        pointerEvents="none"
                      >
                        {edge.calls}
                      </text>
                    </g>
                  );
                })}

                {/* Render nodes */}
                {filteredNodes.map((node) => (
                  <g
                    key={node.id}
                    onClick={() => setSelectedNode(selectedNode?.id === node.id ? null : node)}
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Node circle */}
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.type === 'service' ? 25 : node.type === 'module' ? 20 : 15}
                      fill={getNodeColor(node.type)}
                      opacity={hoveredNode === node.id || selectedNode?.id === node.id ? 1 : 0.7}
                      stroke={hoveredNode === node.id || selectedNode?.id === node.id ? '#f1f5f9' : 'none'}
                      strokeWidth={2}
                    />
                    {/* Node icon/text */}
                    <text
                      x={node.x}
                      y={node.y}
                      textAnchor="middle"
                      dy="0.3em"
                      fill="white"
                      fontSize="12"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {node.name.charAt(0)}
                    </text>
                  </g>
                ))}
              </svg>

              {/* Graph Legend */}
              <div style={{
                display: 'flex',
                gap: '2rem',
                marginTop: '1rem',
                fontSize: '0.85rem',
                flexWrap: 'wrap'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: nodeColors.function
                  }} />
                  <span>Functions</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: nodeColors.module
                  }} />
                  <span>Modules</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: nodeColors.service
                  }} />
                  <span>Services</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <svg width="20" height="2">
                    <line x1="0" y1="1" x2="20" y2="1" stroke="#ff6b6b" strokeWidth="2" />
                  </svg>
                  <span>High Load ({`>`}5 calls)</span>
                </div>
              </div>
            </div>

            {/* Node Details Sidebar */}
            <div style={{
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              maxHeight: '600px',
              overflowY: 'auto'
            }}>
              {hoveredNode || selectedNode ? (
                <div className="node-detail">
                  {(() => {
                    const node = graph?.nodes.find(n => n.id === (selectedNode?.id || hoveredNode));
                    if (!node) return null;

                    return (
                      <>
                        <h3 style={{ marginBottom: '1rem' }}>{node.name}</h3>

                        {/* Type Badge */}
                        <div style={{ marginBottom: '1rem' }}>
                          <span style={{
                            display: 'inline-block',
                            padding: '0.35rem 0.75rem',
                            backgroundColor: getNodeColor(node.type),
                            color: 'white',
                            borderRadius: '0.25rem',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase'
                          }}>
                            {node.type}
                          </span>
                        </div>

                        {/* Description */}
                        <p style={{
                          color: 'var(--text-secondary)',
                          marginBottom: '1rem',
                          fontSize: '0.9rem'
                        }}>
                          {node.description}
                        </p>

                        {/* Metrics */}
                        <div style={{ marginBottom: '1.5rem' }}>
                          <h4 style={{ Color: 'var(--text-primary)', marginBottom: '0.5rem' }}>📊 Metrics</h4>
                          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            <p>• Inbound Calls: <strong style={{ color: 'var(--text-primary)' }}>{node.inbound_count}</strong></p>
                            <p>• Outbound Calls: <strong style={{ color: 'var(--text-primary)' }}>{node.outbound_count}</strong></p>
                            <p>• Avg Response: <strong style={{ color: 'var(--text-primary)' }}>{node.avg_response_time}ms</strong></p>
                            <p>• Error Rate: <strong style={{ color: node.error_rate > 0.05 ? '#ff6b6b' : '#51cf66' }}>{(node.error_rate * 100).toFixed(2)}%</strong></p>
                          </div>
                        </div>

                        {/* Dependencies */}
                        <div style={{ marginBottom: '1.5rem' }}>
                          <h4 style={{ marginBottom: '0.5rem' }}>🔗 Dependencies</h4>
                          {(() => {
                            const deps = graph?.edges.filter(e => e.from === node.id).map(e => {
                              const target = graph.nodes.find(n => n.id === e.to);
                              return { target, edge: e };
                            }).filter(d => d.target) || [];
                            
                            if (deps.length === 0) return <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No outbound dependencies</p>;
                            
                            return (
                              <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                {deps.map((dep, idx) => (
                                  <li key={idx}>
                                    → {dep.target.name}
                                    <span style={{ color: '#94a3b8', marginLeft: '0.5rem' }}>({dep.edge.calls} calls)</span>
                                  </li>
                                ))}
                              </ul>
                            );
                          })()}
                        </div>

                        {/* Consumers */}
                        <div>
                          <h4 style={{ marginBottom: '0.5rem' }}>👥 Consumers</h4>
                          {(() => {
                            const consumers = graph?.edges.filter(e => e.to === node.id).map(e => {
                              const source = graph.nodes.find(n => n.id === e.from);
                              return { source, edge: e };
                            }).filter(d => d.source) || [];
                            
                            if (consumers.length === 0) return <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No consumers</p>;
                            
                            return (
                              <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                {consumers.map((cons, idx) => (
                                  <li key={idx}>
                                    ← {cons.source.name}
                                    <span style={{ color: '#94a3b8', marginLeft: '0.5rem' }}>({cons.edge.calls} calls)</span>
                                  </li>
                                ))}
                              </ul>
                            );
                          })()}
                        </div>
                      </>
                    );
                  })()}
                </div>
              ) : (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center', paddingTop: '2rem' }}>
                  <p>Hover over or click nodes to see details</p>
                </div>
              )}
            </div>
          </div>

          {/* Statistics */}
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>📈 Graph Statistics</h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem'
            }}>
              <div className="stat-card">
                <div className="stat-number">{graph?.nodes.length || 0}</div>
                <div className="stat-label">Total Nodes</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{graph?.edges.length || 0}</div>
                <div className="stat-label">Total Dependencies</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{graph?.nodes.filter(n => n.type === 'function').length || 0}</div>
                <div className="stat-label">Functions</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{graph?.nodes.filter(n => n.type === 'module').length || 0}</div>
                <div className="stat-label">Modules</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{graph?.nodes.filter(n => n.type === 'service').length || 0}</div>
                <div className="stat-label">Services</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{((graph?.edges.filter(e => e.weight > 5).length || 0) / (graph?.edges.length || 1) * 100).toFixed(1)}%</div>
                <div className="stat-label">High Load Deps</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default DependencyGraph;
