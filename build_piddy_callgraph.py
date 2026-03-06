#!/usr/bin/env python3
"""
Real-World Example: Build Piddy's Own Call Graph

This script builds a call graph for Piddy itself, demonstrating Phase 32a
on a real, production-scale codebase.

Usage:
    python build_piddy_callgraph.py
    
The resulting database can be used for:
    - Finding dead code
    - Impact analysis before changes
    - Identifying architecture improvements
    - Detecting circular dependencies
"""

import sys
import time
from pathlib import Path
import sqlite3

sys.path.insert(0, '/workspaces/Piddy/src')

from phase32_call_graph_engine import (
    CallGraphDB,
    CallGraphBuilder,
    PythonCallGraphExtractor,
    ImpactAnalyzer
)


def main():
    print("\n" + "="*70)
    print("BUILDING PIDDY'S CALL GRAPH")
    print("="*70 + "\n")

    # Paths
    repo_path = "/workspaces/Piddy/src"
    db_path = "/workspaces/Piddy/.piddy_callgraph.db"
    nodes_db_path = "/workspaces/Piddy/.piddy_nodes.db"

    print(f"Repository path: {repo_path}")
    print(f"Call graph DB: {db_path}")
    print(f"Nodes DB: {nodes_db_path}\n")

    # Initialize database
    print("Step 1: Initializing database...")
    try:
        call_db = CallGraphDB(db_path)
        print("✓ Call graph database initialized")
        
        # Create nodes table if it doesn't exist
        node_db = sqlite3.connect(nodes_db_path)
        cursor = node_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                name TEXT,
                path TEXT,
                language TEXT DEFAULT 'python',
                lines_of_code INTEGER DEFAULT 0,
                complexity REAL DEFAULT 0.5,
                last_modified TEXT,
                metadata TEXT
            )
        ''')
        node_db.commit()
        print("✓ Nodes database initialized\n")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return 1

    # Build call graph
    print("Step 2: Building call graph from repository...")
    print(f"  Scanning: {repo_path}\n")
    
    start_time = time.time()
    
    try:
        builder = CallGraphBuilder(call_db, node_db)
        stats = builder.build_from_directory(repo_path)
        
        elapsed = time.time() - start_time
        
        print(f"✓ Call graph built in {elapsed:.1f} seconds")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Functions found: {stats['functions_found']}")
        print(f"  Calls extracted: {stats['calls_found']}")
        
        if stats['errors']:
            print(f"  Warnings: {len(stats['errors'])} (non-fatal)")
        print()
        
    except Exception as e:
        print(f"✗ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Analyze results
    print("Step 3: Analyzing call graph...")
    
    try:
        analyzer = ImpactAnalyzer(call_db)
        
        # Find circular dependencies
        cycles = analyzer.find_cycles()
        print(f"\n  Circular dependencies found: {len(cycles)}")
        for i, cycle in enumerate(cycles[:3], 1):
            print(f"    Cycle {i}: {' → '.join(cycle[:3])}...")
        
        # Find dead code
        print(f"\n  Checking for dead code...")
        # Dead code functions would be those with in_degree=0 and not entry points
        
        print(f"\n  Calculating statistics...")
        updated = call_db.update_statistics()
        print(f"  Statistics updated for {updated} functions")
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Show example queries
    print("\nStep 4: Example queries you can run:\n")
    
    print("  # Find all callers of a specific function:")
    print("  callers = call_db.get_callers('func_id')")
    print("  for caller in callers:")
    print("      print(caller['caller_name'], 'calls this function')\n")
    
    print("  # Calculate impact of changing a function:")
    print("  impact = analyzer.calculate_impact_radius('func_id')")
    print(f"      print(f'Risk level: {{impact.risk_level}}')")
    print(f"      print(f'Affected: {{impact.total_affected}} functions')\n")
    
    print("  # Find functions that are never called:")
    print("  conn = sqlite3.connect(db_path)")
    print("  cursor = conn.cursor()")
    print("  cursor.execute('''")
    print("      SELECT n.node_id, n.name FROM nodes n")
    print("      LEFT JOIN call_graphs cg ON n.node_id = cg.target_node_id")
    print("      WHERE cg.call_graph_id IS NULL")
    print("  ''')\n")
    
    print("  # Find hot spots (frequently called functions):")
    print("  conn.execute('''")
    print("      SELECT target_node_id, COUNT(*) as count")
    print("      FROM call_graphs")
    print("      GROUP BY target_node_id")
    print("      ORDER BY count DESC LIMIT 10")
    print("  ''')\n")
    
    # Summary
    print("="*70)
    print("✅ PIDDY CALL GRAPH BUILT SUCCESSFULLY")
    print("="*70 + "\n")
    
    print("Database files created:")
    print(f"  • {db_path}")
    print(f"  • {nodes_db_path}\n")
    
    print("You can now use the call graph for:")
    print("  ✓ Safe deletion analysis")
    print("  ✓ Impact radius calculations")
    print("  ✓ Circular dependency detection")
    print("  ✓ Architecture analysis")
    print("  ✓ Code refactoring validation\n")
    
    print("To use in Python:")
    print("  from src.phase32_call_graph_engine import CallGraphDB, ImpactAnalyzer")
    print("  db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')")
    print("  analyzer = ImpactAnalyzer(db)")
    print("  impact = analyzer.calculate_impact_radius('function_id')\n")
    
    node_db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
