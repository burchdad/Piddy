#!/usr/bin/env python3
"""
Phase 32a: Verification Script

Quick verification that Phase 32a is working correctly.
Run this after pulling the code to ensure everything is set up.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Piddy/src')

def verify_imports():
    """Verify all Phase 32 modules can be imported"""
    print("✓ Verifying imports...")
    try:
        from phase32_call_graph_engine import (
            PythonCallGraphExtractor,
            CallGraphDB,
            ImpactAnalyzer,
            CallGraphBuilder,
            FunctionSignature,
            CallEdge,
            CallType
        )
        print("  ✓ phase32_call_graph_engine imported successfully")
        
        from reasoning.impact_analyzer import (
            ImpactAnalysisTool,
            RefactoringValidator
        )
        print("  ✓ reasoning.impact_analyzer imported successfully")
        
        from tools.call_graph_tools import (
            get_function_impact,
            check_breaking_change,
            find_safe_extraction_points,
            detect_circular_dependencies,
            estimate_refactoring_risk
        )
        print("  ✓ tools.call_graph_tools imported successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_extraction():
    """Verify AST extraction works"""
    print("\n✓ Verifying Python AST extraction...")
    try:
        from phase32_call_graph_engine import PythonCallGraphExtractor
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.py"
            test_file.write_text('''
def function_a():
    return function_b()

def function_b():
    return 42
''')
            
            extractor = PythonCallGraphExtractor(str(test_file))
            functions, calls = extractor.extract()
            
            assert len(functions) == 2, f"Expected 2 functions, got {len(functions)}"
            assert len(calls) >= 1, f"Expected at least 1 call, got {len(calls)}"
            
            print(f"  ✓ Extracted {len(functions)} functions")
            print(f"  ✓ Extracted {len(calls)} calls")
            return True
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")
        return False


def verify_database():
    """Verify database persistence works"""
    print("\n✓ Verifying database persistence...")
    try:
        from phase32_call_graph_engine import CallGraphDB, CallEdge, CallType
        import sqlite3
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Create database
            db = CallGraphDB(db_path)
            print("  ✓ Database created")
            
            # Create nodes table (Phase 28 integration)
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
            cursor.execute("INSERT INTO nodes VALUES ('func_1', 'function', 'test', '/test.py')")
            cursor.execute("INSERT INTO nodes VALUES ('func_2', 'function', 'test2', '/test.py')")
            conn.commit()
            conn.close()
            
            # Add call edge
            edge = CallEdge(
                call_id="call_1",
                source_func_id="func_1",
                target_func_id="func_2",
                call_type=CallType.DIRECT
            )
            count = db.add_call_edges([edge])
            assert count == 1, f"Expected 1 edge added, got {count}"
            print("  ✓ Call edge added to database")
            
            # Query
            callers = db.get_callers("func_2")
            assert len(callers) >= 1, f"Expected at least 1 caller, got {len(callers)}"
            print(f"  ✓ Query returned {len(callers)} caller(s)")
            
            return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_impact_analysis():
    """Verify impact analysis works"""
    print("\n✓ Verifying impact analysis...")
    try:
        from phase32_call_graph_engine import CallGraphDB, ImpactAnalyzer, CallEdge, CallType
        import sqlite3
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = str(Path(tmp_dir) / "test.db")
            
            # Setup database
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
            for i in range(5):
                cursor.execute(
                    "INSERT INTO nodes VALUES (?, 'function', 'func', '/test.py')",
                    (f"func_{i}",)
                )
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # Create call chain: func_1,2,3,4 all call func_0
            edges = [
                CallEdge(
                    call_id=f"call_{i}",
                    source_func_id=f"func_{i}",
                    target_func_id="func_0",
                    call_type=CallType.DIRECT
                )
                for i in range(1, 5)
            ]
            db.add_call_edges(edges)
            
            # Analyze impact
            analyzer = ImpactAnalyzer(db)
            impact = analyzer.calculate_impact_radius("func_0")
            
            assert impact.direct_callers == 4, f"Expected 4 callers, got {impact.direct_callers}"
            assert impact.risk_level in ["low", "medium", "high"], f"Invalid risk level: {impact.risk_level}"
            
            print(f"  ✓ Impact analysis: {impact.direct_callers} direct callers")
            print(f"  ✓ Risk level: {impact.risk_level}")
            
            return True
    except Exception as e:
        print(f"  ✗ Impact analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_circular_detection():
    """Verify circular dependency detection"""
    print("\n✓ Verifying circular dependency detection...")
    try:
        from phase32_call_graph_engine import CallGraphDB, ImpactAnalyzer, CallEdge, CallType
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
            cursor.execute("INSERT INTO nodes VALUES ('func_a', 'function', 'a', '/test.py')")
            cursor.execute("INSERT INTO nodes VALUES ('func_b', 'function', 'b', '/test.py')")
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # Create cycle: a -> b -> a
            edges = [
                CallEdge("call_1", "func_a", "func_b", CallType.DIRECT),
                CallEdge("call_2", "func_b", "func_a", CallType.DIRECT)
            ]
            db.add_call_edges(edges)
            
            # Detect
            analyzer = ImpactAnalyzer(db)
            cycles = analyzer.find_cycles()
            
            assert len(cycles) > 0, f"Expected cycles detected, but got {len(cycles)}"
            print(f"  ✓ Circular dependency detected: {len(cycles)} cycle(s)")
            
            return True
    except Exception as e:
        print(f"  ✗ Circular detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tools():
    """Verify agent tools work"""
    print("\n✓ Verifying agent tools...")
    try:
        from tools.call_graph_tools import (
            get_function_impact,
            estimate_refactoring_risk
        )
        from phase32_call_graph_engine import CallGraphDB, CallEdge, CallType
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
            cursor.execute("INSERT INTO nodes VALUES ('func_test', 'function', 'test', '/test.py')")
            conn.commit()
            conn.close()
            
            db = CallGraphDB(db_path)
            
            # Test tool
            impact = get_function_impact("func_test", db_path)
            assert 'risk_level' in impact, f"Expected risk_level in result"
            print(f"  ✓ get_function_impact() works: risk_level={impact['risk_level']}")
            
            # Test risk estimation
            risk = estimate_refactoring_risk(
                [{"type": "parameter_add", "function": "func_test"}],
                db_path
            )
            assert 'risk_score' in risk, f"Expected risk_score in result"
            print(f"  ✓ estimate_refactoring_risk() works: risk_score={risk['risk_score']}")
            
            return True
    except Exception as e:
        print(f"  ✗ Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("PHASE 32a: VERIFICATION SCRIPT")
    print("="*70 + "\n")
    
    tests = [
        verify_imports,
        verify_extraction,
        verify_database,
        verify_impact_analysis,
        verify_circular_detection,
        verify_tools
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\nPhase 32a is ready for:")
        print("  • Agent integration")
        print("  • Repository-wide call graph building")
        print("  • Automated refactoring decisions")
        print("\nNext: Run pytest for comprehensive test coverage")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print("\nFailing tests need investigation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
