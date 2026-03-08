"""
logger = logging.getLogger(__name__)
Phase 41: Multi-Repository Coordination
Coordinates missions across multiple repositories and manages dependencies

Integrates with:
- Phase 39: Impact graphs across repos
- Phase 40: Coordinated simulation
- Infrastructure: Graph store for multi-repo graphs
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import asyncio

from src.infrastructure.graph_store import DependencyGraphStore, GraphNode, GraphEdge
import logging


@dataclass
class RepositoryInfo:
    """Information about a repository"""
    repo_id: str
    repo_name: str
    repo_path: str
    graph_id: str                   # Associated graph in graph store
    dependencies: List[str] = field(default_factory=list)  # List of repo IDs this depends on
    dependents: List[str] = field(default_factory=list)    # List of repo IDs that depend on this


@dataclass
class CrossRepoDependency:
    """Represents dependency between repositories"""
    source_repo: str
    target_repo: str
    dependency_type: str             # "imports", "uses_api", "extends", etc.
    affected_modules: List[str] = field(default_factory=list)


@dataclass
class CoordinatedMission:
    """Mission coordinated across multiple repos"""
    mission_id: str
    mission_name: str
    primary_repo: str                # Repo where changes start
    coordinated_repos: List[str]     # Other repos that need coordination
    execution_order: List[str]       # Order to execute changes
    cross_repo_prs: List[Dict] = field(default_factory=list)  # PRs to create/manage


class MultiRepoCoordinator:
    """Coordinates missions across multiple repositories"""
    
    def __init__(self, graph_store: DependencyGraphStore):
        """Initialize multi-repo coordinator"""
        self.graph_store = graph_store
        self.repositories: Dict[str, RepositoryInfo] = {}
        self.cross_repo_dependencies: List[CrossRepoDependency] = []
    
    def register_repository(self, repo_info: RepositoryInfo) -> None:
        """Register a repository"""
        self.repositories[repo_info.repo_id] = repo_info
    
    def add_cross_repo_dependency(self, dependency: CrossRepoDependency) -> None:
        """Add cross-repo dependency"""
        self.cross_repo_dependencies.append(dependency)
        
        # Update repository info
        if dependency.source_repo in self.repositories:
            self.repositories[dependency.source_repo].dependents.append(dependency.target_repo)
        
        if dependency.target_repo in self.repositories:
            self.repositories[dependency.target_repo].dependencies.append(dependency.source_repo)
    
    def get_affected_repos(self, primary_repo: str, 
                          changed_modules: List[str]) -> List[str]:
        """
        Determine which repos are affected by changes in primary_repo
        
        Args:
            primary_repo: Repo where changes occur
            changed_modules: Modules changed in that repo
        
        Returns:
            List of affected repo IDs
        """
        
        affected = set()
        
        # Find direct dependencies
        for dep in self.cross_repo_dependencies:
            if dep.source_repo == primary_repo:
                # This repo's changes affect downstream repos
                if self._has_relevant_modules(dep, changed_modules):
                    affected.add(dep.target_repo)
        
        # Find transitive dependencies (cascade)
        to_check = list(affected)
        while to_check:
            current = to_check.pop(0)
            
            for dep in self.cross_repo_dependencies:
                if dep.source_repo == current and dep.target_repo not in affected:
                    affected.add(dep.target_repo)
                    to_check.append(dep.target_repo)
        
        return list(affected)
    
    def plan_coordinated_execution(self, primary_repo: str,
                                  mission_name: str,
                                  changed_modules: List[str]) -> CoordinatedMission:
        """
        Plan coordinated execution across repos
        
        Args:
            primary_repo: Repo where mission starts
            mission_name: Name of the mission
            changed_modules: Modules affected in primary repo
        
        Returns:
            CoordinatedMission with execution plan
        """
        
        # Get affected repos
        affected_repos = self.get_affected_repos(primary_repo, changed_modules)
        
        # Determine execution order (topological sort)
        execution_order = self._topological_sort(primary_repo, affected_repos)
        
        # Create coordinated mission
        mission = CoordinatedMission(
            mission_id=f"coord_{primary_repo}_{mission_name}_{id(mission)}",
            mission_name=f"coordinated_{mission_name}",
            primary_repo=primary_repo,
            coordinated_repos=affected_repos,
            execution_order=execution_order,
        )
        
        return mission
    
    def create_pr_chain(self, mission: CoordinatedMission) -> List[Dict]:
        """
        Create a chain of coordinated PRs across repos
        
        Args:
            mission: Coordinated mission
        
        Returns:
            List of PR configurations
        """
        
        prs = []
        base_branch = "main"
        
        for i, repo_id in enumerate(mission.execution_order):
            repo = self.repositories.get(repo_id)
            if not repo:
                continue
            
            pr_config = {
                'repo_id': repo_id,
                'repo_name': repo.repo_name,
                'branch_name': f"coordinated/{mission.mission_name}/{i}",
                'base_branch': base_branch,
                'title': f"{mission.mission_name} - Part {i+1}/{len(mission.execution_order)}",
                'description': self._generate_pr_description(mission, repo_id),
                'chain_index': i,
                'total_in_chain': len(mission.execution_order),
                'depends_on_pr': prs[i-1]['branch_name'] if i > 0 else None,
            }
            
            prs.append(pr_config)
            mission.cross_repo_prs.append(pr_config)
        
        return prs
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies between repos"""
        
        # Build adjacency list
        graph: Dict[str, List[str]] = {}
        for repo_id in self.repositories:
            graph[repo_id] = []
        
        for dep in self.cross_repo_dependencies:
            if dep.source_repo in graph:
                graph[dep.source_repo].append(dep.target_repo)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for repo_id in graph:
            if repo_id not in visited:
                dfs(repo_id, [])
        
        return cycles
    
    def validate_coordinated_plan(self, mission: CoordinatedMission) -> Tuple[bool, List[str]]:
        """Validate a coordinated mission plan"""
        
        errors = []
        
        # Check all repos exist
        for repo_id in [mission.primary_repo] + mission.coordinated_repos:
            if repo_id not in self.repositories:
                errors.append(f"Repository not found: {repo_id}")
        
        # Check execution order includes all repos
        if set(mission.execution_order) != set([mission.primary_repo] + mission.coordinated_repos):
            errors.append("Execution order mismatch with coordinated repos")
        
        # Check for circular dependencies
        cycles = self.detect_circular_dependencies()
        if cycles:
            errors.append(f"Circular dependencies detected: {cycles}")
        
        return len(errors) == 0, errors
    
    # Private helper methods
    
    def _has_relevant_modules(self, dep: CrossRepoDependency,
                             changed_modules: List[str]) -> bool:
        """Check if dependency is affected by changed modules"""
        
        if not dep.affected_modules:
            # If no specific modules listed, assume all changes affect it
            return True
        
        # Check for overlap between changed modules and affected modules
        for changed in changed_modules:
            for affected in dep.affected_modules:
                if changed in affected or affected in changed:
                    return True
        
        return False
    
    def _topological_sort(self, start_repo: str, repos: List[str]) -> List[str]:
        """Topological sort of repos for execution order"""
        
        # Build graph for these repos
        graph: Dict[str, List[str]] = {repo: [] for repo in [start_repo] + repos}
        
        for dep in self.cross_repo_dependencies:
            if dep.source_repo in graph and dep.target_repo in graph:
                graph[dep.source_repo].append(dep.target_repo)
        
        # Topological sort using Kahn's algorithm
        in_degree = {repo: 0 for repo in graph}
        for repo in graph:
            for neighbor in graph[repo]:
                in_degree[neighbor] += 1
        
        queue = [repo for repo in graph if in_degree[repo] == 0]
        result = []
        
        while queue:
            repo = queue.pop(0)
            result.append(repo)
            
            for neighbor in graph[repo]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If topological sort failed (cycle detected), return original order
        if len(result) != len(graph):
            return [start_repo] + repos
        
        return result
    
    def _generate_pr_description(self, mission: CoordinatedMission, repo_id: str) -> str:
        """Generate PR description"""
        
        idx = mission.execution_order.index(repo_id)
        total = len(mission.execution_order)
        
        description = f"## {mission.mission_name}\n\n"
        description += f"Part {idx+1}/{total} of coordinated mission\n\n"
        description += f"**Execution Order:**\n"
        
        for i, repo in enumerate(mission.execution_order):
            repo_info = self.repositories.get(repo)
            repo_name = repo_info.repo_name if repo_info else repo
            status = "→ **IN PROGRESS**" if i == idx else "✅" if i < idx else "⏳"
            description += f"\n{status} {repo_name}"
        
        return description
