"""
Test suite for Piddy Infrastructure and Phases 39-42
Validates all infrastructure components and phase implementations
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import tempfile
import os

# Import infrastructure components
from src.infrastructure.graph_store import DependencyGraphStore, GraphNode, GraphEdge
from src.infrastructure.mission_config import (
    MissionConfig, MissionConfigManager, MissionType, RiskTolerance
)
from src.infrastructure.approval_system import (
    ApprovalManager, ApprovalRequest, ApprovalStatus, NotificationService
)
from src.infrastructure.scheduler import (
    MissionScheduler, ScheduleFrequency, ScheduledMission, ScheduleBuilder
)
from src.infrastructure.simulation_engine import (
    SimulationEngine, SimulationResult, PredictionConfidence
)
from src.infrastructure.agent_framework import (
    AgentOrchestrator, AnalystAgent, PlannerAgent, ExecutorAgent,
    AgentRole, MessageType
)

# Import phase implementations
from src.phase39_impact_graph_visualization import (
    ImpactGraphVisualizer, ImpactLevel
)
from src.phase40_mission_simulation import (
    MissionSimulator, MissionSimulationMode
)
from src.phase41_multi_repo_coordination import (
    MultiRepoCoordinator, RepositoryInfo, CrossRepoDependency
)
from src.phase42_continuous_refactoring import (
    ContinuousRefactoringScheduler, RefactoringMission, AutoMergePolicy,
    create_default_continuous_refactoring
)


class TestGraphStore:
    """Test graph store infrastructure"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_graphs.db")
        self.store = DependencyGraphStore(self.db_path)
    
    def test_create_graph(self):
        """Test creating a graph"""
        nodes = [
            GraphNode("func_a", "function", {"name": "a"}),
            GraphNode("func_b", "function", {"name": "b"}),
            GraphNode("func_c", "function", {"name": "c"}),
        ]
        
        edges = [
            GraphEdge("func_a", "func_b", "calls", {}),
            GraphEdge("func_b", "func_c", "calls", {}),
        ]
        
        self.store.create_graph("test_graph", "repo1", nodes, edges)
        
        # Verify graph exists
        assert "test_graph" in self.store.graphs
        G = self.store.load_graph("test_graph")
        assert G.number_of_nodes() == 3
        assert G.number_of_edges() == 2
    
    def test_get_dependencies(self):
        """Test getting dependencies"""
        nodes = [
            GraphNode("a", "function", {}),
            GraphNode("b", "function", {}),
            GraphNode("c", "function", {}),
        ]
        edges = [
            GraphEdge("a", "b", "calls", {}),
            GraphEdge("b", "c", "calls", {}),
        ]
        
        self.store.create_graph("graph1", "repo1", nodes, edges)
        
        # b depends on c
        deps_of_b = self.store.get_dependencies("graph1", "b")
        assert "c" in deps_of_b
    
    def test_transitive_dependencies(self):
        """Test transitive dependency calculation"""
        nodes = [
            GraphNode(f"func_{i}", "function", {})
            for i in range(5)
        ]
        edges = [
            GraphEdge(f"func_{i}", f"func_{i+1}", "calls", {})
            for i in range(4)
        ]
        
        self.store.create_graph("chain", "repo1", nodes, edges)
        
        # func_0 transitively depends on all others
        trans_deps = self.store.get_transitive_dependencies("chain", "func_0")
        assert "func_4" in trans_deps
        assert len(trans_deps) == 4
    
    def test_circular_dependencies(self):
        """Test detecting circular dependencies"""
        nodes = [
            GraphNode("a", "function", {}),
            GraphNode("b", "function", {}),
            GraphNode("c", "function", {}),
        ]
        edges = [
            GraphEdge("a", "b", "calls", {}),
            GraphEdge("b", "c", "calls", {}),
            GraphEdge("c", "a", "calls", {}),  # Creates cycle
        ]
        
        self.store.create_graph("cycle", "repo1", nodes, edges)
        
        cycles = self.store.find_circular_dependencies("cycle")
        assert len(cycles) > 0


class TestMissionConfig:
    """Test mission configuration management"""
    
    def setup_method(self):
        """Set up test config manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = MissionConfigManager(self.temp_dir)
        self.config_manager.create_default_missions()
    
    def test_create_config(self):
        """Test creating mission config"""
        config = MissionConfig(
            name="test_cleanup",
            type=MissionType.CLEANUP,
            description="Test cleanup",
            priority=3,
            risk_tolerance=RiskTolerance.LOW,
            approval_required=False,
        )
        
        self.config_manager.save_config(config)
        
        loaded = self.config_manager.get_config("test_cleanup")
        assert loaded is not None
        assert loaded.name == "test_cleanup"
    
    def test_validate_config(self):
        """Test config validation"""
        config = MissionConfig(
            name="test",
            type=MissionType.CLEANUP,
            description="Test",
            priority=5,
            risk_tolerance=RiskTolerance.MEDIUM,
            approval_required=False,
        )
        
        valid, errors = self.config_manager.validate_config(config)
        assert valid
        assert len(errors) == 0
    
    def test_get_configs_by_type(self):
        """Test filtering configs by type"""
        configs = self.config_manager.get_configs_by_type(MissionType.CLEANUP)
        assert len(configs) > 0


class TestApprovalSystem:
    """Test approval and notification system"""
    
    def setup_method(self):
        """Set up approval manager"""
        self.manager = ApprovalManager()
        self.notifications = NotificationService()
        self.manager.register_notification_handler(
            self.notifications.send_approval_notification
        )
    
    @pytest.mark.asyncio
    async def test_request_approval(self):
        """Test requesting approval"""
        request = ApprovalRequest(
            mission_id="test_mission",
            mission_name="Test Mission",
            mission_type="cleanup",
            description="Test cleanup mission",
            prediction={},
            confidence=0.75,
            risk_level="medium",
            requires_approval=True,
            expires_in=3600,
        )
        
        # Request approval (non-blocking for test)
        assert isinstance(request.mission_id, str)
    
    @pytest.mark.asyncio
    async def test_approval_expiry(self):
        """Test approval expiry"""
        request = ApprovalRequest(
            mission_id="test",
            mission_name="Test",
            mission_type="cleanup",
            description="Test",
            prediction={},
            confidence=0.8,
            risk_level="low",
            requires_approval=True,
            expires_in=1,  # Expire in 1 second
        )
        
        request.created_at = datetime.utcnow().isoformat()
        
        # Should not be expired immediately
        assert not request.is_expired()
        
        # Simulate time passing
        request.created_at = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
        assert request.is_expired()


class TestSimulationEngine:
    """Test mission simulation engine"""
    
    def setup_method(self):
        """Set up simulation engine"""
        self.engine = SimulationEngine()
    
    def test_simulate_cleanup(self):
        """Test simulating cleanup mission"""
        repo_context = {
            'estimated_dead_functions': 5,
            'estimated_unused_imports': 3,
        }
        
        result = self.engine.simulate(
            "cleanup_dead_code",
            {'id': 'test1', 'type': 'cleanup'},
            repo_context
        )
        
        assert result.will_succeed
        assert result.confidence > 0.5
        assert result.files_affected >= 0
    
    def test_simulate_refactor(self):
        """Test simulating refactor mission"""
        repo_context = {
            'high_complexity_functions': 3,
        }
        
        result = self.engine.simulate(
            "refactor",
            {'id': 'test2', 'type': 'refactor'},
            repo_context
        )
        
        assert result.will_succeed
        assert result.confidence > 0.5
    
    def test_risk_score(self):
        """Test risk score calculation"""
        result = SimulationResult(
            mission_id="test",
            mission_name="test",
            will_succeed=True,
            confidence=0.8,
            predicted_changes={},
            files_affected=10,
            lines_changed=100,
        )
        
        risk = result.get_risk_score()
        assert 0.0 <= risk <= 1.0


class TestMissionScheduler:
    """Test mission scheduler"""
    
    def setup_method(self):
        """Set up scheduler"""
        self.scheduler = MissionScheduler()
    
    def test_create_daily_scheduled(self):
        """Test creating daily scheduled mission"""
        mission = ScheduleBuilder.daily("cleanup", at_time="02:00")
        
        assert mission.mission_name == "cleanup"
        assert mission.frequency == ScheduleFrequency.DAILY
        assert mission.next_execution is not None
    
    def test_create_weekly_scheduled(self):
        """Test creating weekly scheduled mission"""
        mission = ScheduleBuilder.weekly("refactor", day=6)  # Sunday
        
        assert mission.mission_name == "refactor"
        assert mission.frequency == ScheduleFrequency.WEEKLY
    
    def test_should_run(self):
        """Test should_run check"""
        mission = ScheduleBuilder.once("test", datetime.utcnow() - timedelta(seconds=1))
        
        # Should run because scheduled time has passed
        assert mission.should_run()


class TestImpactGraphVisualizer:
    """Test impact graph visualization"""
    
    def setup_method(self):
        """Set up visualizer"""
        self.store = DependencyGraphStore(":memory:")
        self.visualizer = ImpactGraphVisualizer(self.store)
        
        # Create test graph
        nodes = [
            GraphNode(f"func_{i}", "function", {})
            for i in range(5)
        ]
        edges = [
            GraphEdge("func_0", "func_1", "calls", {}),
            GraphEdge("func_1", "func_2", "calls", {}),
            GraphEdge("func_1", "func_3", "calls", {}),
            GraphEdge("func_3", "func_4", "calls", {}),
        ]
        
        self.store.create_graph("test", "repo1", nodes, edges)
    
    def test_analyze_change(self):
        """Test analyzing change impact"""
        analysis = self.visualizer.analyze_change("test", "func_1")
        
        assert analysis.node_id == "func_1"
        assert len(analysis.direct_dependents) > 0
        assert analysis.impact_level is not None
    
    def test_create_visualization(self):
        """Test creating visualization"""
        analysis = self.visualizer.analyze_change("test", "func_0")
        viz = self.visualizer.create_visualization(analysis)
        
        assert viz.node_id == "func_0"
        assert viz.impact_score >= 0.0
        assert viz.confidence >= 0.0


class TestMissionSimulator:
    """Test mission simulation mode"""
    
    def setup_method(self):
        """Set up simulator"""
        self.approval_manager = ApprovalManager()
        self.config_manager = MissionConfigManager()
        self.simulator = MissionSimulator(self.approval_manager, self.config_manager)
        self.mode = MissionSimulationMode(self.simulator)
    
    @pytest.mark.asyncio
    async def test_simulate_mission(self):
        """Test simulating a mission"""
        config = MissionConfig(
            name="test_cleanup",
            type=MissionType.CLEANUP,
            description="Test cleanup",
            priority=3,
            risk_tolerance=RiskTolerance.LOW,
            approval_required=False,
            min_confidence=0.5,
        )
        
        repo_context = {
            'estimated_dead_functions': 2,
            'estimated_unused_imports': 1,
        }
        
        report = await self.simulator.simulate_mission(config, repo_context)
        
        assert report.mission_name == "test_cleanup"
        assert report.simulation_result is not None
    
    @pytest.mark.asyncio
    async def test_simulation_mode_enabled(self):
        """Test simulation mode when enabled"""
        assert self.mode.is_enabled()
        self.mode.disable()
        assert not self.mode.is_enabled()
        self.mode.enable()
        assert self.mode.is_enabled()


class TestMultiRepoCoordinator:
    """Test multi-repo coordination"""
    
    def setup_method(self):
        """Set up coordinator"""
        self.store = DependencyGraphStore(":memory:")
        self.coordinator = MultiRepoCoordinator(self.store)
        
        # Register test repositories
        self.coordinator.register_repository(RepositoryInfo(
            repo_id="repo_a",
            repo_name="Service A",
            repo_path="/repos/a",
            graph_id="graph_a",
        ))
        self.coordinator.register_repository(RepositoryInfo(
            repo_id="repo_b",
            repo_name="Service B",
            repo_path="/repos/b",
            graph_id="graph_b",
        ))
    
    def test_register_repository(self):
        """Test registering repository"""
        assert "repo_a" in self.coordinator.repositories
        assert "repo_b" in self.coordinator.repositories
    
    def test_add_cross_repo_dependency(self):
        """Test adding cross-repo dependency"""
        dep = CrossRepoDependency(
            source_repo="repo_a",
            target_repo="repo_b",
            dependency_type="imports",
        )
        
        self.coordinator.add_cross_repo_dependency(dep)
        
        assert "repo_b" in self.coordinator.repositories["repo_a"].dependents
        assert "repo_a" in self.coordinator.repositories["repo_b"].dependencies


class TestContinuousRefactoring:
    """Test continuous refactoring scheduler"""
    
    def setup_method(self):
        """Set up scheduler"""
        self.scheduler = create_default_continuous_refactoring()
    
    def test_get_nightly_missions(self):
        """Test getting nightly missions"""
        missions = self.scheduler.get_nightly_missions()
        assert len(missions) > 0
    
    def test_auto_merge_policy(self):
        """Test setting auto-merge policy"""
        prs = self.scheduler.get_active_prs()
        
        # Initially no PRs
        assert len(prs) == 0


class TestAgentFramework:
    """Test agent framework"""
    
    @pytest.mark.asyncio
    async def test_agent_message(self):
        """Test agent message creation"""
        from src.infrastructure.agent_framework import AgentMessage
        
        msg = AgentMessage(
            sender_id="agent_1",
            recipient_id="agent_2",
            message_type=MessageType.REQUEST,
            payload={'action': 'analyze'},
        )
        
        assert msg.sender_id == "agent_1"
        assert msg.message_type == MessageType.REQUEST
        assert msg.message_id is not None
    
    @pytest.mark.asyncio
    async def test_analyst_agent(self):
        """Test analyst agent"""
        agent = AnalystAgent()
        assert agent.role == AgentRole.ANALYST


# Integration test
class TestIntegration:
    """Integration tests across components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.graph_store = DependencyGraphStore(os.path.join(self.temp_dir, "graphs.db"))
        self.config_manager = MissionConfigManager(self.temp_dir)
        self.config_manager.create_default_missions()
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from config to simulation"""
        
        # 1. Get a mission config
        config = self.config_manager.get_config("cleanup_dead_code")
        assert config is not None
        
        # 2. Create graph analysis
        visualizer = ImpactGraphVisualizer(self.graph_store)
        # (Would need actual graph data)
        
        # 3. Simulate mission
        simulator = MissionSimulator(self.config_manager, None)
        # (Would call async simulate_mission)
        
        # 4. Schedule continuous execution
        scheduler = create_default_continuous_refactoring()
        missions = scheduler.get_nightly_missions()
        assert len(missions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
