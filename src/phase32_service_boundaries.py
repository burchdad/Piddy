"""
Phase 32e: Service Boundary Analysis

Maps service boundaries and identifies cross-service dependencies.
Enables service-aware impact analysis and safe service refactoring.
"""

import sqlite3
from typing import Dict, List, Set
from collections import defaultdict

class ServiceBoundaryDetector:
    """Detect and analyze service boundaries"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.services = None

    def identify_services(self) -> Dict[str, List[str]]:
        """Identify services by analyzing module structure"""
        if self.services:
            return self.services

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        services = defaultdict(list)

        try:
            # Group by top-level module
            cursor.execute('''
                SELECT DISTINCT 
                    CASE 
                        WHEN path LIKE 'src/%' THEN substr(path, 5, instr(substr(path, 5), '/') - 1)
                        ELSE substr(path, 1, instr(path, '/') - 1)
                    END as service,
                    node_id
                FROM nodes
                WHERE node_type = 'function'
            ''')

            for service, node_id in cursor.fetchall():
                if service:
                    services[service].append(node_id)

        except Exception as e:
            print(f"Error identifying services: {e}")

        conn.close()
        self.services = dict(services)
        return self.services

    def get_service_for_function(self, func_id: str) -> str:
        """Get service name for a function"""
        services = self.identify_services()
        
        for service, func_ids in services.items():
            if func_id in func_ids:
                return service
        
        return 'unknown'

    def find_cross_service_calls(self) -> List[Dict]:
        """Find all calls between services"""
        services = self.identify_services()
        service_map = {}

        # Map function IDs to service
        for service, func_ids in services.items():
            for func_id in func_ids:
                service_map[func_id] = service

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cross_service = []

        try:
            cursor.execute('''
                SELECT cg.*, n1.name as source_name, n2.name as target_name
                FROM call_graphs cg
                JOIN nodes n1 ON cg.source_node_id = n1.node_id
                JOIN nodes n2 ON cg.target_node_id = n2.node_id
            ''')

            for row in cursor.fetchall():
                source_service = service_map.get(row['source_node_id'], 'unknown')
                target_service = service_map.get(row['target_node_id'], 'unknown')

                if source_service != target_service:
                    cross_service.append({
                        'source_service': source_service,
                        'target_service': target_service,
                        'source_func': row['source_name'],
                        'target_func': row['target_name'],
                        'call_type': row['call_type'],
                        'confidence': row.get('confidence', 0.95)
                    })

        except Exception as e:
            print(f"Error finding cross-service calls: {e}")

        conn.close()
        return cross_service

    def analyze_service_dependencies(self) -> Dict:
        """Analyze dependency graph between services"""
        services = self.identify_services()
        cross_service_calls = self.find_cross_service_calls()

        # Build dependency graph
        deps = defaultdict(set)
        call_counts = defaultdict(int)

        for call in cross_service_calls:
            source = call['source_service']
            target = call['target_service']
            deps[source].add(target)
            call_counts[(source, target)] += 1

        # Calculate metrics
        analysis = {
            'total_services': len(services),
            'services': list(services.keys()),
            'total_cross_service_calls': len(cross_service_calls),
            'service_dependencies': dict(deps),
            'call_counts': {k: v for k, v in call_counts.items()},
            'dependency_depth': self._calculate_dependency_depth(deps)
        }

        return analysis

    def _calculate_dependency_depth(self, deps: Dict[str, Set[str]]) -> int:
        """Calculate maximum dependency depth (longest chain)"""
        if not deps:
            return 0

        visited = set()
        max_depth = 0

        def dfs(service, depth):
            nonlocal max_depth
            if service in visited:
                return
            visited.add(service)
            max_depth = max(max_depth, depth)

            for dependent in deps.get(service, set()):
                dfs(dependent, depth + 1)

        for service in deps:
            visited = set()
            dfs(service, 0)

        return max_depth

    def identify_boundary_violations(self) -> List[Dict]:
        """Identify functions that violate service boundaries"""
        services = self.identify_services()
        violations = []

        # Define expected boundaries
        # (Example: auth service shouldn't call database directly)
        problematic_patterns = [
            ('auth', 'ml'),  # Auth shouldn't call ML
            ('cache', 'ai'),  # Cache shouldn't call AI
        ]

        cross_service = self.find_cross_service_calls()

        for call in cross_service:
            source = call['source_service']
            target = call['target_service']

            if (source, target) in problematic_patterns:
                violations.append({
                    'from_service': source,
                    'to_service': target,
                    'severity': 'high',
                    'reason': f'{source} should not depend on {target}'
                })

        return violations

    def get_service_health(self) -> Dict:
        """Calculate health metrics for each service"""
        services = self.identify_services()
        deps = self.analyze_service_dependencies()

        health = {}

        for service in services:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                # Count functions in service
                cursor.execute('''
                    SELECT COUNT(*) FROM nodes
                    WHERE node_type = 'function' AND node_id IN ({})
                '''.format(','.join(['?'] * len(services[service]))),
                service_ids := services[service])

                func_count = cursor.fetchone()[0]

                # Count outgoing dependencies
                outgoing = len(deps['service_dependencies'].get(service, []))

                # Count incoming dependencies  
                incoming = sum(
                    1 for deps_list in deps['service_dependencies'].values()
                    if service in deps_list
                )

                health[service] = {
                    'function_count': len(services[service]),
                    'outgoing_dependencies': outgoing,
                    'incoming_dependencies': incoming,
                    'coupling': (outgoing + incoming) / max(len(services), 1),
                    'status': 'healthy' if outgoing <= 3 else 'tightly_coupled'
                }

            except Exception as e:
                health[service] = {'error': str(e)}

            conn.close()

        return health


class ServiceRefactoringPlanner:
    """Plan safe service refactoring"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.detector = ServiceBoundaryDetector(db_path)

    def plan_service_extraction(self, source_service: str,
                               functions_to_extract: List[str]) -> Dict:
        """Plan extraction of functions into new service"""
        
        # Calculate impact
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Find callers of functions being extracted
            placeholders = ','.join(['?'] * len(functions_to_extract))
            cursor.execute(f'''
                SELECT DISTINCT source_node_id FROM call_graphs
                WHERE target_node_id IN ({placeholders})
            ''', functions_to_extract)

            affected_callers = set(row[0] for row in cursor.fetchall())

        except:
            affected_callers = set()

        conn.close()

        plan = {
            'source_service': source_service,
            'functions_to_extract': len(functions_to_extract),
            'affected_callers': len(affected_callers),
            'risk_level': 'high' if len(affected_callers) > 10 else 'medium',
            'steps': [
                '1. Create new service module',
                '2. Move selected functions',
                '3. Update imports in calling code',
                '4. Add service boundary interface',
                '5. Update tests'
            ]
        }

        return plan


if __name__ == '__main__':
    print("Phase 32e: Service Boundary Analysis")
    print("=" * 70)

    detector = ServiceBoundaryDetector('.piddy_callgraph.db')

    # Identify services
    print("\n1. Identifying services...")
    services = detector.identify_services()
    print(f"   ✅ Services found: {len(services)}")
    for service in list(services.keys())[:5]:
        print(f"      - {service}: {len(services[service])} functions")

    # Find cross-service calls
    print("\n2. Finding cross-service dependencies...")
    cross_service = detector.find_cross_service_calls()
    print(f"   ✅ Cross-service calls: {len(cross_service)}")

    # Analyze dependencies
    print("\n3. Analyzing service dependencies...")
    analysis = detector.analyze_service_dependencies()
    print(f"   ✅ Total services: {analysis['total_services']}")
    print(f"   ✅ Cross-service calls: {analysis['total_cross_service_calls']}")
    print(f"   ✅ Max dependency depth: {analysis['dependency_depth']}")

    # Service health
    print("\n4. Service health metrics...")
    health = detector.get_service_health()
    healthy = sum(1 for s in health.values() if s.get('status') == 'healthy')
    print(f"   ✅ Healthy services: {healthy}/{len(health)}")

    print("\n✅ Phase 32e service analysis complete")
