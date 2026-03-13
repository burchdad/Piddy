"""
Tests for agent functionality fixes.

Verifies that:
1. AutonomousAgent.execute_capability() performs real execution
2. ExecutorAgent.execute_mission() processes steps sequentially
3. Both agents return actual results, not simulated ones
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict

from src.phase50_multi_agent_orchestration import (
    AutonomousAgent, AgentRole, AgentCapability
)
from src.infrastructure.agent_framework import ExecutorAgent


class TestAutonomousAgentExecuteCapability:
    """Test suite for AutonomousAgent.execute_capability() fix"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent"""
        capabilities = [
            AgentCapability(
                capability_id="code_analysis",
                name="Code Analysis",
                description="Analyze code quality",
                estimated_runtime_sec=60
            ),
            AgentCapability(
                capability_id="code_refactoring",
                name="Code Refactoring",
                description="Refactor code",
                estimated_runtime_sec=300
            ),
            AgentCapability(
                capability_id="security_analysis",
                name="Security Analysis",
                description="Analyze security",
                estimated_runtime_sec=120
            ),
        ]
        return AutonomousAgent("test-agent-1", AgentRole.EXECUTOR, capabilities)
    
    @pytest.mark.asyncio
    async def test_execute_capability_returns_success_true(self, agent):
        """Test that execute_capability returns actual success status"""
        result = await agent.execute_capability("code_analysis", {"target": "test.py"})
        
        assert result['success'] == True
        assert result['capability_id'] == 'code_analysis'
        assert 'actual_runtime_sec' in result
        assert result['status'] == 'completed'
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_execute_capability_measures_actual_runtime(self, agent):
        """Test that execution time is actually measured, not hardcoded"""
        result = await agent.execute_capability("code_analysis", {"target": "test.py"})
        
        # Should have measured run-time
        assert 'actual_runtime_sec' in result
        assert result['actual_runtime_sec'] >= 0
        # Should be much less than estimated (0.1-1 second, not 60 seconds)
        assert result['actual_runtime_sec'] < result['estimated_runtime_sec']
    
    @pytest.mark.asyncio
    async def test_execute_capability_returns_result_data_not_generic_message(self, agent):
        """Test that result contains actual data, not generic message"""
        result = await agent.execute_capability("code_analysis", {
            "target": "test.py",
            "metrics_requested": ["complexity", "maintainability"]
        })
        
        # Should not be a generic message like "Executed code_analysis"
        assert isinstance(result['result'], dict)
        assert result['result'] != f"Executed code_analysis"
        # Analysis results should have actual fields
        assert 'findings' in result['result'] or 'analysis_type' in result['result']
    
    @pytest.mark.asyncio
    async def test_execute_capability_handles_error(self, agent):
        """Test that execute_capability handles errors properly"""
        result = await agent.execute_capability("nonexistent_capability", {})
        
        assert result['success'] == False
        assert 'error' in result
        assert result['capability_id'] == 'nonexistent_capability'
    
    @pytest.mark.asyncio
    async def test_execute_capability_tracks_in_history(self, agent):
        """Test that execution is tracked in history"""
        initial_count = len(agent.execution_history)
        
        await agent.execute_capability("code_analysis", {"target": "test.py"})
        
        assert len(agent.execution_history) == initial_count + 1
        last_execution = agent.execution_history[-1]
        assert last_execution['capability_id'] == 'code_analysis'
        assert last_execution['success'] == True
    
    @pytest.mark.asyncio
    async def test_execute_capability_analysis_returns_detailed_results(self, agent):
        """Test analysis capability returns detailed analysis data"""
        result = await agent.execute_capability("code_analysis", {
            "target": "app.py",
            "check_types": ["complexity", "coverage"]
        })
        
        assert result['success'] == True
        analysis_data = result['result']
        
        # Should have analysis fields
        assert 'analysis_type' in analysis_data
        assert 'findings' in analysis_data
        assert 'severity_levels' in analysis_data
        assert isinstance(analysis_data['findings'], list)
    
    @pytest.mark.asyncio
    async def test_execute_capability_security_analysis_includes_checks(self, agent):
        """Test security analysis returns actual security check data"""
        result = await agent.execute_capability("security_analysis", {
            "target": "auth.py",
            "severity_threshold": "high"
        })
        
        assert result['success'] == True
        analysis_data = result['result']
        
        # Should have security findings
        assert analysis_data['analysis_type'] == 'security'
        assert len(analysis_data['findings']) > 0
        # Should have security check results
        first_finding = analysis_data['findings'][0]
        assert 'type' in first_finding
        assert 'status' in first_finding
    
    @pytest.mark.asyncio
    async def test_execute_capability_deployment_returns_step_results(self, agent):
        """Test deployment capability returns actual deployment steps"""
        # Add deployment capability
        deploy_cap = AgentCapability(
            capability_id="deploy",
            name="Deploy",
            description="Deploy application",
            estimated_runtime_sec=600
        )
        agent.capabilities[deploy_cap.capability_id] = deploy_cap
        
        result = await agent.execute_capability("deploy", {
            "environment": "production",
            "version": "1.2.3"
        })
        
        assert result['success'] == True
        deploy_data = result['result']
        
        # Should have deployment steps
        assert 'steps_executed' in deploy_data
        assert len(deploy_data['steps_executed']) > 0
        # Steps should have status
        for step in deploy_data['steps_executed']:
            assert 'step' in step
            assert 'status' in step


class TestExecutorAgentExecuteMission:
    """Test suite for ExecutorAgent.execute_mission() fix"""
    
    @pytest.fixture
    def executor(self):
        """Create test executor agent"""
        return ExecutorAgent("executor-test")
    
    @pytest.mark.asyncio
    async def test_execute_mission_returns_completed_status(self, executor):
        """Test that execute_mission returns completed status"""
        mission_payload = {
            'mission_id': 'test-mission-1',
            'steps': [
                {'action': 'analyze', 'target': 'code.py'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        assert result['status'] == 'completed'
        assert result['success'] == True
        assert result['mission_id'] == 'test-mission-1'
    
    @pytest.mark.asyncio
    async def test_execute_mission_processes_all_steps(self, executor):
        """Test that all mission steps are executed"""
        mission_payload = {
            'mission_id': 'test-mission-2',
            'steps': [
                {'action': 'analyze', 'target': 'code.py'},
                {'action': 'execute', 'command': 'python test.py'},
                {'action': 'validate', 'check_type': 'unit_tests'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        assert result['success'] == True
        assert result['steps_executed'] == 3
        assert len(result['execution_results']) == 3
    
    @pytest.mark.asyncio
    async def test_execute_mission_returns_actual_results_not_empty(self, executor):
        """Test that execution results contain actual data"""
        mission_payload = {
            'mission_id': 'test-mission-3',
            'steps': [
                {'action': 'analyze', 'analysis_type': 'code_quality'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        # Should not have empty result dict
        assert result['result'] != {} if 'result' in result else True
        # Should have execution results
        assert len(result['execution_results']) > 0
        
        step_result = result['execution_results'][0]
        # Step should have actual result data
        assert step_result['success'] == True
        assert step_result['result'] != None
        assert isinstance(step_result['result'], dict)
    
    @pytest.mark.asyncio
    async def test_execute_mission_tracks_step_duration(self, executor):
        """Test that individual step execution time is tracked"""
        mission_payload = {
            'mission_id': 'test-mission-4',
            'steps': [
                {'action': 'execute', 'command': 'test_command'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        step_result = result['execution_results'][0]
        
        # Should have duration for step
        assert 'duration_sec' in step_result
        assert step_result['duration_sec'] >= 0
        # Should have timestamp
        assert 'timestamp' in step_result
    
    @pytest.mark.asyncio
    async def test_execute_mission_tracks_overall_duration(self, executor):
        """Test that overall mission duration is tracked"""
        mission_payload = {
            'mission_id': 'test-mission-5',
            'steps': [
                {'action': 'analyze', 'target': 'code.py'},
                {'action': 'execute', 'command': 'run_tests'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        # Should have overall duration
        assert 'duration_sec' in result
        assert result['duration_sec'] >= 0
        # Should have timestamp
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_execute_mission_handles_deploy_step(self, executor):
        """Test that deploy step returns deployment results"""
        mission_payload = {
            'mission_id': 'test-mission-deploy',
            'steps': [
                {'action': 'deploy', 'environment': 'staging', 'version': '1.0.0'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        step_result = result['execution_results'][0]
        assert step_result['success'] == True
        
        deploy_result = step_result['result']
        assert deploy_result['type'] == 'deployment'
        assert deploy_result['environment'] == 'staging'
        assert 'deployment_id' in deploy_result
        assert deploy_result['status'] == 'successful'
    
    @pytest.mark.asyncio
    async def test_execute_mission_handles_validate_step(self, executor):
        """Test that validation step returns validation results"""
        mission_payload = {
            'mission_id': 'test-mission-validate',
            'steps': [
                {'action': 'validate', 'check_type': 'unit_tests'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        step_result = result['execution_results'][0]
        assert step_result['success'] == True
        
        validate_result = step_result['result']
        assert validate_result['type'] == 'validation'
        assert 'check_type' in validate_result
        assert 'passed' in validate_result
        assert 'checks_performed' in validate_result
    
    @pytest.mark.asyncio
    async def test_execute_mission_handles_multiple_steps(self, executor):
        """Test complex mission with multiple step types"""
        mission_payload = {
            'mission_id': 'test-mission-complex',
            'steps': [
                {'action': 'analyze', 'analysis_type': 'security'},
                {'action': 'execute', 'command': 'apply_fixes'},
                {'action': 'validate', 'check_type': 'security_scan'},
                {'action': 'deploy', 'environment': 'production'},
            ],
            'context': {'priority': 'high'}
        }
        
        result = await executor.execute_mission(mission_payload)
        
        assert result['success'] == True
        assert result['steps_executed'] == 4
        
        # Verify each step type
        results = result['execution_results']
        assert results[0]['result']['type'] == 'analysis'
        assert results[1]['result']['type'] == 'execution'
        assert results[2]['result']['type'] == 'validation'
        assert results[3]['result']['type'] == 'deployment'
    
    @pytest.mark.asyncio
    async def test_execute_mission_handles_unknown_action(self, executor):
        """Test that mission handles unknown action types gracefully"""
        mission_payload = {
            'mission_id': 'test-mission-unknown-action',
            'steps': [
                {'action': 'custom_action', 'parameter': 'value'},
            ],
            'context': {}
        }
        
        result = await executor.execute_mission(mission_payload)
        
        # Mission should complete (handled by generic handler)
        assert result['success'] == True
        # Should have executed the generic handler
        assert result['steps_executed'] == 1
        step_result = result['execution_results'][0]
        assert step_result['success'] == True
        assert step_result['result']['type'] == 'generic'


class TestAgentIntegration:
    """Integration tests for agent fixes"""
    
    @pytest.mark.asyncio
    async def test_autonomous_agent_execution_consistency(self):
        """Test that multiple executions of same capability return consistent structure"""
        agent = AutonomousAgent("integration-test", AgentRole.ANALYZER, [
            AgentCapability(
                capability_id="test_capability",
                name="Test",
                description="Test capability",
                estimated_runtime_sec=30
            )
        ])
        
        result1 = await agent.execute_capability("test_capability", {"param": "value1"})
        result2 = await agent.execute_capability("test_capability", {"param": "value2"})
        
        # Both should have same structure
        assert set(result1.keys()) == set(result2.keys())
        assert result1['success'] == True
        assert result2['success'] == True
        # Both should be timestamped
        assert result1['timestamp'] != result2['timestamp']
    
    @pytest.mark.asyncio
    async def test_executor_mission_creates_step_ids(self):
        """Test that each executed step gets unique ID"""
        executor = ExecutorAgent("step-id-test")
        
        mission_payload = {
            'mission_id': 'step-id-mission',
            'steps': [
                {'action': 'analyze', 'target': 'file1.py'},
                {'action': 'analyze', 'target': 'file2.py'},
            ]
        }
        
        result = await executor.execute_mission(mission_payload)
        
        # Each step should have unique ID
        step_ids = [r['step_id'] for r in result['execution_results']]
        assert len(step_ids) == len(set(step_ids))  # All unique


# Performance tests
class TestAgentPerformance:
    """Performance tests for agent execution"""
    
    @pytest.mark.asyncio
    async def test_execute_capability_completes_quickly(self):
        """Test that capability execution doesn't waste time with sleep"""
        agent = AutonomousAgent("perf-test", AgentRole.EXECUTOR, [
            AgentCapability(
                capability_id="quick_task",
                name="Quick Task",
                description="Fast operation",
                estimated_runtime_sec=300
            )
        ])
        
        start = datetime.utcnow()
        result = await agent.execute_capability("quick_task", {})
        elapsed = (datetime.utcnow() - start).total_seconds()
        
        # Should complete in less than 1 second (not simulate with sleep)
        assert elapsed < 1.0
        # Reported time should match actual
        assert abs(result['actual_runtime_sec'] - elapsed) < 0.1
    
    @pytest.mark.asyncio
    async def test_execute_mission_completes_quickly(self):
        """Test that mission execution doesn't waste time"""
        executor = ExecutorAgent("perf-mission-test")
        
        mission_payload = {
            'mission_id': 'perf-mission',
            'steps': [
                {'action': 'analyze', 'target': 'code.py'},
                {'action': 'validate', 'check_type': 'syntax'},
            ]
        }
        
        start = datetime.utcnow()
        result = await executor.execute_mission(mission_payload)
        elapsed = (datetime.utcnow() - start).total_seconds()
        
        # Should complete in less than 2 seconds
        assert elapsed < 2.0
        # Reported time should match actual
        assert abs(result['duration_sec'] - elapsed) < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
