"""
Phase 32b: Test Coverage Mapping

Extracts test → function relationships to enable risk-aware impact analysis.
Enables agent to prioritize changes based on:
- Test coverage (high coverage = lower risk)
- Test quality (mock-based vs integration)
- Test age/recency (recently changed tests = reliable tests)

Integration: Maps test functions to stable_id functions for persistent tracking.
"""

import sqlite3
import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TestMapping:
    """Maps a test function to tested functions"""
    test_func_id: str
    test_name: str
    test_file: str
    tested_func_id: str
    tested_func_name: str
    tested_func_stable_id: str
    test_type: str  # 'unit', 'integration', 'e2e'
    confidence: float = 0.85  # How confident we are this test covers the function
    created_at: str = None


class TestCoverageExtractor:
    """Extract test → function mappings from test files"""

    def __init__(self, db_path: str, test_root: str = 'tests'):
        self.db_path = Path(db_path)
        self.test_root = Path(test_root)
        self.test_imports = {}  # Track what each test file imports
        self.test_functions = {}  # test_id -> FunctionDef

    def extract_test_coverage(self) -> Dict:
        """Extract all test → function mappings"""
        stats = {
            'test_files_found': 0,
            'test_functions_found': 0,
            'mappings_created': 0,
            'errors': []
        }

        # Find all test files
        for test_file in self.test_root.glob('**/test_*.py'):
            try:
                self._extract_file_tests(test_file, stats)
                stats['test_files_found'] += 1
            except Exception as e:
                logger.error(f"Error processing {test_file}: {e}")
                stats['errors'].append(str(e))

        return stats

    def _extract_file_tests(self, test_file: Path, stats: Dict):
        """Extract test functions from a single test file"""
        try:
            source = test_file.read_text()
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {test_file}: {e}")
            return

        test_funcs = []
        imports = self._extract_imports(tree)
        self.test_imports[str(test_file)] = imports

        # Find test functions (start with 'test_')
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_funcs.append(node)
                stats['test_functions_found'] += 1

        # Analyze each test function
        for test_func in test_funcs:
            mappings = self._analyze_test_function(
                test_func,
                test_file,
                imports
            )
            stats['mappings_created'] += len(mappings)

    def _extract_imports(self, tree: ast.AST) -> Dict[str, str]:
        """Extract imports from a test file"""
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = f"{module}.{alias.name}".lstrip('.')

        return imports

    def _analyze_test_function(self,
                               test_func: ast.FunctionDef,
                               test_file: Path,
                               imports: Dict[str, str]) -> List[TestMapping]:
        """Analyze a test function to find what it's testing"""
        mappings = []

        # Extract function calls from test body
        for node in ast.walk(test_func):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node.func)
                if func_name:
                    # Try to find which source function this calls
                    source_func_id = self._find_source_function(
                        func_name,
                        imports
                    )
                    
                    if source_func_id:
                        mapping = TestMapping(
                            test_func_id=self._make_id(test_func.name, str(test_file)),
                            test_name=test_func.name,
                            test_file=str(test_file),
                            tested_func_id=source_func_id,
                            tested_func_name=func_name,
                            tested_func_stable_id='',  # Will be populated from DB
                            test_type=self._classify_test(test_func, imports),
                            confidence=self._calculate_confidence(test_func),
                            created_at=datetime.now().isoformat()
                        )
                        mappings.append(mapping)

        return mappings

    def _get_call_name(self, func_node: ast.AST) -> Optional[str]:
        """Extract function name from a Call node"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            parts = []
            node = func_node
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                return '.'.join(reversed(parts))
        return None

    def _find_source_function(self, func_name: str, imports: Dict[str, str]) -> Optional[str]:
        """Find source function in database by name"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Try direct match first
        cursor.execute('''
            SELECT node_id FROM nodes 
            WHERE name = ? AND node_type = 'function'
            LIMIT 1
        ''', (func_name,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def _classify_test(self, test_func: ast.FunctionDef, imports: Dict[str, str]) -> str:
        """Classify test as unit/integration/e2e"""
        # Heuristic: look for common patterns
        source = ast.get_source_segment('', test_func) or ''

        if any(mock_pattern in source for mock_pattern in ['Mock', 'patch', 'mock']):
            return 'unit'
        elif any(fixture in source for fixture in ['client', 'session', 'db']):
            return 'integration'
        elif any(e2e in source for e2e in ['selenium', 'playwright', 'driver']):
            return 'e2e'
        else:
            return 'unit'

    def _calculate_confidence(self, test_func: ast.FunctionDef) -> float:
        """Calculate confidence in test coverage
        
        Heuristic:
        - Longer tests = more thorough = higher confidence (cap at 0.95)
        - Tests with assertions = higher confidence
        - Tests with multiple calls = lower confidence (scattered)
        """
        # Count LOC
        loc = len([n for n in ast.walk(test_func) if isinstance(n, ast.stmt)])

        # Count assertions
        assertions = len([n for n in ast.walk(test_func) if isinstance(n, ast.Assert)])

        # Count function calls (to find scattered coverage)
        calls = len([n for n in ast.walk(test_func) if isinstance(n, ast.Call)])

        confidence = 0.5
        confidence += min(0.2, loc / 50)  # Up to +0.2 for LOC
        confidence += min(0.2, assertions / 3)  # Up to +0.2 for assertions
        confidence -= min(0.1, max(0, (calls - 1) / 10))  # -0.1 if scattered

        return min(max(confidence, 0.0), 1.0)

    def _make_id(self, name: str, file_path: str) -> str:
        """Generate unique ID for test function"""
        import hashlib
        key = f"{file_path}:{name}"
        return hashlib.md5(key.encode()).hexdigest()[:16]

    def store_mappings(self, mappings: List[TestMapping]) -> int:
        """Store test → function mappings in database"""
        # Note: Requires test_coverage table to be created
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Create table if it doesn't exist
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_coverage (
                    coverage_id TEXT PRIMARY KEY,
                    test_func_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    test_file TEXT NOT NULL,
                    tested_func_id TEXT NOT NULL,
                    tested_func_name TEXT NOT NULL,
                    tested_func_stable_id TEXT,
                    test_type TEXT,
                    confidence REAL,
                    created_at TEXT,
                    FOREIGN KEY (tested_func_id) REFERENCES nodes(node_id),
                    FOREIGN KEY (tested_func_stable_id) REFERENCES nodes(stable_id)
                )
            ''')
        except sqlite3.OperationalError:
            pass  # Table already exists

        # Insert mappings
        added = 0
        for mapping in mappings:
            mapping_id = hashlib.md5(
                f"{mapping.test_func_id}:{mapping.tested_func_id}".encode()
            ).hexdigest()[:16]

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO test_coverage
                    (coverage_id, test_func_id, test_name, test_file,
                     tested_func_id, tested_func_name, tested_func_stable_id,
                     test_type, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mapping_id,
                    mapping.test_func_id,
                    mapping.test_name,
                    mapping.test_file,
                    mapping.tested_func_id,
                    mapping.tested_func_name,
                    mapping.tested_func_stable_id,
                    mapping.test_type,
                    mapping.confidence,
                    mapping.created_at
                ))
                added += 1
            except Exception as e:
                logger.error(f"Error storing mapping {mapping.test_name}: {e}")

        conn.commit()
        conn.close()
        return added


class RiskScorer:
    """Calculate risk scores based on test coverage"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)

    def calculate_function_risk(self, func_id: str) -> Dict:
        """Calculate risk score for a function (0.0 = low risk, 1.0 = high risk)"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get test coverage for function if table exists
        test_count = 0
        avg_conf = 0.0
        try:
            cursor.execute('''
                SELECT COUNT(*) as test_count, AVG(confidence) as avg_confidence
                FROM test_coverage
                WHERE tested_func_id = ?
            ''', (func_id,))
            coverage = dict(cursor.fetchone() or {'test_count': 0, 'avg_confidence': 0})
            test_count = coverage.get('test_count', 0) or 0
            avg_conf = coverage.get('avg_confidence', 0) or 0.0
        except sqlite3.OperationalError:
            # test_coverage table doesn't exist yet
            pass

        # Get function metadata
        cursor.execute('''
            SELECT complexity, lines_of_code FROM nodes WHERE node_id = ?
        ''', (func_id,))
        func_meta = cursor.fetchone()

        conn.close()

        if not func_meta:
            return {
                'func_id': func_id,
                'risk_score': 1.0,  # Unknown = high risk
                'reason': 'unknown_function'
            }

        # Calculate risk score
        complexity = func_meta['complexity'] or 0
        loc = func_meta['lines_of_code'] or 0

        # Base risk from lack of tests
        risk = 1.0 if test_count == 0 else 0.2

        # Reduce risk based on test coverage
        if test_count > 0:
            test_coverage_factor = min(0.8, test_count * 0.1)  # Up to 80% reduction
            risk -= test_coverage_factor * avg_conf

        # Increase risk based on complexity
        risk += min(0.3, complexity * 0.15)

        # Increase risk based on size
        risk += min(0.2, loc / 200)

        # Clamp to [0, 1]
        risk = max(0.0, min(1.0, risk))

        return {
            'func_id': func_id,
            'risk_score': risk,
            'test_count': test_count,
            'avg_test_confidence': avg_conf,
            'complexity': complexity,
            'lines_of_code': loc,
            'reason': self._get_risk_reason(risk, test_count, complexity)
        }

    def _get_risk_reason(self, risk: float, test_count: int, complexity: float) -> str:
        """Generate human-readable risk explanation"""
        if risk < 0.3:
            return 'well_tested_and_simple'
        elif risk < 0.6:
            if test_count == 0:
                return 'untested'
            else:
                return 'partially_tested'
        else:
            return 'high_complexity_low_coverage'

    def get_high_risk_functions(self, threshold: float = 0.7) -> List[Dict]:
        """Get all functions above risk threshold"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT node_id, name, complexity, lines_of_code FROM nodes
            WHERE node_type = 'function'
            ORDER BY complexity DESC, lines_of_code DESC
            LIMIT 100
        ''')

        functions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        high_risk = []
        for func in functions:
            risk_info = self.calculate_function_risk(func['node_id'])
            if risk_info['risk_score'] >= threshold:
                high_risk.append({
                    **func,
                    **risk_info
                })

        return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)


# Testing
if __name__ == '__main__':
    logger.info("Phase 32b: Test Coverage Mapping")
    logger.info("=" * 70)

    # Extract test coverage
    logger.info("\n1. Extracting test coverage...")
    extractor = TestCoverageExtractor('/workspaces/Piddy/.piddy_callgraph.db', 'tests')
    stats = extractor.extract_test_coverage()
    logger.info(f"   ✅ Test files found: {stats['test_files_found']}")
    logger.info(f"   ✅ Test functions found: {stats['test_functions_found']}")
    logger.info(f"   ✅ Mappings created: {stats['mappings_created']}")

    # Calculate risk scores
    logger.info("\n2. Calculating risk scores...")
    scorer = RiskScorer('/workspaces/Piddy/.piddy_callgraph.db')

    # Get sample functions
    import sqlite3
    conn = sqlite3.connect('/workspaces/Piddy/.piddy_callgraph.db')
    cursor = conn.cursor()
    cursor.execute('SELECT node_id, name FROM nodes LIMIT 5')
    functions = cursor.fetchall()
    conn.close()

    for func_id, func_name in functions:
        risk = scorer.calculate_function_risk(func_id)
        logger.info(f"   {func_name}: risk={risk['risk_score']:.2f} ({risk['reason']})")

    # High risk functions
    logger.info("\n3. High-risk functions (>0.7 risk):")
    high_risk = scorer.get_high_risk_functions(threshold=0.7)
    for func in high_risk[:5]:
        logger.info(f"   {func['name']}: {func['risk_score']:.2f} - {func['reason']}")

    logger.info("\n✅ Phase 32b test coverage mapping complete")
