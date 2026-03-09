import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function DependencyGraph() {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const response = await fetch('/api/graph/dependencies');
        const data = await response.json();
        setGraph(data);
      } catch (err) {
        console.error('Failed to fetch dependency graph:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
    const interval = setInterval(fetchGraph, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="page">Loading dependency graph...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>📈 Dependency Graph</h1>
      </div>

      {graph && (
        <div className="graph-container">
          <div className="graph-stats">
            <div className="stat-card">
              <div className="stat-label">Total Nodes</div>
              <div className="stat-value">{graph.nodes?.length || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Total Edges</div>
              <div className="stat-value">{graph.edges?.length || 0}</div>
            </div>
          </div>

          <div className="nodes-list">
            <h3>Services & Dependencies</h3>
            <div className="nodes-grid">
              {graph.nodes?.map((node) => (
                <div
                  key={node.id}
                  className="node-item"
                  onClick={() => setSelectedNode(selectedNode?.id === node.id ? null : node)}
                >
                  <div className="node-name">{node.name}</div>
                  <div className="node-type">{node.type}</div>
                  <div className="node-stats">
                    <span>튱 {node.inbound_count}</span>
                    <span>튰 {node.outbound_count}</span>
                  </div>
                  <div className="node-metric">{node.avg_response_time.toFixed(0)}ms</div>
                </div>
              ))}
            </div>
          </div>

          {selectedNode && (
            <div className="node-details">
              <h3>Node Details: {selectedNode.name}</h3>
              <div className="details-grid">
                <div className="detail">
                  <span className="label">Type:</span>
                  <span className="value">{selectedNode.type}</span>
                </div>
                <div className="detail">
                  <span className="label">Inbound Connections:</span>
                  <span className="value">{selectedNode.inbound_count}</span>
                </div>
                <div className="detail">
                  <span className="label">Outbound Connections:</span>
                  <span className="value">{selectedNode.outbound_count}</span>
                </div>
                <div className="detail">
                  <span className="label">Avg Response Time:</span>
                  <span className="value">{selectedNode.avg_response_time.toFixed(2)}ms</span>
                </div>
                <div className="detail">
                  <span className="label">Error Rate:</span>
                  <span className="value">{(selectedNode.error_rate * 100).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DependencyGraph;
