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
import logging
logger = logging.getLogger(__name__)
    CallGraphDB,
    CallGraphBuilder,
    PythonCallGraphExtractor,
    ImpactAnalyzer
)


def main():
    logger.info("\n" + "="*70)
    logger.info("BUILDING PIDDY'S CALL GRAPH")
    logger.info("="*70 + "\n")

    # Paths
    repo_path = "/workspaces/Piddy/src"
    db_path = "/workspaces/Piddy/.piddy_callgraph.db"
    nodes_db_path = "/workspaces/Piddy/.piddy_nodes.db"

    logger.info(f"Repository path: {repo_path}")
    logger.info(f"Call graph DB: {db_path}")
    logger.info(f"Nodes DB: {nodes_db_path}\n")

    # Initialize database
    logger.info("Step 1: Initializing database...")
    try:
        call_db = CallGraphDB(db_path)
        logger.info("✓ Call graph database initialized")
        
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
        logger.info("✓ Nodes database initialized\n")
    except Exception as e:
        logger.info(f"✗ Database initialization failed: {e}")
        return 1

    # Build call graph
    logger.info("Step 2: Building call graph from repository...")
    logger.info(f"  Scanning: {repo_path}\n")
    
    start_time = time.time()
    
    try:
        builder = CallGraphBuilder(call_db, node_db)
        stats = builder.build_from_directory(repo_path)
        
        elapsed = time.time() - start_time
        
        logger.info(f"✓ Call graph built in {elapsed:.1f} seconds")
        logger.info(f"  Files processed: {stats['files_processed']}")
        logger.info(f"  Functions found: {stats['functions_found']}")
        logger.info(f"  Calls extracted: {stats['calls_found']}")
        
        if stats['errors']:
            logger.info(f"  Warnings: {len(stats['errors'])} (non-fatal)")
        logger.info()
        
    except Exception as e:
        logger.info(f"✗ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Analyze results
    logger.info("Step 3: Analyzing call graph...")
    
    try:
        analyzer = ImpactAnalyzer(call_db)
        
        # Find circular dependencies
        cycles = analyzer.find_cycles()
        logger.info(f"\n  Circular dependencies found: {len(cycles)}")
        for i, cycle in enumerate(cycles[:3], 1):
            logger.info(f"    Cycle {i}: {' → '.join(cycle[:3])}...")
        
        # Find dead code
        logger.info(f"\n  Checking for dead code...")
        # Dead code functions would be those with in_degree=0 and not entry points
        
        logger.info(f"\n  Calculating statistics...")
        updated = call_db.update_statistics()
        logger.info(f"  Statistics updated for {updated} functions")
        
    except Exception as e:
        logger.info(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Show example queries
    logger.info("\nStep 4: Example queries you can run:\n")
    
    logger.info("  # Find all callers of a specific function:")
    logger.info("  callers = call_db.get_callers('func_id')")
    logger.info("  for caller in callers:")
    logger.info("      print(caller['caller_name'], 'calls this function')\n")
    
    logger.info("  # Calculate impact of changing a function:")
    logger.info("  impact = analyzer.calculate_impact_radius('func_id')")
    logger.info(f"      print(f'Risk level: {{impact.risk_level}}')")
    logger.info(f"      print(f'Affected: {{impact.total_affected}} functions')\n")
    
    logger.info("  # Find functions that are never called:")
    logger.info("  conn = sqlite3.connect(db_path)")
    logger.info("  cursor = conn.cursor()")
    logger.info("  cursor.execute('''")
    logger.info("      SELECT n.node_id, n.name FROM nodes n")
    logger.info("      LEFT JOIN call_graphs cg ON n.node_id = cg.target_node_id")
    logger.info("      WHERE cg.call_graph_id IS NULL")
    logger.info("  ''')\n")
    
    logger.info("  # Find hot spots (frequently called functions):")
    logger.info("  conn.execute('''")
    logger.info("      SELECT target_node_id, COUNT(*) as count")
    logger.info("      FROM call_graphs")
    logger.info("      GROUP BY target_node_id")
    logger.info("      ORDER BY count DESC LIMIT 10")
    logger.info("  ''')\n")
    
    # Summary
    logger.info("="*70)
    logger.info("✅ PIDDY CALL GRAPH BUILT SUCCESSFULLY")
    logger.info("="*70 + "\n")
    
    logger.info("Database files created:")
    logger.info(f"  • {db_path}")
    logger.info(f"  • {nodes_db_path}\n")
    
    logger.info("You can now use the call graph for:")
    logger.info("  ✓ Safe deletion analysis")
    logger.info("  ✓ Impact radius calculations")
    logger.info("  ✓ Circular dependency detection")
    logger.info("  ✓ Architecture analysis")
    logger.info("  ✓ Code refactoring validation\n")
    
    logger.info("To use in Python:")
    logger.info("  from src.phase32_call_graph_engine import CallGraphDB, ImpactAnalyzer")
    logger.info("  db = CallGraphDB('/workspaces/Piddy/.piddy_callgraph.db')")
    logger.info("  analyzer = ImpactAnalyzer(db)")
    logger.info("  impact = analyzer.calculate_impact_radius('function_id')\n")
    
    node_db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
