"""
Tests for Phase 32: Node Identity Stability

Comprehensive tests for:
1. Migration execution
2. Qualified name computation
3. Signature hash generation
4. Node stability across refactors
5. Confidence scoring setup
"""

import unittest
import tempfile
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from phase32_migrations import Phase32Migrations, NodeIdentityBuilder, run_migration
from phase32_call_graph_engine import CallGraphDB


class TestMigration1NodeIdentity(unittest.TestCase):
    """Test Node Identity Stability (Migration 1)"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.repo_path = Path(self.temp_dir.name)
        
        # Initialize database with Phase28-compatible schema
        self._init_test_schema()

    def tearDown(self):
        """Clean up temporary files"""
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()

    def _init_test_schema(self):
        """Initialize test database with base schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create nodes table (from Phase 28)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT,
                language TEXT DEFAULT 'python',
                lines_of_code INTEGER DEFAULT 0,
                complexity REAL DEFAULT 0.5,
                last_modified TEXT,
                metadata TEXT
            )
        ''')
        
        # Create call_graphs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_graphs (
                call_graph_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'direct',
                is_recursive BOOLEAN DEFAULT 0,
                is_circular BOOLEAN DEFAULT 0,
                parameter_types TEXT,
                return_type TEXT,
                type_compatibility_score REAL DEFAULT 1.0,
                call_frequency INT DEFAULT 1,
                execution_time_ms REAL,
                call_line_number INT,
                is_deprecated BOOLEAN DEFAULT 0,
                first_observed TEXT,
                last_observed TEXT,
                FOREIGN KEY (source_node_id) REFERENCES nodes(node_id),
                FOREIGN KEY (target_node_id) REFERENCES nodes(node_id),
                UNIQUE(source_node_id, target_node_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def test_migration_1_adds_columns(self):
        """Test that migration 1 adds all required columns"""
        # Apply migration
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        # Verify columns exist
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check nodes table columns
        cursor.execute("PRAGMA table_info(nodes)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_node_columns = {
            'repo_id', 'qualified_name', 'signature_hash', 'stable_id',
            'created_at', 'last_seen', 'is_deprecated'
        }
        
        missing = required_node_columns - columns
        self.assertEqual(len(missing), 0, f"Missing nodes columns: {missing}")
        
        # Check call_graphs table columns
        cursor.execute("PRAGMA table_info(call_graphs)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_call_columns = {
            'source_stable_id', 'target_stable_id'
        }
        
        missing = required_call_columns - columns
        self.assertEqual(len(missing), 0, f"Missing call_graphs columns: {missing}")
        
        conn.close()

    def test_compute_qualified_names(self):
        """Test qualified name computation for functions"""
        # Create test Python file
        test_file = self.repo_path / "test_module.py"
        test_file.write_text('''
def hello_world(name: str) -> str:
    """Say hello"""
    return f"Hello {name}"

def calculate_sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

class Calculator:
    def add(self, x: int, y: int) -> int:
        return x + y
''')
        
        # Insert test nodes
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func1', 'function', 'hello_world', str(test_file), 'python'))
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func2', 'function', 'calculate_sum', str(test_file), 'python'))
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('class1', 'class', 'Calculator', str(test_file), 'python'))
        
        conn.commit()
        conn.close()
        
        # Apply migration and compute qualified names
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        builder = NodeIdentityBuilder(str(self.db_path), str(self.repo_path))
        processed, updated = builder.compute_qualified_names()
        
        self.assertGreater(processed, 0, "No files processed")
        self.assertGreater(updated, 0, "No nodes updated")
        
        # Verify qualified names were computed
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, qualified_name FROM nodes WHERE name = 'hello_world'")
        row = cursor.fetchone()
        self.assertIsNotNone(row, "hello_world node not found")
        self.assertIn('hello_world', row[1], f"Expected 'hello_world' in qualified name, got {row[1]}")
        
        conn.close()

    def test_signature_hash_prevents_collisions(self):
        """Test that signature hash prevents function name collisions"""
        # Create test Python files with same function names in different modules
        (self.repo_path / "module_a").mkdir(exist_ok=True)
        (self.repo_path / "module_b").mkdir(exist_ok=True)
        
        file_a = self.repo_path / "module_a" / "utils.py"
        file_a.write_text('''
def process(data: str) -> str:
    """Module A processor"""
    return data.upper()
''')
        
        file_b = self.repo_path / "module_b" / "utils.py"
        file_b.write_text('''
def process(data: int) -> int:
    """Module B processor"""
    return data * 2
''')
        
        # Insert both functions
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func_a', 'function', 'process', str(file_a), 'python'))
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func_b', 'function', 'process', str(file_b), 'python'))
        
        conn.commit()
        conn.close()
        
        # Apply migration
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        builder = NodeIdentityBuilder(str(self.db_path), str(self.repo_path))
        processed, updated = builder.compute_qualified_names()
        
        # Verify both have different stable IDs
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT node_id, stable_id FROM nodes WHERE name = 'process' ORDER BY node_id")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2, "Expected 2 'process' functions")
        
        stable_id_a = rows[0][1]
        stable_id_b = rows[1][1]
        
        self.assertNotEqual(stable_id_a, stable_id_b, 
                          "Same function name should have different stable IDs due to signature hash")
        
        # Verify both have 'process' in stable ID (from qualified name)
        self.assertIn('process', stable_id_a)
        self.assertIn('process', stable_id_b)
        
        conn.close()

    def test_node_stability_across_file_move(self):
        """Test that node IDs survive file movements"""
        # Create test file
        test_file = self.repo_path / "original_location.py"
        test_file.write_text('''
def important_function():
    return 42
''')
        
        # Insert node
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language, last_modified)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('func1', 'function', 'important_function', str(test_file), 'python', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Apply migration and compute qualified names
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        builder = NodeIdentityBuilder(str(self.db_path), str(self.repo_path))
        builder.compute_qualified_names()
        
        # Get stable ID before move
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT stable_id FROM nodes WHERE node_id = 'func1'")
        stable_id_before = cursor.fetchone()[0]
        conn.close()
        
        # Simulate file move: update path
        new_path = self.repo_path / "new_location.py"
        new_path.write_text(test_file.read_text())  # Copy content
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("UPDATE nodes SET path = ? WHERE node_id = 'func1'", (str(new_path),))
        conn.commit()
        conn.close()
        
        # Recompute qualified names
        builder.compute_qualified_names()
        
        # Get stable ID after move
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT stable_id FROM nodes WHERE node_id = 'func1'")
        stable_id_after = cursor.fetchone()[0]
        conn.close()
        
        # Verify stable ID remained the same (survived the move)
        self.assertEqual(stable_id_before, stable_id_after,
                        "Stable ID should not change when file moves")

    def test_node_stability_report(self):
        """Test node stability verification report"""
        # Create test nodes
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for i in range(5):
            cursor.execute("""
                INSERT INTO nodes (node_id, node_type, name, path, language)
                VALUES (?, ?, ?, ?, ?)
            """, (f'func{i}', 'function', f'func_{i}', f'/path/func_{i}.py', 'python'))
        
        conn.commit()
        conn.close()
        
        # Apply migration
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        builder = NodeIdentityBuilder(str(self.db_path), str(self.repo_path))
        stability = builder.verify_node_stability()
        
        # Verify report structure
        self.assertIn('total_nodes', stability)
        self.assertIn('with_stable_id', stability)
        self.assertIn('stability_percent', stability)
        self.assertIn('is_stable', stability)
        
        self.assertEqual(stability['total_nodes'], 5)

    def test_stable_id_uniqueness(self):
        """Test that stable IDs are truly unique"""
        # Create test file with multiple functions
        test_file = self.repo_path / "test.py"
        test_file.write_text('''
def func_a() -> str:
    return "a"

def func_b() -> int:
    return 1

async def func_c() -> bool:
    return True

def func_d(x: str, y: int) -> str:
    return x * y
''')
        
        # Insert nodes
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for i, name in enumerate(['func_a', 'func_b', 'func_c', 'func_d']):
            cursor.execute("""
                INSERT INTO nodes (node_id, node_type, name, path, language)
                VALUES (?, ?, ?, ?, ?)
            """, (f'func{i}', 'function', name, str(test_file), 'python'))
        
        conn.commit()
        conn.close()
        
        # Apply migration and populate
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_1_node_identity()
        
        builder = NodeIdentityBuilder(str(self.db_path), str(self.repo_path))
        builder.compute_qualified_names()
        
        # Verify all stable IDs are unique
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT stable_id, COUNT(*) as cnt
            FROM nodes
            WHERE stable_id IS NOT NULL
            GROUP BY stable_id
            HAVING cnt > 1
        """)
        
        duplicates = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(duplicates), 0, f"Found duplicate stable IDs: {duplicates}")


class TestMigration2ConfidenceScoring(unittest.TestCase):
    """Test Confidence Scoring (Migration 2)"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self._init_test_schema()

    def tearDown(self):
        """Clean up temporary files"""
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()

    def _init_test_schema(self):
        """Initialize test database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_graphs (
                call_graph_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'direct'
            )
        ''')
        
        conn.commit()
        conn.close()

    def test_migration_2_adds_confidence_columns(self):
        """Test that migration 2 adds confidence columns"""
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_2_confidence_scoring()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(call_graphs)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {
            'evidence_type', 'confidence', 'source', 'observed_count', 'last_verified'
        }
        self.assertTrue(required_columns.issubset(columns),
                       f"Missing columns: {required_columns - columns}")
        
        conn.close()

    def test_confidence_default_values(self):
        """Test that default confidence values are set"""
        migrator = Phase32Migrations(str(self.db_path))
        migrator.migration_2_confidence_scoring()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Insert test edge
        cursor.execute("""
            INSERT INTO call_graphs (call_graph_id, source_node_id, target_node_id, call_type)
            VALUES (?, ?, ?, ?)
        """, ('call1', 'func_a', 'func_b', 'direct'))
        
        conn.commit()
        
        # Verify defaults
        cursor.execute("SELECT evidence_type, confidence, source FROM call_graphs WHERE call_graph_id = 'call1'")
        row = cursor.fetchone()
        
        self.assertEqual(row[0], 'static', "Default evidence_type should be 'static'")
        self.assertEqual(row[1], 0.95, "Default confidence should be 0.95 for static edges")
        self.assertEqual(row[2], 'ast:call_node', "Default source should be 'ast:call_node'")
        
        conn.close()


class TestIntegrationMigrations(unittest.TestCase):
    """Integration tests for all migrations"""

    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.repo_path = Path(self.temp_dir.name)
        self._init_base_schema()

    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()

    def _init_base_schema(self):
        """Initialize Phase 28 base schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT,
                language TEXT DEFAULT 'python',
                lines_of_code INTEGER DEFAULT 0,
                complexity REAL DEFAULT 0.5,
                last_modified TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_graphs (
                call_graph_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'direct',
                is_recursive BOOLEAN DEFAULT 0,
                is_circular BOOLEAN DEFAULT 0,
                parameter_types TEXT,
                return_type TEXT,
                call_frequency INT DEFAULT 1,
                FOREIGN KEY (source_node_id) REFERENCES nodes(node_id),
                FOREIGN KEY (target_node_id) REFERENCES nodes(node_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def test_run_migration_complete_flow(self):
        """Test complete migration flow"""
        # Create test file
        test_file = self.repo_path / "sample.py"
        test_file.write_text('''
def main():
    return helper()

def helper():
    return 42
''')
        
        # Insert nodes
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func1', 'function', 'main', str(test_file), 'python'))
        
        cursor.execute("""
            INSERT INTO nodes (node_id, node_type, name, path, language)
            VALUES (?, ?, ?, ?, ?)
        """, ('func2', 'function', 'helper', str(test_file), 'python'))
        
        # Insert call edge
        cursor.execute("""
            INSERT INTO call_graphs (call_graph_id, source_node_id, target_node_id, call_type)
            VALUES (?, ?, ?, ?)
        """, ('call1', 'func1', 'func2', 'direct'))
        
        conn.commit()
        conn.close()
        
        # Run full migration
        stability = run_migration(str(self.db_path), str(self.repo_path))
        
        # Verify results
        self.assertGreater(stability['total_nodes'], 0)
        self.assertTrue(stability['is_stable'])

    def test_all_migrations_idempotent(self):
        """Test that migrations can be run multiple times safely"""
        migrator = Phase32Migrations(str(self.db_path))
        
        # Run migrations twice
        migrator.apply_migrations()
        migrator.apply_migrations()  # Should not error
        
        # Verify schema is intact
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = {'nodes', 'call_graphs', 'file_hashes', 'extraction_deltas'}
        self.assertTrue(required_tables.issubset(tables))
        
        conn.close()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
