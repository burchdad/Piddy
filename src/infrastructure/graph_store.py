"""
logger = logging.getLogger(__name__)
Graph Store Infrastructure
Stores and queries dependency graphs for Phases 39-41+

Supports:
- Phase 39: Impact visualization
- Phase 41: Multi-repo coordination  
- Phase 50+: Multi-agent reasoning
"""

from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
import sqlite3
from dataclasses import dataclass, asdict
import json
from datetime import datetime
import logging


@dataclass
class GraphNode:
    """Represents a single node in dependency graph"""
    id: str                          # Unique identifier
    type: str                        # "function", "module", "service", "file"
    metadata: Dict                   # name, file, line_number, complexity, etc.


@dataclass
class GraphEdge:
    """Represents relationship between nodes"""
    source: str                      # Source node ID
    target: str                      # Target node ID
    type: str                        # "calls", "imports", "depends_on", "uses_api"
    metadata: Dict                   # weight, confidence, frequency, etc.


class DependencyGraphStore:
    """Store and query dependency graphs"""
    
    def __init__(self, db_path: str = "piddy_graphs.db"):
        """Initialize graph store with SQLite backend"""
        self.db_path = db_path
        self.graphs: Dict[str, nx.DiGraph] = {}
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Graph metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graphs (
                graph_id TEXT PRIMARY KEY,
                repo_id TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                node_count INTEGER,
                edge_count INTEGER,
                metadata TEXT
            )
        ''')
        
        # Nodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                graph_id TEXT,
                node_id TEXT,
                node_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (graph_id, node_id),
                FOREIGN KEY (graph_id) REFERENCES graphs(graph_id)
            )
        ''')
        
        # Edges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_edges (
                graph_id TEXT,
                source_id TEXT,
                target_id TEXT,
                edge_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (graph_id, source_id, target_id),
                FOREIGN KEY (graph_id) REFERENCES graphs(graph_id)
            )
        ''')
        
        # Indices for fast queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_type ON graph_nodes(node_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_type ON graph_edges(edge_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_id)')
        
        conn.commit()
        conn.close()
    
    def create_graph(self, graph_id: str, repo_id: str, 
                    nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """Create new dependency graph"""
        G = nx.DiGraph()
        
        # Add nodes to graph
        for node in nodes:
            G.add_node(node.id, type=node.type, **node.metadata)
        
        # Add edges to graph
        for edge in edges:
            G.add_edge(edge.source, edge.target, 
                      relation_type=edge.type, **edge.metadata)
        
        # Store in memory
        self.graphs[graph_id] = G
        
        # Persist to database
        self._persist_graph(graph_id, repo_id, nodes, edges)
    
    def _persist_graph(self, graph_id: str, repo_id: str,
                      nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        """Save graph to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        # Insert graph metadata
        cursor.execute('''
            INSERT OR REPLACE INTO graphs 
            (graph_id, repo_id, created_at, updated_at, node_count, edge_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (graph_id, repo_id, now, now, len(nodes), len(edges), '{}'))
        
        # Insert nodes
        for node in nodes:
            cursor.execute('''
                INSERT OR REPLACE INTO graph_nodes
                (graph_id, node_id, node_type, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (graph_id, node.id, node.type, json.dumps(node.metadata), now))
        
        # Insert edges
        for edge in edges:
            cursor.execute('''
                INSERT OR REPLACE INTO graph_edges
                (graph_id, source_id, target_id, edge_type, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (graph_id, edge.source, edge.target, edge.type,
                  json.dumps(edge.metadata), now))
        
        conn.commit()
        conn.close()
    
    def load_graph(self, graph_id: str) -> Optional[nx.DiGraph]:
        """Load graph from database"""
        if graph_id in self.graphs:
            return self.graphs[graph_id]
        
        G = nx.DiGraph()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load nodes
        cursor.execute('''
            SELECT node_id, node_type, metadata 
            FROM graph_nodes 
            WHERE graph_id = ?
        ''', (graph_id,))
        
        for node_id, node_type, metadata in cursor.fetchall():
            meta = json.loads(metadata) if metadata else {}
            G.add_node(node_id, type=node_type, **meta)
        
        # Load edges
        cursor.execute('''
            SELECT source_id, target_id, edge_type, metadata
            FROM graph_edges
            WHERE graph_id = ?
        ''', (graph_id,))
        
        for source, target, edge_type, metadata in cursor.fetchall():
            meta = json.loads(metadata) if metadata else {}
            G.add_edge(source, target, relation_type=edge_type, **meta)
        
        conn.close()
        
        self.graphs[graph_id] = G
        return G
    
    def get_dependencies(self, graph_id: str, node_id: str) -> Set[str]:
        """Get all direct dependencies of a node (downstream)"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return set()
        
        # Return all nodes this node directly depends on
        return set(G.predecessors(node_id))
    
    def get_dependents(self, graph_id: str, node_id: str) -> Set[str]:
        """Get all nodes that depend on this node (upstream)"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return set()
        
        # Return all nodes that depend on this node
        return set(G.successors(node_id))
    
    def get_transitive_dependencies(self, graph_id: str, node_id: str) -> Set[str]:
        """Get all transitive dependencies (full impact radius downstream)"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return set()
        
        # Use BFS to find all reachable nodes
        return set(nx.descendants(G, node_id))
    
    def get_transitive_dependents(self, graph_id: str, node_id: str) -> Set[str]:
        """Get all transitive dependents (full impact radius upstream)"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return set()
        
        # Use BFS to find all nodes that can reach this node
        return set(nx.ancestors(G, node_id))
    
    def get_impact_radius(self, graph_id: str, node_id: str) -> int:
        """Calculate maximum distance changes can propagate from node"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return 0
        
        try:
            # Use longest path algorithm
            longest = nx.dag_longest_path_length(G, node_id)
            return longest
        except (nx.NetworkXError, nx.NodeNotFound):
            return 0
    
    def find_circular_dependencies(self, graph_id: str) -> List[List[str]]:
        """Find all circular dependencies for phase 41 handling"""
        G = self.load_graph(graph_id)
        if not G:
            return []
        
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except Exception as e:  # TODO (2026-03-08): specify exception type
            return []
    
    def get_critical_path(self, graph_id: str, source: str, target: str) -> Optional[List[str]]:
        """Find critical path from source to target for Phase 41"""
        G = self.load_graph(graph_id)
        if not G:
            return None
        
        try:
            path = nx.shortest_path(G, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_strongly_connected_components(self, graph_id: str) -> List[Set[str]]:
        """Find groups of mutually dependent nodes"""
        G = self.load_graph(graph_id)
        if not G:
            return []
        
        return list(nx.strongly_connected_components(G))
    
    def analyze_node(self, graph_id: str, node_id: str) -> Dict:
        """Get comprehensive analysis of a node"""
        G = self.load_graph(graph_id)
        if not G or node_id not in G:
            return {}
        
        return {
            'node_id': node_id,
            'type': G.nodes[node_id].get('type'),
            'in_degree': G.in_degree(node_id),
            'out_degree': G.out_degree(node_id),
            'direct_dependencies': list(self.get_dependencies(graph_id, node_id)),
            'direct_dependents': list(self.get_dependents(graph_id, node_id)),
            'transitive_dependencies': list(self.get_transitive_dependencies(graph_id, node_id)),
            'transitive_dependents': list(self.get_transitive_dependents(graph_id, node_id)),
            'impact_radius': self.get_impact_radius(graph_id, node_id),
            'is_leaf': G.out_degree(node_id) == 0,
            'is_root': G.in_degree(node_id) == 0,
            'metadata': G.nodes[node_id],
        }
    
    def delete_graph(self, graph_id: str) -> None:
        """Delete graph from storage"""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM graph_edges WHERE graph_id = ?', (graph_id,))
        cursor.execute('DELETE FROM graph_nodes WHERE graph_id = ?', (graph_id,))
        cursor.execute('DELETE FROM graphs WHERE graph_id = ?', (graph_id,))
        
        conn.commit()
        conn.close()
    
    def list_graphs(self) -> List[Dict]:
        """List all stored graphs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT graph_id, repo_id, created_at, updated_at, node_count, edge_count FROM graphs')
        results = []
        for row in cursor.fetchall():
            results.append({
                'graph_id': row[0],
                'repo_id': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'node_count': row[4],
                'edge_count': row[5],
            })
        
        conn.close()
        return results
