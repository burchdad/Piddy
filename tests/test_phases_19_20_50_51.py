"""
Test suite for Phases 19, 20, 50, and 51
Comprehensive testing of production hardening, launch, multi-agent orchestration,
and advanced graph reasoning
"""

import pytest
import asyncio
from datetime import datetime

# Phase 19: Production Hardening
from src.phase19_production_hardening import (
    ProductionSecurityValidator,
    LoadTestEngine,
    ProductionReadinessReport,
    SecurityLevel,
    PerformanceThreshold,
)

# Phase 20: Production Launch
from src.phase20_production_launch import (
    DeploymentPlanner,
    DeploymentConfig,
    DeploymentStrategy,
    HealthChecker,
    IncidentManager,
    ProductionOperationsCenter,
)

# Phase 50: Multi-Agent Orchestration
from src.phase50_multi_agent_orchestration import (
    AutonomousAgent,
    AgentOrchestrator,
    AgentRole,
    ConsensusType,
    MessageType,
    SwarmIntelligence,
)

# Phase 51: Advanced Graph Reasoning
from src.phase51_advanced_graph_reasoning import (
    AdvancedGraphReasoner,
    ArchitectureModel,
    GraphNode,
    GraphEdge,
    EmergentArchitecture,
    ContinuousLearningSystem,
    InsightType,
)


# ============================================================================
# PHASE 19: PRODUCTION HARDENING TESTS
# ============================================================================

class TestProductionSecurityValidator:
    """Test security validation system"""
    
    @pytest.mark.asyncio
    async def test_validator_initialization(self):
        """Test validator initializes with all checks"""
        validator = ProductionSecurityValidator()
        assert len(validator.checks) == 10
        assert "auth_001" in validator.checks
        assert "data_001" in validator.checks
    
    @pytest.mark.asyncio
    async def test_run_security_audit(self):
        """Test running full security audit"""
        validator = ProductionSecurityValidator()
        audit = await validator.run_audit()
        
        assert audit.total_checks > 0
        assert audit.passed_checks >= 0
        assert audit.failed_checks >= 0
        assert audit.total_checks == audit.passed_checks + audit.failed_checks
    
    @pytest.mark.asyncio
    async def test_security_check_levels(self):
        """Test that critical checks are marked correctly"""
        validator = ProductionSecurityValidator()
        critical_checks = [c for c in validator.checks.values() 
                          if c.level == SecurityLevel.CRITICAL]
        
        assert len(critical_checks) > 0
        assert any(c.name == "API authentication enabled" for c in critical_checks)


class TestLoadTestEngine:
    """Test load testing engine"""
    
    @pytest.mark.asyncio
    async def test_graph_store_benchmark(self):
        """Test graph store performance benchmark"""
        engine = LoadTestEngine()
        benchmark = await engine.test_graph_store_performance(node_count=100)
        
        assert benchmark.benchmark_id == "graph_store_perf"
        assert benchmark.operation_count > 0
        assert benchmark.ops_per_second >= 0
        assert benchmark.avg_latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_simulation_benchmark(self):
        """Test simulation engine benchmark"""
        engine = LoadTestEngine()
        benchmark = await engine.test_simulation_performance(simulation_count=10)
        
        assert benchmark.benchmark_id == "simulation_perf"
        assert benchmark.operation_count > 0
        assert benchmark.avg_latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_scheduler_benchmark(self):
        """Test mission scheduler benchmark"""
        engine = LoadTestEngine()
        benchmark = await engine.test_mission_scheduling(mission_count=10)
        
        assert benchmark.benchmark_id == "scheduler_perf"
        assert benchmark.operation_count > 0
    
    def test_benchmark_summary(self):
        """Test benchmark summary generation"""
        engine = LoadTestEngine()
        # Add mock benchmarks
        engine.benchmarks = []
        engine.benchmarks.append(type('obj', (object,), {
            'name': 'test1',
            'passed': True,
            'ops_per_second': 100,
            'avg_latency_ms': 10
        })())
        
        summary = engine.get_benchmark_summary()
        assert summary['total_benchmarks'] == 1
        assert summary['passed'] == 1
        assert summary['failed'] == 0


class TestProductionReadiness:
    """Test production readiness assessment"""
    
    @pytest.mark.asyncio
    async def test_readiness_report_generation(self):
        """Test generating readiness report"""
        report = ProductionReadinessReport()
        result = await report.generate(run_load_tests=False)
        
        assert 'timestamp' in result
        assert 'ready_for_production' in result
        assert 'security_audit' in result
        assert 'recommendation' in result
    
    def test_readiness_recommendation(self):
        """Test readiness recommendations"""
        report = ProductionReadinessReport()
        
        # Test approved recommendation
        report.ready_for_production = True
        rec = report._get_recommendation()
        assert "APPROVED" in rec


# ============================================================================
# PHASE 20: PRODUCTION LAUNCH TESTS
# ============================================================================

class TestDeploymentPlanner:
    """Test deployment planning"""
    
    def test_blue_green_plan_creation(self):
        """Test creating blue-green deployment plan"""
        planner = DeploymentPlanner()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment="production",
            docker_image="piddy:2.0.0",
        )
        
        plan = planner.create_blue_green_plan(config)
        
        assert plan.plan_id is not None
        assert len(plan.steps) > 0
        assert plan.steps[0].phase.value == "pre_deployment"
    
    def test_canary_plan_creation(self):
        """Test creating canary deployment plan"""
        planner = DeploymentPlanner()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.CANARY,
            environment="production",
            docker_image="piddy:2.0.0",
        )
        
        plan = planner.create_canary_plan(config)
        
        assert plan.plan_id is not None
        assert len(plan.steps) > 5  # Canary has more steps
    
    @pytest.mark.asyncio
    async def test_plan_validation(self):
        """Test deployment plan validation"""
        planner = DeploymentPlanner()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment="production",
            docker_image="piddy:2.0.0",
            replicas=3,
        )
        
        plan = planner.create_blue_green_plan(config)
        valid, issues = await planner.validate_plan(plan)
        
        assert isinstance(valid, bool)
        assert isinstance(issues, list)


class TestHealthChecker:
    """Test health checking"""
    
    @pytest.mark.asyncio
    async def test_instance_health_check(self):
        """Test checking instance health"""
        checker = HealthChecker()
        status = await checker.check_instance_health("instance-1")
        
        assert status is not None
        assert "instance-1" in checker.instances
        assert len(checker.instances["instance-1"].health_checks) > 0


class TestIncidentManager:
    """Test incident management"""
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self):
        """Test anomaly detection"""
        manager = IncidentManager()
        
        current = {
            'error_rate': 0.15,  # 15% errors (2x baseline)
            'avg_latency_ms': 300,
        }
        baseline = {
            'error_rate': 0.05,
            'avg_latency_ms': 150,
        }
        
        anomaly = await manager.detect_anomaly(current, baseline)
        
        assert anomaly['detected'] is True
        assert len(anomaly['anomalies']) > 0
    
    @pytest.mark.asyncio
    async def test_rollback_initiation(self):
        """Test initiating rollback"""
        manager = IncidentManager()
        rollback = await manager.initiate_rollback("plan_123", "Error rate exceeded")
        
        assert rollback['plan_id'] == "plan_123"
        assert rollback['status'] == 'in_progress'


class TestProductionOperationsCenter:
    """Test operations center"""
    
    @pytest.mark.asyncio
    async def test_stage_deployment(self):
        """Test staging deployment"""
        ops = ProductionOperationsCenter()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment="production",
            docker_image="piddy:2.0.0",
            replicas=3,
        )
        
        plan = await ops.stage_deployment(config)
        assert plan.plan_id is not None
        assert plan.approved is False
    
    @pytest.mark.asyncio
    async def test_deployment_approval(self):
        """Test approving deployment"""
        ops = ProductionOperationsCenter()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment="production",
            docker_image="piddy:2.0.0",
            replicas=3,
        )
        
        plan = await ops.stage_deployment(config)
        await ops.approve_deployment(plan, "DevOps Team")
        
        assert plan.approved is True
        assert plan.approval_user == "DevOps Team"


# ============================================================================
# PHASE 50: MULTI-AGENT ORCHESTRATION TESTS
# ============================================================================

class TestAutonomousAgent:
    """Test autonomous agents"""
    
    def test_agent_creation(self):
        """Test creating an agent"""
        agent = AutonomousAgent(
            agent_id="analyzer_001",
            role=AgentRole.ANALYZER,
            capabilities=[]
        )
        
        assert agent.agent_id == "analyzer_001"
        assert agent.role == AgentRole.ANALYZER
        assert agent.reputation.agent_id == "analyzer_001"
    
    @pytest.mark.asyncio
    async def test_agent_message_handling(self):
        """Test agent message handling"""
        from src.phase50_multi_agent_orchestration import Message
        
        agent = AutonomousAgent(
            agent_id="executor_001",
            role=AgentRole.EXECUTOR,
            capabilities=[]
        )
        
        message = Message(
            sender_id="analyzer_001",
            receiver_id="executor_001",
            message_type=MessageType.PROPOSAL,
        )
        
        await agent.receive_message(message)
        assert agent.inbox.qsize() > 0
    
    @pytest.mark.asyncio
    async def test_agent_proposal(self):
        """Test agent creating proposal"""
        agent = AutonomousAgent(
            agent_id="analyzer_001",
            role=AgentRole.ANALYZER,
            capabilities=[]
        )
        
        proposal = await agent.propose_action(
            "analyze_code",
            {"file": "app.py"}
        )
        
        assert proposal.proposal_id is not None
        assert proposal.proposer_id == "analyzer_001"
        assert proposal.action == "analyze_code"


class TestAgentOrchestrator:
    """Test agent orchestration"""
    
    def test_orchestrator_creation(self):
        """Test creating orchestrator"""
        orchestrator = AgentOrchestrator()
        assert len(orchestrator.agents) == 0
    
    def test_agent_registration(self):
        """Test registering agents"""
        orchestrator = AgentOrchestrator()
        agent = AutonomousAgent(
            agent_id="test_001",
            role=AgentRole.ANALYZER,
            capabilities=[]
        )
        
        orchestrator.register_agent(agent)
        assert "test_001" in orchestrator.agents
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self):
        """Test broadcasting messages"""
        from src.phase50_multi_agent_orchestration import Message
        
        orchestrator = AgentOrchestrator()
        agent1 = AutonomousAgent("agent_1", AgentRole.ANALYZER, [])
        agent2 = AutonomousAgent("agent_2", AgentRole.VALIDATOR, [])
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        message = Message(
            sender_id="system",
            message_type=MessageType.ALERT,
        )
        
        await orchestrator.broadcast_message(message)
        
        # Message logged
        assert len(orchestrator.message_log) > 0
    
    @pytest.mark.asyncio
    async def test_consensus_evaluation(self):
        """Test consensus evaluation"""
        from src.phase50_multi_agent_orchestration import Proposal, Vote, VoteOutcome
        
        orchestrator = AgentOrchestrator()
        proposal = Proposal(
            proposal_id="prop_001",
            proposer_id="agent_1",
            action="test_action",
            required_consensus=ConsensusType.MAJORITY,
        )
        
        # Add votes
        proposal.votes["agent_1"] = Vote(
            vote_id="vote_1",
            proposal_id="prop_001",
            agent_id="agent_1",
            outcome=VoteOutcome.APPROVED,
        )
        proposal.votes["agent_2"] = Vote(
            vote_id="vote_2",
            proposal_id="prop_001",
            agent_id="agent_2",
            outcome=VoteOutcome.APPROVED,
        )
        proposal.votes["agent_3"] = Vote(
            vote_id="vote_3",
            proposal_id="prop_001",
            agent_id="agent_3",
            outcome=VoteOutcome.REJECTED,
        )
        
        approved, consensus_info = await orchestrator.evaluate_consensus(proposal)
        
        assert approved is True  # 2/3 approved, majority met


class TestSwarmIntelligence:
    """Test swarm intelligence"""
    
    def test_swarm_creation(self):
        """Test creating swarm intelligence"""
        orchestrator = AgentOrchestrator()
        swarm = SwarmIntelligence(orchestrator)
        
        assert swarm.orchestrator == orchestrator
    
    @pytest.mark.asyncio
    async def test_collective_behavior_analysis(self):
        """Test analyzing collective behavior"""
        orchestrator = AgentOrchestrator()
        swarm = SwarmIntelligence(orchestrator)
        
        analysis = await swarm.analyze_collective_behavior()
        
        assert 'timestamp' in analysis
        assert 'total_messages' in analysis
        assert 'message_patterns' in analysis


# ============================================================================
# PHASE 51: ADVANCED GRAPH REASONING TESTS
# ============================================================================

class TestAdvancedGraphReasoner:
    """Test advanced graph reasoning"""
    
    def test_reasoner_creation(self):
        """Test creating reasoner"""
        reasoner = AdvancedGraphReasoner()
        assert len(reasoner.models) == 0
        assert len(reasoner.insights) == 0
    
    def test_architecture_model_creation(self):
        """Test creating architecture model"""
        reasoner = AdvancedGraphReasoner()
        model = reasoner.create_model("test_app")
        
        assert model.model_id is not None
        assert model.name == "test_app"
        assert model.model_id in reasoner.models
    
    def test_model_nodes_and_edges(self):
        """Test adding nodes and edges to model"""
        model = ArchitectureModel(
            model_id="test",
            name="Test Model"
        )
        
        node1 = GraphNode("api", "service", "API Service")
        node2 = GraphNode("db", "service", "Database")
        
        model.add_node(node1)
        model.add_node(node2)
        
        edge = GraphEdge("api", "db", "queries")
        model.add_edge(edge)
        
        assert len(model.nodes) == 2
        assert len(model.edges) == 1
    
    def test_model_dependency_queries(self):
        """Test querying dependencies"""
        model = ArchitectureModel(
            model_id="test",
            name="Test Model"
        )
        
        # Create chain: A -> B -> C
        model.add_node(GraphNode("a", "module", "A"))
        model.add_node(GraphNode("b", "module", "B"))
        model.add_node(GraphNode("c", "module", "C"))
        
        model.add_edge(GraphEdge("a", "b", "calls"))
        model.add_edge(GraphEdge("b", "c", "calls"))
        
        # Query dependencies
        deps = model.get_dependencies("a", depth=2)
        
        assert "b" in deps
        assert "c" in deps
    
    @pytest.mark.asyncio
    async def test_dependency_analysis(self):
        """Test dependency analysis"""
        reasoner = AdvancedGraphReasoner()
        model = reasoner.create_model("test_app")
        
        # Add simple graph
        model.add_node(GraphNode("service_a", "service", "A"))
        model.add_node(GraphNode("service_b", "service", "B"))
        model.add_edge(GraphEdge("service_a", "service_b", "calls"))
        
        insights = await reasoner.analyze_dependencies(model)
        
        assert isinstance(insights, list)
    
    @pytest.mark.asyncio
    async def test_hotspot_analysis(self):
        """Test hotspot analysis"""
        reasoner = AdvancedGraphReasoner()
        model = reasoner.create_model("test_app")
        
        # Create hub-spoke structure
        hub = GraphNode("core", "service", "Core Service")
        model.add_node(hub)
        
        for i in range(5):
            spoke = GraphNode(f"service_{i}", "service", f"Service {i}")
            model.add_node(spoke)
            model.add_edge(GraphEdge(f"service_{i}", "core", "calls"))
        
        insights = await reasoner.analyze_hotspots(model)
        
        assert len(insights) > 0
    
    @pytest.mark.asyncio
    async def test_recommendations(self):
        """Test generating recommendations"""
        reasoner = AdvancedGraphReasoner()
        mock_insights = [
            type('Insight', (), {
                'title': 'Test',
                'insight_type': type('Type', (), {'value': 'test'}),
                'priority': 5,
                'confidence': type('Conf', (), {'value': 0.8}),
            })()
        ]
        
        recommendations = await reasoner.provide_recommendations(mock_insights)
        
        assert 'timestamp' in recommendations
        assert 'total_insights' in recommendations


class TestEmergentArchitecture:
    """Test emergent architecture tracking"""
    
    def test_architecture_creation(self):
        """Test creating emergent architecture tracker"""
        reasoner = AdvancedGraphReasoner()
        arch = EmergentArchitecture(reasoner)
        
        assert arch.reasoner == reasoner
    
    @pytest.mark.asyncio
    async def test_evolution_analysis(self):
        """Test analyzing architectural evolution"""
        reasoner = AdvancedGraphReasoner()
        arch = EmergentArchitecture(reasoner)
        
        evolution = await arch.analyze_architectural_evolution()
        
        assert 'timestamp' in evolution
        assert 'insights_count' in evolution


class TestContinuousLearning:
    """Test continuous learning system"""
    
    def test_learner_creation(self):
        """Test creating learning system"""
        reasoner = AdvancedGraphReasoner()
        learner = ContinuousLearningSystem(reasoner)
        
        assert learner.reasoner == reasoner
        assert len(learner.feedback_log) == 0
    
    @pytest.mark.asyncio
    async def test_outcome_recording(self):
        """Test recording outcomes"""
        reasoner = AdvancedGraphReasoner()
        learner = ContinuousLearningSystem(reasoner)
        
        await learner.record_outcome("insight_1", accepted=True, result_quality=0.9)
        
        assert len(learner.feedback_log) > 0
        assert learner.feedback_log[0]['accepted'] is True
    
    @pytest.mark.asyncio
    async def test_model_improvement(self):
        """Test improving recommendation model"""
        reasoner = AdvancedGraphReasoner()
        learner = ContinuousLearningSystem(reasoner)
        
        # Add feedback
        await learner.record_outcome("insight_1", True, 0.95)
        await learner.record_outcome("insight_2", True, 0.90)
        await learner.record_outcome("insight_3", False, 0.50)
        
        improvement = await learner.improve_recommendation_model()
        
        assert 'acceptance_rate' in improvement
        assert 'average_quality' in improvement


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullIntegration:
    """Test integration across phases"""
    
    @pytest.mark.asyncio
    async def test_deployment_to_orchestration_flow(self):
        """Test flow from deployment to agent orchestration"""
        
        # Phase 20: Deploy system
        ops = ProductionOperationsCenter()
        config = DeploymentConfig(
            app_name="piddy",
            version="2.0.0",
            strategy=DeploymentStrategy.CANARY,
            environment="production",
            docker_image="piddy:2.0.0",
            replicas=3,
        )
        
        plan = await ops.stage_deployment(config)
        assert plan is not None
        
        # Phase 50: Set up agents for post-deployment orchestration
        orchestrator = AgentOrchestrator()
        
        analyzer = AutonomousAgent("analyzer_1", AgentRole.ANALYZER, [])
        validator = AutonomousAgent("validator_1", AgentRole.VALIDATOR, [])
        executor = AutonomousAgent("executor_1", AgentRole.EXECUTOR, [])
        
        orchestrator.register_agent(analyzer)
        orchestrator.register_agent(validator)
        orchestrator.register_agent(executor)
        
        # Verify orchestration ready
        assert len(orchestrator.agents) == 3
    
    @pytest.mark.asyncio
    async def test_reasoning_to_learning_flow(self):
        """Test flow from reasoning to learning"""
        
        # Phase 51: Create reasoner
        reasoner = AdvancedGraphReasoner()
        model = reasoner.create_model("app")
        
        model.add_node(GraphNode("module_a", "module", "ModuleA"))
        model.add_node(GraphNode("module_b", "module", "ModuleB"))
        model.add_edge(GraphEdge("module_a", "module_b", "calls"))
        
        # Generate insights
        insights = await reasoner.analyze_dependencies(model)
        
        # Phase 51: Learn from outcomes
        learner = ContinuousLearningSystem(reasoner)
        
        for insight in insights:
            await learner.record_outcome(
                insight.insight_id,
                accepted=True,
                result_quality=0.85
            )
        
        # Verify learning
        assert len(learner.feedback_log) > 0
        assert learner.learning_metrics['acceptance_rate'] > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_agent_message_throughput(self):
        """Test agent message throughput"""
        from src.phase50_multi_agent_orchestration import Message
        
        orchestrator = AgentOrchestrator()
        
        # Register 10 agents
        for i in range(10):
            agent = AutonomousAgent(
                f"agent_{i}",
                AgentRole.ANALYZER if i % 2 == 0 else AgentRole.VALIDATOR,
                []
            )
            orchestrator.register_agent(agent)
        
        # Send 100 messages
        start = datetime.utcnow()
        for i in range(100):
            message = Message(
                sender_id="system",
                message_type=MessageType.QUERY,
            )
            await orchestrator.broadcast_message(message)
        
        duration = (datetime.utcnow() - start).total_seconds()
        throughput = 100 / duration if duration > 0 else 0
        
        # Should be able to broadcast 100 messages in <1 second
        assert throughput > 50  # At least 50 msg/sec
    
    @pytest.mark.asyncio
    async def test_graph_analysis_performance(self):
        """Test graph analysis performance"""
        reasoner = AdvancedGraphReasoner()
        model = reasoner.create_model("large_app")
        
        # Create 100-node graph
        for i in range(100):
            node = GraphNode(f"service_{i}", "service", f"Service {i}")
            model.add_node(node)
            
            if i > 0:
                model.add_edge(GraphEdge(f"service_{i-1}", f"service_{i}", "calls"))
        
        # Analyze
        start = datetime.utcnow()
        insights = await reasoner.analyze_dependencies(model)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Should complete in <1 second
        assert duration < 1.0


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
