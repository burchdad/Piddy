"""
Phase 39: Impact Graph Visualization
Visualizes dependency graphs to show impact of changes

Integrates with:
- Phase 32/33: RKG for building graphs
- Phase 38: LLM planning context
- Infrastructure: Graph store for persistence
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from src.infrastructure.graph_store import DependencyGraphStore, GraphNode, GraphEdge


class ImpactLevel(Enum):
    """Impact levels for dependency changes"""
    NONE = 0              # No impact
    MINIMAL = 1           # Affects 1-2 nodes
    LOW = 2               # Affects 3-10 nodes
    MEDIUM = 3            # Affects 11-50 nodes
    HIGH = 4              # Affects 51-200 nodes
    CRITICAL = 5          # Affects 200+ nodes


@dataclass
class ImpactAnalysis:
    """Analysis of impact for a change"""
    node_id: str
    direct_dependents: Set[str]          # Direct downstream
    transitive_dependents: Set[str]      # Full downstream impact
    direct_dependencies: Set[str]        # Direct upstream
    transitive_dependencies: Set[str]    # Full upstream impact
    total_impact_count: int              # Total nodes affected
    impact_level: ImpactLevel            # Severity classification
    impact_percentage: float             # % of codebase affected
    risky_patterns: List[str]            # Known risky patterns detected
    

@dataclass
class ImpactVisualization:
    """Visualization metadata for display"""
    node_id: str
    node_type: str
    change_type: str                     # "modified", "added", "deleted"
    
    # Graph structure
    direct_dependencies: List[Dict]      # For rendering
    direct_dependents: List[Dict]        # For rendering
    
    # Metrics
    impact_score: float                  # 0-1, higher = more risky
    confidence: float                    # Prediction confidence
    
    # Rendering hints
    node_size: str                       # "small", "medium", "large"
    node_color: str                      # Risk color
    warning_level: str                   # "none", "warn", "critical"


class ImpactGraphVisualizer:
    """Visualizes dependency graphs and impact analysis"""
    
    def __init__(self, graph_store: DependencyGraphStore):
        """Initialize visualizer with graph store"""
        self.graph_store = graph_store
        self.cache: Dict = {}
    
    def analyze_change(self, graph_id: str, changed_node_id: str) -> ImpactAnalysis:
        """Analyze impact of changing a single node"""
        
        # Get all relationships
        direct_dependents = self.graph_store.get_dependents(graph_id, changed_node_id)
        transitive_dependents = self.graph_store.get_transitive_dependents(graph_id, changed_node_id)
        direct_dependencies = self.graph_store.get_dependencies(graph_id, changed_node_id)
        transitive_dependencies = self.graph_store.get_transitive_dependencies(graph_id, changed_node_id)
        
        # Calculate metrics
        total_impact = len(transitive_dependents)
        
        # Estimate codebase size (conservative estimate)
        G = self.graph_store.load_graph(graph_id)
        codebase_size = G.number_of_nodes() if G else 1
        impact_percentage = (total_impact / codebase_size * 100) if codebase_size > 0 else 0
        
        # Classify impact level
        impact_level = self._classify_impact(total_impact)
        
        # Detect risky patterns
        risky_patterns = self._detect_risky_patterns(
            graph_id, changed_node_id, direct_dependents, transitive_dependents
        )
        
        return ImpactAnalysis(
            node_id=changed_node_id,
            direct_dependents=direct_dependents,
            transitive_dependents=transitive_dependents,
            direct_dependencies=direct_dependencies,
            transitive_dependencies=transitive_dependencies,
            total_impact_count=total_impact,
            impact_level=impact_level,
            impact_percentage=impact_percentage,
            risky_patterns=risky_patterns,
        )
    
    def analyze_multi_change(self, graph_id: str, changed_node_ids: List[str]) -> Dict:
        """Analyze impact of changing multiple nodes"""
        
        all_analyses = {}
        combined_impact = set()
        
        for node_id in changed_node_ids:
            analysis = self.analyze_change(graph_id, node_id)
            all_analyses[node_id] = analysis
            combined_impact.update(analysis.transitive_dependents)
        
        # Calculate combined metrics
        combined_impact_level = self._classify_impact(len(combined_impact))
        
        # Check for cascading effects
        cascading_issues = self._detect_cascading_effects(all_analyses, combined_impact)
        
        return {
            'analyses': {k: self._analysis_to_dict(v) for k, v in all_analyses.items()},
            'combined_impact_count': len(combined_impact),
            'combined_impact_level': combined_impact_level.name,
            'affected_nodes': list(combined_impact),
            'cascading_issues': cascading_issues,
            'recommendation': self._generate_recommendation(combined_impact_level, cascading_issues),
        }
    
    def create_visualization(self, analysis: ImpactAnalysis, 
                            change_type: str = "modified") -> ImpactVisualization:
        """Create visualization data from analysis"""
        
        # Calculate metrics
        impact_score = min(analysis.impact_percentage / 100.0, 1.0)
        confidence = self._estimate_confidence(analysis)
        
        # Determine visualization properties
        node_size = self._size_from_impact(analysis.total_impact_count)
        node_color = self._color_from_impact(analysis.impact_level)
        warning_level = self._warning_level(analysis.impact_level)
        
        # Format dependencies for rendering
        direct_deps = [
            {
                'id': dep_id,
                'type': 'dependency',
                'direction': 'upstream',
            }
            for dep_id in list(analysis.direct_dependencies)[:10]  # Top 10
        ]
        
        direct_dependents = [
            {
                'id': dep_id,
                'type': 'dependent',
                'direction': 'downstream',
            }
            for dep_id in list(analysis.direct_dependents)[:10]  # Top 10
        ]
        
        return ImpactVisualization(
            node_id=analysis.node_id,
            node_type="unknown",
            change_type=change_type,
            direct_dependencies=direct_deps,
            direct_dependents=direct_dependents,
            impact_score=impact_score,
            confidence=confidence,
            node_size=node_size,
            node_color=node_color,
            warning_level=warning_level,
        )
    
    def export_json(self, visualization: ImpactVisualization) -> str:
        """Export visualization as JSON"""
        return json.dumps({
            'node_id': visualization.node_id,
            'node_type': visualization.node_type,
            'change_type': visualization.change_type,
            'direct_dependencies': visualization.direct_dependencies,
            'direct_dependents': visualization.direct_dependents,
            'impact_score': visualization.impact_score,
            'confidence': visualization.confidence,
            'node_size': visualization.node_size,
            'node_color': visualization.node_color,
            'warning_level': visualization.warning_level,
            'timestamp': datetime.utcnow().isoformat(),
        }, indent=2)
    
    def export_svg(self, visualization: ImpactVisualization) -> str:
        """Export visualization as SVG graph"""
        
        # Create SVG structure
        svg_parts = [
            '<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '.node { stroke: #333; stroke-width: 2; }',
            '.edge { stroke: #999; stroke-width: 1; }',
            '.label { font-family: Arial; font-size: 12px; }',
            '.critical { fill: #ff4444; }',
            '.high { fill: #ff8844; }',
            '.medium { fill: #ffcc44; }',
            '.low { fill: #44ff44; }',
            '</style>',
        ]
        
        # Add central node
        node_class = visualization.warning_level
        svg_parts.append(
            f'<circle cx="400" cy="300" r="30" class="node {node_class}" />'
        )
        svg_parts.append(
            f'<text x="400" y="305" text-anchor="middle" class="label">'
            f'{visualization.node_id}</text>'
        )
        
        # Add dependent nodes
        deps = visualization.direct_dependents
        for i, dep in enumerate(deps[:6]):
            angle = (i / 6) * 2 * 3.14159
            x = 400 + 150 * math.cos(angle)
            y = 300 + 150 * math.sin(angle)
            
            svg_parts.append(f'<line x1="400" y1="300" x2="{x}" y2="{y}" class="edge" />')
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="15" class="node low" />')
            svg_parts.append(
                f'<text x="{x}" y="{y+3}" text-anchor="middle" class="label">'
                f'{dep.get("id", "")[:10]}</text>'
            )
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def export_html_report(self, analysis: ImpactAnalysis, 
                          visualization: ImpactVisualization) -> str:
        """Export as HTML report"""
        
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Impact Analysis Report</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }',
            '.report { background: white; padding: 20px; border-radius: 8px; }',
            '.metric { display: inline-block; margin: 10px 20px 10px 0; }',
            '.metric-value { font-size: 24px; font-weight: bold; color: #333; }',
            '.metric-label { font-size: 12px; color: #666; }',
            '.warning { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }',
            '.critical { background: #f8d7da; padding: 10px; border-left: 4px solid #f44; margin: 10px 0; }',
            '.recommendations { background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin: 10px 0; }',
            '.nodes-list { background: #f9f9f9; padding: 10px; max-height: 300px; overflow-y: auto; }',
            '</style>',
            '</head>',
            '<body>',
            '<div class="report">',
            f'<h1>Impact Analysis: {analysis.node_id}</h1>',
            '<div class="metrics">',
            f'<div class="metric"><div class="metric-value">{analysis.total_impact_count}</div><div class="metric-label">Total Impact</div></div>',
            f'<div class="metric"><div class="metric-value">{analysis.impact_level.name}</div><div class="metric-label">Impact Level</div></div>',
            f'<div class="metric"><div class="metric-value">{analysis.impact_percentage:.1f}%</div><div class="metric-label">% of Codebase</div></div>',
            '</div>',
        ]
        
        # Add warnings
        if analysis.risky_patterns:
            html_parts.append('<div class="warning">')
            html_parts.append('<strong>Risky Patterns Detected:</strong>')
            for pattern in analysis.risky_patterns:
                html_parts.append(f'<div>• {pattern}</div>')
            html_parts.append('</div>')
        
        # Add affected nodes
        html_parts.append('<h2>Directly Dependent Nodes</h2>')
        html_parts.append('<div class="nodes-list">')
        for node in list(analysis.direct_dependents)[:20]:
            html_parts.append(f'<div>• {node}</div>')
        if len(analysis.direct_dependents) > 20:
            html_parts.append(f'<div>... and {len(analysis.direct_dependents) - 20} more</div>')
        html_parts.append('</div>')
        
        # Add recommendations
        html_parts.append('<div class="recommendations">')
        html_parts.append('<strong>Recommendations:</strong>')
        if analysis.impact_level == ImpactLevel.CRITICAL:
            html_parts.append('<div>⚠️ HIGH RISK: Requires thorough review and testing</div>')
        elif analysis.impact_level == ImpactLevel.HIGH:
            html_parts.append('<div>⚠️ Recommend additional testing for downstream nodes</div>')
        else:
            html_parts.append('<div>✅ Low risk - standard review sufficient</div>')
        html_parts.append('</div>')
        
        html_parts.extend([
            '</div>',
            '</body>',
            '</html>',
        ])
        
        return '\n'.join(html_parts)
    
    # Private helper methods
    
    def _classify_impact(self, impact_count: int) -> ImpactLevel:
        """Classify impact level based on count"""
        if impact_count == 0:
            return ImpactLevel.NONE
        elif impact_count <= 2:
            return ImpactLevel.MINIMAL
        elif impact_count <= 10:
            return ImpactLevel.LOW
        elif impact_count <= 50:
            return ImpactLevel.MEDIUM
        elif impact_count <= 200:
            return ImpactLevel.HIGH
        else:
            return ImpactLevel.CRITICAL
    
    def _detect_risky_patterns(self, graph_id: str, node_id: str,
                              direct_dependents: Set[str],
                              transitive_dependents: Set[str]) -> List[str]:
        """Detect risky patterns in dependencies"""
        patterns = []
        
        # Check for circular dependencies
        G = self.graph_store.load_graph(graph_id)
        if G:
            cycles = self.graph_store.find_circular_dependencies(graph_id)
            for cycle in cycles:
                if node_id in cycle:
                    patterns.append("Circular dependency detected")
                    break
        
        # Check for fan-out (many dependents)
        if len(direct_dependents) > 50:
            patterns.append("High fan-out (many nodes depend on this)")
        
        # Check for deep cascading
        if len(transitive_dependents) > len(direct_dependents) * 5:
            patterns.append("Deep cascading impact - changes propagate far")
        
        return patterns
    
    def _detect_cascading_effects(self, analyses: Dict, combined_impact: Set) -> List[str]:
        """Detect potential cascading effects"""
        cascading = []
        
        # Check for nodes with very high impact
        high_impact_nodes = [
            node_id for node_id, analysis in analyses.items()
            if analysis.impact_level.value >= ImpactLevel.HIGH.value
        ]
        
        if len(high_impact_nodes) > 1:
            cascading.append("Multiple high-impact changes detected - risk of cascading failures")
        
        return cascading
    
    def _estimate_confidence(self, analysis: ImpactAnalysis) -> float:
        """Estimate confidence in the analysis"""
        confidence = 0.7  # Start with baseline
        
        # More risky patterns = less confident
        confidence -= len(analysis.risky_patterns) * 0.1
        
        # Very high impact = less confident in prediction
        if analysis.impact_level == ImpactLevel.CRITICAL:
            confidence -= 0.2
        
        return max(confidence, 0.3)  # Never below 0.3
    
    def _size_from_impact(self, impact_count: int) -> str:
        """Determine node size from impact count"""
        if impact_count < 5:
            return "small"
        elif impact_count < 20:
            return "medium"
        else:
            return "large"
    
    def _color_from_impact(self, impact_level: ImpactLevel) -> str:
        """Determine node color from impact level"""
        colors = {
            ImpactLevel.NONE: "#44ff44",
            ImpactLevel.MINIMAL: "#88ff44",
            ImpactLevel.LOW: "#ccff44",
            ImpactLevel.MEDIUM: "#ffcc44",
            ImpactLevel.HIGH: "#ff8844",
            ImpactLevel.CRITICAL: "#ff4444",
        }
        return colors.get(impact_level, "#999999")
    
    def _warning_level(self, impact_level: ImpactLevel) -> str:
        """Determine warning level from impact"""
        if impact_level.value >= ImpactLevel.CRITICAL.value:
            return "critical"
        elif impact_level.value >= ImpactLevel.HIGH.value:
            return "warn"
        else:
            return "none"
    
    def _generate_recommendation(self, impact_level: ImpactLevel, 
                                 cascading_issues: List[str]) -> str:
        """Generate recommendation based on impact"""
        if cascading_issues:
            return "REJECT: Cascading effects detected - requires redesign"
        elif impact_level == ImpactLevel.CRITICAL:
            return "REQUIRES APPROVAL: Higher risk - needs senior review"
        elif impact_level == ImpactLevel.HIGH:
            return "CAUTION: Wide impact - recommend manual review"
        elif impact_level == ImpactLevel.MEDIUM:
            return "RECOMMEND: Automated approval with monitoring"
        else:
            return "SAFE: Can proceed with automation"
    
    def _analysis_to_dict(self, analysis: ImpactAnalysis) -> Dict:
        """Convert analysis to dictionary"""
        return {
            'node_id': analysis.node_id,
            'direct_dependents': len(analysis.direct_dependents),
            'transitive_dependents': len(analysis.transitive_dependents),
            'direct_dependencies': len(analysis.direct_dependencies),
            'transitive_dependencies': len(analysis.transitive_dependencies),
            'total_impact_count': analysis.total_impact_count,
            'impact_level': analysis.impact_level.name,
            'impact_percentage': analysis.impact_percentage,
            'risky_patterns': analysis.risky_patterns,
        }


# Import for compatibility
import math
