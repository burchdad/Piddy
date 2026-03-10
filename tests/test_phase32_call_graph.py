"""
Tests for Phase 32a: Call Graph Engine

Comprehensive test suite covering:
- AST extraction for function definitions and calls
- Call graph database persistence
- Impact radius calculation
- Circular dependency detection
- Query operations
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

# Import the modules to test
import sys
sys.path.insert(0, '/workspaces/Piddy/src')

from phase32_call_graph_engine import (
import asyncio
    PythonCallGraphExtractor,
    CallGraphDB,
    ImpactAnalyzer,
    CallGraphBuilder,
    FunctionSignature,
    CallEdge,
    CallType,
    ImpactRadius
)


class TestPythonCallGraphExtractor:
    """Test AST extraction of functions and calls"""

    def test_extract_simple_function(self, tmp_path):
        """Extract a simple function definition"""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        assert len(functions) == 1
        func = list(functions.values())[0]
        assert func.name == "add"
        assert len(func.parameters) == 2
        assert func.parameters[0]["name"] == "a"
        assert func.parameters[0]["type"] == "int"
        assert func.return_type == "int"

    def test_extract_function_call(self, tmp_path):
        """Extract function call relationships"""
        code = """
def add(a, b):
    return a + b

def compute():
    result = add(1, 2)
    return result
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        assert len(functions) == 2
        assert len(calls) >= 1
        
        # Find the call from compute to add
        add_calls = [c for c in calls if c.target_func_id == "add"]
        assert len(add_calls) > 0

    def test_extract_recursive_function(self, tmp_path):
        """Detect recursive functions"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        func = list(functions.values())[0]
        assert func.is_recursive

    def test_extract_async_function(self, tmp_path):
        """Extract async function and calls"""
        code = """
async def fetch_data():
    result = await get_api_data()
    return result

async def get_api_data():
    return {"data": "test"}
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        assert len(functions) == 2
        assert any(f.is_async for f in functions.values())

    def test_extract_class_methods(self, tmp_path):
        """Extract class method definitions"""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        assert len(functions) >= 2

    def test_extract_multiple_calls(self, tmp_path):
        """Extract multiple calls from one function"""
        code = """
def orchestrate():
    a = do_step_1()
    b = do_step_2()
    c = do_step_3()
    return combine(a, b, c)

def do_step_1():
    return 1

def do_step_2():
    return 2

def do_step_3():
    return 3

def combine(a, b, c):
    return a + b + c
"""
        py_file = tmp_path / "test.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        # Should have 5 functions and 4 calls
        assert len(functions) >= 5
        assert len(calls) >= 4

    def test_syntax_error_handling(self, tmp_path):
        """Handle files with syntax errors gracefully"""
        code = """
def broken(
    # Missing closing paren
"""
        py_file = tmp_path / "broken.py"
        py_file.write_text(code)

        extractor = PythonCallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()

        # Should return empty results, not crash
        assert functions == {}
        assert calls == []


class TestCallGraphDB:
    """Test database persistence layer"""

    def test_init_database(self, tmp_path):
        """Initialize database schema"""
        db_path = str(tmp_path / "test.db")
        db = CallGraphDB(db_path)

        # Verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='call_graphs'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_add_call_edges(self, tmp_path):
        """Add call edges to database"""
        db_path = str(tmp_path / "test.db")
        db = CallGraphDB(db_path)

        edge = CallEdge(
            call_id="call_1",
            source_func_id="func_a",
            target_func_id="func_b",
            call_type=CallType.DIRECT,
            parameter_types=["int", "str"],
            return_type="bool",
            line_number=10
        )

        count = db.add_call_edges([edge])
        assert count == 1

        # Verify it was stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM call_graphs WHERE call_graph_id = ?", ("call_1",))
        row = cursor.fetchone()
        assert row is not None
        conn.close()

    def test_update_statistics(self, tmp_path):
        """Update call statistics"""
        db_path = str(tmp_path / "test.db")
        
        # Create nodes table (from Phase 28)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        cursor.execute("INSERT INTO nodes VALUES ('func_a', 'function', 'a', '/test.py')")
        cursor.execute("INSERT INTO nodes VALUES ('func_b', 'function', 'b', '/test.py')")
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)

        # Add edges
        edge = CallEdge(
            call_id="call_1",
            source_func_id="func_a",
            target_func_id="func_b",
            call_type=CallType.DIRECT
        )
        db.add_call_edges([edge])

        # Update statistics
        count = db.update_statistics()
        assert count >= 0


class TestImpactAnalyzer:
    """Test impact analysis functionality"""

    def test_calculate_impact_radius_no_callers(self, tmp_path):
        """Calculate impact for function with no callers"""
        db_path = str(tmp_path / "test.db")
        db = CallGraphDB(db_path)

        analyzer = ImpactAnalyzer(db)
        impact = analyzer.calculate_impact_radius("func_a")

        assert impact.direct_callers == 0
        assert impact.indirect_callers == 0
        assert impact.risk_level == "low"

    def test_calculate_impact_radius_direct_callers(self, tmp_path):
        """Calculate impact with direct callers"""
        db_path = str(tmp_path / "test.db")
        
        # Setup nodes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        for i in range(6):
            cursor.execute(
                "INSERT INTO nodes VALUES (?, 'function', 'func', '/test.py')",
                (f"func_{i}",)
            )
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)

        # Add edges: func_1 to func_5 all call func_0
        edges = [
            CallEdge(
                call_id=f"call_{i}",
                source_func_id=f"func_{i}",
                target_func_id="func_0",
                call_type=CallType.DIRECT
            )
            for i in range(1, 6)
        ]
        db.add_call_edges(edges)

        analyzer = ImpactAnalyzer(db)
        impact = analyzer.calculate_impact_radius("func_0")

        assert impact.direct_callers == 5
        assert impact.risk_level == "medium"

    def test_is_safe_to_delete_no_callers(self, tmp_path):
        """Check if function with no callers can be deleted"""
        db_path = str(tmp_path / "test.db")
        db = CallGraphDB(db_path)

        analyzer = ImpactAnalyzer(db)
        safe, message = analyzer.is_safe_to_delete("func_a")

        assert safe is True
        assert "No callers" in message

    def test_find_cycles_no_cycles(self, tmp_path):
        """Detect cycles when none exist"""
        db_path = str(tmp_path / "test.db")
        db = CallGraphDB(db_path)

        analyzer = ImpactAnalyzer(db)
        cycles = analyzer.find_cycles()

        assert len(cycles) == 0

    def test_find_simple_cycle(self, tmp_path):
        """Detect simple circular dependency"""
        db_path = str(tmp_path / "test.db")
        
        # Setup nodes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        cursor.execute("INSERT INTO nodes VALUES ('func_a', 'function', 'a', '/test.py')")
        cursor.execute("INSERT INTO nodes VALUES ('func_b', 'function', 'b', '/test.py')")
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)

        # Create cycle: a -> b -> a
        edges = [
            CallEdge(
                call_id="call_1",
                source_func_id="func_a",
                target_func_id="func_b",
                call_type=CallType.DIRECT
            ),
            CallEdge(
                call_id="call_2",
                source_func_id="func_b",
                target_func_id="func_a",
                call_type=CallType.DIRECT
            )
        ]
        db.add_call_edges(edges)

        analyzer = ImpactAnalyzer(db)
        cycles = analyzer.find_cycles()

        assert len(cycles) > 0


class TestIntegration:
    """Integration tests combining multiple components"""

    def test_full_workflow_simple_repo(self, tmp_path):
        """Test complete workflow from extraction to analysis"""
        # Create a simple Python module
        module_file = tmp_path / "module.py"
        module_file.write_text('''
def function_a():
    return function_b()

def function_b():
    return function_c()

def function_c():
    return 42
''')

        # Extract call graph
        extractor = PythonCallGraphExtractor(str(module_file))
        functions, calls = extractor.extract()

        assert len(functions) == 3
        assert len(calls) == 2

        # Store in database
        db_path = str(tmp_path / "test.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)
        db.add_call_edges(calls)

        # Analyze impact
        analyzer = ImpactAnalyzer(db)
        
        # Get first function
        first_func_id = list(functions.keys())[0]
        impact = analyzer.calculate_impact_radius(first_func_id)

        assert impact.total_affected >= 0

    def test_full_workflow_with_cycles(self, tmp_path):
        """Test workflow detecting circular dependencies"""
        module_file = tmp_path / "module.py"
        module_file.write_text('''
def service_a():
    return service_b()

def service_b():
    return service_a()
''')

        extractor = PythonCallGraphExtractor(str(module_file))
        functions, calls = extractor.extract()

        db_path = str(tmp_path / "test.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)
        db.add_call_edges(calls)

        analyzer = ImpactAnalyzer(db)
        cycles = analyzer.find_cycles()

        assert len(cycles) > 0


# Performance benchmark tests (optional)
class TestPerformance:
    """Performance characteristics"""

    def test_query_performance_large_graph(self, tmp_path):
        """Ensure queries are fast on large graphs"""
        db_path = str(tmp_path / "large.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT
            )
        ''')
        
        # Create 1000 nodes
        for i in range(1000):
            cursor.execute(
                "INSERT INTO nodes VALUES (?, 'function', 'func', '/test.py')",
                (f"func_{i}",)
            )
        conn.commit()
        conn.close()

        db = CallGraphDB(db_path)

        # Add 5000 edges
        import time
        start = time.time()
        
        edges = []
        for i in range(5000):
            edge = CallEdge(
                call_id=f"call_{i}",
                source_func_id=f"func_{i % 500}",
                target_func_id=f"func_{(i + 1) % 500}",
                call_type=CallType.DIRECT
            )
            edges.append(edge)
        
        db.add_call_edges(edges)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 10.0  # 5000 edges in < 10 seconds

        # Test query performance
        start = time.time()
        analyzer = ImpactAnalyzer(db)
        analyzer.calculate_impact_radius("func_0")
        query_time = time.time() - start

        assert query_time < 1.0  # Query should be < 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
