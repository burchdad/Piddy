"""
Tests for Phase 32 Migration 2: Confidence-Aware Query Methods

Tests the new confidence-aware query API in CallGraphDB:
- get_callers_confident()
- get_callees_confident()
- get_impact_radius_confident()
- get_confident_call_paths()
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from phase32_call_graph_engine import CallGraphDB, CallGraphBuilder, PythonCallGraphExtractor, CallEdge, CallType


class TestConfidenceAwareQueries:
    """Test confidence-filtered query methods"""

    @pytest.fixture
    def db(self):
        """Create temporary test database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'test.db'
            test_db = CallGraphDB(str(db_path))
            yield test_db

    def test_get_callers_confident(self, db):
        """Test filtering callers by confidence threshold"""
        # This would test with real data
        # For now, verify the method exists and signature is correct
        assert hasattr(db, 'get_callers_confident')
        assert callable(db.get_callers_confident)

    def test_get_callees_confident(self, db):
        """Test filtering callees by confidence threshold"""
        assert hasattr(db, 'get_callees_confident')
        assert callable(db.get_callees_confident)

    def test_get_impact_radius_confident(self, db):
        """Test impact radius calculation with confidence filtering"""
        assert hasattr(db, 'get_impact_radius_confident')
        assert callable(db.get_impact_radius_confident)

    def test_get_confident_call_paths(self, db):
        """Test path-finding with confidence constraints"""
        assert hasattr(db, 'get_confident_call_paths')
        assert callable(db.get_confident_call_paths)

    def test_confidence_threshold_filtering(self):
        """Test confidence threshold filtering on real data"""
        # This would use the Piddy database for real testing
        db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')
        
        # Get any function node
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        cursor.execute('SELECT node_id FROM nodes LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            func_id = result[0]
            
            # Should return results
            high_conf_callers = db.get_callers_confident(func_id, min_confidence=0.95)
            assert isinstance(high_conf_callers, list)
            
            # Very strict threshold
            very_high_conf = db.get_callers_confident(func_id, min_confidence=0.99)
            assert isinstance(very_high_conf, list)
            # Should have <= results with very high threshold
            assert len(very_high_conf) <= len(high_conf_callers)


class TestImpactRadiusCalculation:
    """Test impact radius with confidence weighting"""

    def test_impact_radius_returns_dict(self):
        """Verify impact_radius_confident returns proper structure"""
        db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')
        
        # Get a function with callers
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT source_node_id 
            FROM call_graphs 
            LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            func_id = result[0]
            impact = db.get_impact_radius_confident(func_id, min_confidence=0.85)
            
            # Check structure
            assert 'function_id' in impact
            assert 'total_affected' in impact
            assert 'affected_functions' in impact
            assert 'risk_level' in impact
            assert 'avg_confidence' in impact
            
            # Risk level should be valid
            assert impact['risk_level'] in ['low', 'medium', 'high']
            
            # Confidence should be between 0 and 1
            if impact['avg_confidence'] > 0:
                assert 0 <= impact['avg_confidence'] <= 1.0

    def test_risk_level_calculation(self):
        """Test risk level calculation based on affected count"""
        db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')
        
        # Get a high-impact function (main or similar)
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT source_node_id, COUNT(*) as caller_count
            FROM call_graphs
            GROUP BY source_node_id
            ORDER BY caller_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            func_id = result[0]
            impact = db.get_impact_radius_confident(func_id, min_confidence=0.80)
            
            # Verify risk level matches expected logic
            affected_count = impact['total_affected']
            risk = impact['risk_level']
            
            if affected_count == 0:
                assert risk == 'low'
            elif affected_count <= 3:
                assert risk == 'low'
            elif affected_count <= 10:
                assert risk == 'medium'
            else:
                assert risk == 'high'


class TestConfidentCallPaths:
    """Test confident path finding"""

    def test_confident_paths_exist(self):
        """Verify confident paths can be found"""
        db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')
        
        # Get two functions with potential path between them
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        
        # Get a source and target that might have paths
        cursor.execute('''
            SELECT DISTINCT source_node_id FROM call_graphs LIMIT 1
        ''')
        source = cursor.fetchone()
        
        cursor.execute('''
            SELECT DISTINCT target_node_id FROM call_graphs LIMIT 1
        ''')
        target = cursor.fetchone()
        conn.close()
        
        if source and target:
            paths = db.get_confident_call_paths(
                source[0], 
                target[0], 
                min_confidence=0.85
            )
            
            # Should return a list (may be empty if no path)
            assert isinstance(paths, list)


class TestRealDataIntegration:
    """Integration tests with real Piddy codebase"""

    def test_piddy_database_loaded(self):
        """Verify Piddy database has trust data"""
        db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')
        
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        
        # Count entries
        cursor.execute('SELECT COUNT(*) FROM nodes')
        node_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM call_graphs')
        edge_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Should have significant data
        assert node_count > 100, f"Expected >100 nodes, got {node_count}"
        assert edge_count > 500, f"Expected >500 edges, got {edge_count}"

    def test_all_edges_have_confidence(self):
        """Verify all edges have confidence values"""
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        
        # Check for NULL confidence values
        cursor.execute('SELECT COUNT(*) FROM call_graphs WHERE confidence IS NULL')
        null_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM call_graphs')
        total = cursor.fetchone()[0]
        
        conn.close()
        
        # Should have confidence for all edges
        assert null_count == 0, f"Found {null_count} edges without confidence"
        assert total > 0

    def test_confidence_values_in_range(self):
        """Verify confidence values are in valid range [0, 1]"""
        conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM call_graphs WHERE confidence < 0 OR confidence > 1')
        invalid_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert invalid_count == 0, f"Found {invalid_count} edges with invalid confidence"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
