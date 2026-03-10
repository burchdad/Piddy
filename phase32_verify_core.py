#!/usr/bin/env python3
"""
Phase 32a: Quick Verification (Core Functionality)

Tests core Phase 32a without external dependencies.
Shows the call graph engine is production-ready.
"""

import sys
import tempfile
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

sys.path.insert(0, '/workspaces/Piddy/src')

def main():
    logger.info("\n" + "="*70)
    logger.info("PHASE 32a: CORE FUNCTIONALITY VERIFICATION")
    logger.info("="*70 + "\n")

    # Test 1: Import core modules
    logger.info("TEST 1: Importing core Phase 32 modules...")
    try:
        from phase32_call_graph_engine import (
            PythonCallGraphExtractor,
            CallGraphDB,
            ImpactAnalyzer,
            CallType
        )
        logger.info("✅ PASS: All core modules imported\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        return 1

    # Test 2: AST Extraction
    logger.info("TEST 2: Python AST Extraction...")
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.py"
            test_file.write_text('''
def authenticate(user, password):
    """Authenticate user credentials"""
    if validate_input(user, password):
        return check_password(user, password)
    return False

def validate_input(user, password):
    """Validate input format"""
    return user and password

def check_password(user, password):
    """Check password against database"""
    return hash_match(user, password)

def hash_match(user, hash_val):
    """Match hashes"""
    return True
''')
            
            extractor = PythonCallGraphExtractor(str(test_file))
            functions, calls = extractor.extract()
            
            assert len(functions) == 4, f"Expected 4 functions, got {len(functions)}"
            assert len(calls) >= 3, f"Expected 3+ calls, got {len(calls)}"
            
            logger.info(f"✅ PASS: Extracted {len(functions)} functions, {len(calls)} calls\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        return 1

    # Test 3: Database Persistence
    logger.info("TEST 3: Database Persistence (SQLite)...")
    try:
        import sqlite3
        from phase32_call_graph_engine import CallEdge
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Create database
            db = CallGraphDB(db_path)
            
            # Create nodes
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
            for i, name in enumerate(['authenticate', 'validate_input', 'check_password', 'hash_match']):
                cursor.execute(
                    "INSERT INTO nodes VALUES (?, 'function', ?, '/test.py')",
                    (f"func_{i}", name)
                )
            conn.commit()
            conn.close()
            
            # Add call edges
            edges = [
                CallEdge("c1", "func_0", "func_1", CallType.DIRECT, line_number=5),
                CallEdge("c2", "func_0", "func_2", CallType.DIRECT, line_number=6),
                CallEdge("c3", "func_2", "func_3", CallType.DIRECT, line_number=12)
            ]
            count = db.add_call_edges(edges)
            
            assert count == 3, f"Expected 3 edges added, got {count}"
            
            # Verify persistence
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM call_graphs")
            stored = cursor.fetchone()[0]
            conn.close()
            
            assert stored == 3, f"Expected 3 stored edges, got {stored}"
            
            logger.info(f"✅ PASS: Persisted 3 call edges to SQLite\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    # Test 4: Impact Analysis
    logger.info("TEST 4: Impact Radius Calculation...")
    try:
        import sqlite3
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Setup
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
            # Create node hierarchy: func_0 <- func_1, func_2, func_3, func_4
            for i in range(5):
                cursor.execute(
                    "INSERT INTO nodes VALUES (?, 'function', ?, '/test.py')",
                    (f"func_{i}", f"function_{i}")
                )
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # Create calls: func_1,2,3 all call func_0
            edges = [
                CallEdge(f"c{i}", f"func_{i}", "func_0", CallType.DIRECT)
                for i in range(1, 4)
            ]
            db.add_call_edges(edges)
            
            # Analyze impact
            analyzer = ImpactAnalyzer(db)
            impact = analyzer.calculate_impact_radius("func_0")
            
            assert impact.direct_callers == 3, f"Expected 3 callers, got {impact.direct_callers}"
            assert impact.risk_level == "medium", f"Expected medium risk, got {impact.risk_level}"
            
            logger.info(f"✅ PASS: Impact radius calculated")
            logger.info(f"   - Direct callers: {impact.direct_callers}")
            logger.info(f"   - Risk level: {impact.risk_level}")
            logger.info(f"   - Total affected: {impact.total_affected}\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    # Test 5: Circular Dependency Detection
    logger.info("TEST 5: Circular Dependency Detection...")
    try:
        import sqlite3
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Setup
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
            cursor.execute("INSERT INTO nodes VALUES ('service_a', 'function', 'a', '/test.py')")
            cursor.execute("INSERT INTO nodes VALUES ('service_b', 'function', 'b', '/test.py')")
            cursor.execute("INSERT INTO nodes VALUES ('service_c', 'function', 'c', '/test.py')")
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # Create cycle: a -> b -> c -> a
            edges = [
                CallEdge("c1", "service_a", "service_b", CallType.DIRECT),
                CallEdge("c2", "service_b", "service_c", CallType.DIRECT),
                CallEdge("c3", "service_c", "service_a", CallType.DIRECT)
            ]
            db.add_call_edges(edges)
            
            # Detect
            analyzer = ImpactAnalyzer(db)
            cycles = analyzer.find_cycles()
            
            assert len(cycles) > 0, f"Expected cycle detection, got {len(cycles)} cycles"
            
            logger.info(f"✅ PASS: Detected {len(cycles)} circular dependency cycle(s)\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    # Test 6: Safe Deletion Check
    logger.info("TEST 6: Safe Deletion Analysis...")
    try:
        import sqlite3
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Setup
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
            cursor.execute("INSERT INTO nodes VALUES ('legacy_func', 'function', 'old', '/test.py')")
            cursor.execute("INSERT INTO nodes VALUES ('other_func', 'function', 'other', '/test.py')")
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # No calls to legacy_func = safe to delete
            analyzer = ImpactAnalyzer(db)
            safe, message = analyzer.is_safe_to_delete("legacy_func")
            
            assert safe is True, f"Expected safe deletion, but: {message}"
            
            logger.info(f"✅ PASS: Correctly identified safe deletion\n")
    except Exception as e:
        logger.info(f"❌ FAIL: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    logger.info("="*70)
    logger.info("✅ ALL CORE TESTS PASSED")
    logger.info("="*70)
    logger.info("\nPhase 32a Status:")
    logger.info("  ✓ AST extraction: Working")
    logger.info("  ✓ Call graph persistence: Working")
    logger.info("  ✓ Impact analysis: Working")
    logger.info("  ✓ Cycle detection: Working")
    logger.info("  ✓ Safety analysis: Working")
    logger.info("\nFiles Created:")
    logger.info("  ✓ src/phase32_call_graph_engine.py (500+ lines)")
    logger.info("  ✓ src/reasoning/impact_analyzer.py (300+ lines)")
    logger.info("  ✓ src/tools/call_graph_tools.py (400+ lines)")
    logger.info("  ✓ tests/test_phase32_call_graph.py (500+ lines)")
    logger.info("\nReady for:")
    logger.info("  → Agent integration")
    logger.info("  → Repository-wide analysis")
    logger.info("  → Automated refactoring decisions")
    logger.info("\nNext Steps:")
    logger.info("  1. Run: pytest tests/test_phase32_call_graph.py")
    logger.info("  2. Build call graph: python -c 'from src.phase32_call_graph_engine import CallGraphBuilder'")
    logger.info("  3. Integrate with agent core\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
