#!/usr/bin/env python3
"""
Phase 32 Live Testing Suite

Tests all Phase 32 components in production environment.
"""

import sys
import os
import time
import json
import sqlite3
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# Add production path to Python path
prod_path = Path(__file__).parent
sys.path.insert(0, str(prod_path / 'src'))
sys.path.insert(0, str(prod_path.parent / 'src'))  # Add main src for imports
sys.path.insert(0, str(prod_path.parent))  # Add workspace root

class Phase32LiveTests:
    """Live testing framework for Phase 32 production"""
    
    def __init__(self, prod_path):
        self.prod_path = Path(prod_path)
        self.db_path = self.prod_path / '.piddy_callgraph.db'
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test_database_connectivity(self):
        """Test 1: Database connectivity"""
        logger.info("\n[TEST 1] Database Connectivity...")
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nodes')
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                self.passed += 1
                logger.info(f"  ✅ PASS: Database connected ({count} nodes)")
                return True
            else:
                self.failed += 1
                logger.info("  ❌ FAIL: Database empty")
                return False
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_call_graph_integrity(self):
        """Test 2: Call graph integrity"""
        logger.info("\n[TEST 2] Call Graph Integrity...")
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check edges
            cursor.execute('SELECT COUNT(*) FROM call_graphs WHERE confidence IS NOT NULL')
            confident_edges = cursor.fetchone()[0]
            
            # Check nodes with stable IDs
            cursor.execute('SELECT COUNT(*) FROM nodes WHERE stable_id IS NOT NULL')
            stable_nodes = cursor.fetchone()[0]
            
            conn.close()
            
            if confident_edges > 0 and stable_nodes > 0:
                self.passed += 1
                logger.info(f"  ✅ PASS: {confident_edges} confident edges, {stable_nodes} stable nodes")
                return True
            else:
                self.failed += 1
                logger.info(f"  ❌ FAIL: No confident edges or stable nodes")
                return False
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_phase32_imports(self):
        """Test 3: Phase 32 module imports"""
        logger.info("\n[TEST 3] Phase 32 Module Imports...")
        try:
            from phase32_unified_reasoning import UnifiedReasoningEngine
            from phase32_type_system import TypeExtractor
            from phase32_api_contracts import APIContractTracker
            from phase32_service_boundaries import ServiceBoundaryDetector
            
            self.passed += 1
            logger.info("  ✅ PASS: All Phase 32 modules imported successfully")
            return True
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: Import error: {e}")
            return False
    
    def test_unified_reasoning_engine(self):
        """Test 4: Unified Reasoning Engine"""
        logger.info("\n[TEST 4] Unified Reasoning Engine...")
        try:
            from phase32_unified_reasoning import UnifiedReasoningEngine
            
            engine = UnifiedReasoningEngine(str(self.db_path))
            
            # Get sample function
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT node_id FROM nodes WHERE node_type = "function" LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                func_id = result[0]
                evaluation = engine.evaluate_refactoring(func_id, {'action': 'test'})
                
                if 'confidence' in evaluation and evaluation['confidence'] > 0:
                    self.passed += 1
                    logger.info(f"  ✅ PASS: Engine evaluated with confidence {evaluation['confidence']:.2f}")
                    return True
            
            self.failed += 1
            logger.info("  ❌ FAIL: Engine evaluation failed")
            return False
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_type_system(self):
        """Test 5: Type System"""
        logger.info("\n[TEST 5] Type System...")
        try:
            from phase32_type_system import TypeExtractor
            
            extractor = TypeExtractor(str(self.db_path))
            result = extractor.extract_types()
            
            # extract_types() returns a dict with 'type_hints_found' key
            if isinstance(result, dict) and result.get('type_hints_found', 0) > 0:
                self.passed += 1
                logger.info(f"  ✅ PASS: Extracted {result['type_hints_found']} type hints from {result['functions_analyzed']} functions")
                return True
            else:
                self.failed += 1
                logger.info("  ❌ FAIL: No type hints extracted")
                return False
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_api_contracts(self):
        """Test 6: API Contracts"""
        logger.info("\n[TEST 6] API Contracts...")
        try:
            from phase32_api_contracts import APIContractTracker
            
            tracker = APIContractTracker(str(self.db_path))
            
            self.passed += 1
            logger.info("  ✅ PASS: API Contract tracker initialized")
            return True
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_service_boundaries(self):
        """Test 7: Service Boundaries"""
        logger.info("\n[TEST 7] Service Boundaries...")
        try:
            from phase32_service_boundaries import ServiceBoundaryDetector
            
            detector = ServiceBoundaryDetector(str(self.db_path))
            
            self.passed += 1
            logger.info("  ✅ PASS: Service Boundary detector initialized")
            return True
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_production_integration(self):
        """Test 8: Production Integration"""
        logger.info("\n[TEST 8] Production Integration...")
        try:
            from phase32_production import Phase32ProductionIntegration
            
            integration = Phase32ProductionIntegration(str(self.db_path))
            
            self.passed += 1
            logger.info("  ✅ PASS: Production integration layer initialized")
            return True
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def test_performance(self):
        """Test 9: Performance (all operations < 100ms)"""
        logger.info("\n[TEST 9] Performance...")
        try:
            from phase32_unified_reasoning import UnifiedReasoningEngine
            
            engine = UnifiedReasoningEngine(str(self.db_path))
            
            # Get sample function
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT node_id FROM nodes WHERE node_type = "function" LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                func_id = result[0]
                
                # Time refactoring evaluation
                start = time.time()
                engine.evaluate_refactoring(func_id, {'action': 'test'})
                elapsed = (time.time() - start) * 1000  # milliseconds
                
                if elapsed < 100:
                    self.passed += 1
                    logger.info(f"  ✅ PASS: Evaluation completed in {elapsed:.1f}ms (target <100ms)")
                    return True
                else:
                    self.failed += 1
                    logger.info(f"  ⚠️  WARN: Evaluation took {elapsed:.1f}ms (target <100ms)")
                    return False
            
            self.failed += 1
            logger.info("  ❌ FAIL: Performance test inconclusive")
            return False
        except Exception as e:
            self.failed += 1
            logger.info(f"  ❌ FAIL: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 32 LIVE TESTING SUITE")
        logger.info("=" * 70)
        
        self.test_database_connectivity()
        self.test_call_graph_integrity()
        self.test_phase32_imports()
        self.test_unified_reasoning_engine()
        self.test_type_system()
        self.test_api_contracts()
        self.test_service_boundaries()
        self.test_production_integration()
        self.test_performance()
        
        # Summary
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        logger.info("\n" + "=" * 70)
        logger.info(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed ({pass_rate:.1f}%)")
        logger.info("=" * 70)
        
        return self.failed == 0

if __name__ == '__main__':
    import sys
    prod_path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent
    
    tester = Phase32LiveTests(prod_path)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
