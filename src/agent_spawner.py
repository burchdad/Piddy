"""
Agent spawner and lifecycle manager
Initializes agents on system startup and keeps them online
"""

import asyncio
import logging
from typing import List, Dict
from src.coordination.agent_coordinator import AgentCoordinator, AgentRole

logger = logging.getLogger(__name__)


async def spawn_agents(coordinator: AgentCoordinator) -> int:
    """
    Spawn all 12 agents on system startup and mark them as online and active
    
    Returns:
        Number of agents spawned
    """
    agents_to_spawn = [
        ("Guardian", AgentRole.SECURITY_SPECIALIST, ["security_scan", "vulnerability_detection", "threat_analysis"]),
        ("Architect", AgentRole.ARCHITECT, ["design_review", "system_planning", "scalability_analysis"]),
        ("CodeMaster", AgentRole.BACKEND_DEVELOPER, ["code_generation", "bug_fixing", "optimization"]),
        ("Reviewer", AgentRole.CODE_REVIEWER, ["code_review", "quality_assurance", "performance_review"]),
        ("DevOps Pro", AgentRole.DEVOPS_ENGINEER, ["deployment", "infrastructure", "monitoring"]),
        ("Data Expert", AgentRole.DATA_ENGINEER, ["data_pipeline", "analytics", "optimization"]),
        ("Coordinator", AgentRole.COORDINATOR, ["task_distribution", "orchestration", "communication"]),
        ("Perf Analyst", AgentRole.PERFORMANCE_ANALYST, ["profiling", "optimization", "bottleneck_detection"]),
        ("Tech Debt Hunter", AgentRole.TECH_DEBT_HUNTER, ["code_debt_detection", "refactoring", "cleanup"]),
        ("API Compat", AgentRole.API_COMPATIBILITY, ["api_testing", "compatibility_check", "versioning"]),
        ("DB Migration", AgentRole.DATABASE_MIGRATION, ["schema_migration", "data_migration", "optimization"]),
        ("Arch Reviewer", AgentRole.ARCHITECTURE_REVIEWER, ["architecture_review", "design_patterns", "best_practices"]),
        ("Cost Optimizer", AgentRole.COST_OPTIMIZER, ["cost_analysis", "resource_optimization", "budget_tracking"]),
        ("Frontend Dev", AgentRole.FRONTEND_DEVELOPER, ["ui_development", "react_components", "css_styling", "accessibility"]),
        ("Doc Writer", AgentRole.DOCUMENTATION, ["documentation", "api_docs", "user_guides", "changelog"]),
        ("SecTool Dev", AgentRole.SECURITY_TOOLING, ["scanner_development", "rule_authoring", "exploit_detection", "tool_integration"]),
        ("Sec Monitor", AgentRole.SECURITY_MONITORING, ["alert_management", "anomaly_detection", "incident_response", "log_analysis"]),
        ("Load Tester", AgentRole.LOAD_TESTING, ["load_testing", "stress_testing", "capacity_planning", "latency_analysis"]),
        ("Data Guardian", AgentRole.DATA_SECURITY, ["pii_detection", "data_encryption", "retention_policy", "data_cleanup"]),
        ("KB Monitor", AgentRole.KNOWLEDGE_MONITOR, ["kb_sync", "content_validation", "coverage_tracking", "stale_detection"]),
        ("Automator", AgentRole.TASK_AUTOMATION, ["workflow_building", "script_generation", "ci_cd_pipelines", "scheduled_tasks"]),
    ]
    
    spawned_count = 0
    
    for agent_name, agent_role, capabilities in agents_to_spawn:
        try:
            # Register agent
            agent = coordinator.register_agent(agent_name, agent_role, capabilities)
            
            # Mark as online and available
            agent.is_available = True
            
            # Initialize with baseline stats so reputation isn't 0%
            # Give each agent 1 completed task to establish reputation baseline
            agent.completed_tasks = 1
            agent.failed_tasks = 0
            
            # Update last activity to now
            from datetime import datetime
            agent.last_activity = datetime.now().isoformat()
            
            logger.info(f"🟢 Agent spawned and online: {agent_name} ({agent_role.value}) - ID: {agent.id}")
            spawned_count += 1
            
            # Give async time to process
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Failed to spawn agent {agent_name}: {e}")
    
    logger.info(f"✅ Spawned {spawned_count}/{len(agents_to_spawn)} agents successfully")
    return spawned_count


def mark_agents_online(coordinator: AgentCoordinator) -> int:
    """
    Synchronously mark all registered agents as online
    
    Returns:
        Number of agents marked online
    """
    agents = coordinator.get_all_agents()
    count = 0
    
    for agent in agents:
        try:
            agent.is_available = True
            
            # Initialize with baseline stats
            if agent.completed_tasks == 0 and agent.failed_tasks == 0:
                agent.completed_tasks = 1
            
            # Update last activity
            from datetime import datetime
            agent.last_activity = datetime.now().isoformat()
            
            logger.info(f"🟢 {agent.name} online - Reputation: {agent.completed_tasks / max(agent.completed_tasks + agent.failed_tasks, 1):.0%}")
            count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to mark {agent.name} online: {e}")
    
    return count
