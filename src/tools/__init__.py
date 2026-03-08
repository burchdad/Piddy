"""Agent tools initialization and management."""

import json
import logging
import asyncio
import threading
from langchain.tools import Tool
from typing import List, Dict, Any
from src.tools.advanced_codegen import generate_rest_endpoint, Language, APIStyle
from src.tools.code_review import analyze_code_quality, suggest_refactoring
from src.tools.design_patterns import get_design_pattern, get_architecture_blueprint, DesignPattern, ArchitecturePattern
from src.tools.database_tools import generate_database_models, generate_migration, generate_index_strategy, DatabaseType
from src.tools.security_analysis import analyze_security, get_security_recommendations
from src.tools.code_analyzer import CodeAnalyzer
from src.tools.git_manager import get_git_manager
from src.tools.phase_3_tools import (
    analyze_code_multilingual,
    generate_boilerplate_code,
    get_cache_statistics,
    clear_cache,
    check_rate_limit,
    get_audit_log,
    get_security_incidents,
    get_system_health,
    get_metrics_summary,
    get_learning_recommendations,
    get_code_quality_trend,
    get_failure_analysis,
)
from src.tools.phase_4_tools import (
    get_cache_statistics as get_redis_cache_stats,
    clear_cache_namespace,
    get_cache_entry,
    set_cache_entry,
    detect_code_patterns,
    get_pattern_recommendations,
    learn_from_code,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    auto_encrypt_config,
    get_encryption_key_fingerprint,
    submit_task_to_agent_pool,
    get_agent_pool_status,
    register_ai_agent,
    get_agent_recommendations,
    trigger_ci_pipeline,
    get_ci_build_metrics,
    get_ci_pipeline_status,
    verify_ci_webhook,
)
from src.utils.memory import get_memory
from src.utils.file_writer import write_generated_file, FileType
from src.utils.error_handler import ErrorHandler
from src.phase32_production import (
    evaluate_refactoring_safety,
    get_refactoring_plan,
    prioritize_testing,
    find_refactoring_opportunities,
    verify_type_safety,
    check_api_compatibility,
    plan_service_refactoring,
)
from src.phase33_planning_integration import Phase33PlanningIntegration
from src.tools.autonomous_tools import (
    autonomous_monitor_start,
    autonomous_monitor_stop,
    autonomous_monitor_status,
    autonomous_analyze_now,
    autonomous_get_prs,
)

logger = logging.getLogger(__name__)


def _run_async_in_thread(coro):
    """
    Run an async coroutine safely, handling cases where an event loop is already running.
    
    If we're in an async context, run the coroutine in a new thread with its own event loop.
    Otherwise, run it directly with asyncio.run().
    """
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        # If we get here, we're in an async context
        logger.debug("Event loop already running, executing async code in thread")
        
        # Create a new event loop in a separate thread
        result_container = {}
        exception_container = {}
        
        def run_in_new_loop():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result_container['result'] = new_loop.run_until_complete(coro)
            except Exception as e:
                exception_container['error'] = e
            finally:
                new_loop.close()
        
        thread = threading.Thread(target=run_in_new_loop, daemon=True)
        thread.start()
        thread.join(timeout=30)  # Wait up to 30 seconds
        
        if exception_container:
            raise exception_container['error']
        
        if 'result' not in result_container:
            logger.warning("Async operation timed out or failed to complete")
            return None
            
        return result_container['result']
        
    except RuntimeError:
        # No event loop is running, use asyncio.run()
        logger.debug("No event loop running, using asyncio.run()")
        return asyncio.run(coro)


def _tool_generate_rest_endpoint(description: str) -> str:
    """Wrapper for REST endpoint generation."""
    try:
        params = json.loads(description)
        result = generate_rest_endpoint(
            endpoint_name=params.get("endpoint_name", "endpoint"),
            http_method=params.get("method", "GET"),
            path=params.get("path", "/"),
            language=Language(params.get("language", "python")),
            framework=params.get("framework", "fastapi"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_analyze_code(code: str) -> str:
    """Wrapper for code quality analysis."""
    try:
        result = analyze_code_quality(code, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_suggest_refactoring(code: str) -> str:
    """Wrapper for refactoring suggestions."""
    try:
        result = suggest_refactoring(code)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_get_design_pattern(pattern_name: str) -> str:
    """Wrapper for design pattern generation."""
    try:
        pattern = DesignPattern(pattern_name.lower())
        result = get_design_pattern(pattern, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_get_architecture(arch_name: str) -> str:
    """Wrapper for architecture blueprint."""
    try:
        architecture = ArchitecturePattern(arch_name.lower())
        result = get_architecture_bluelogger.info(architecture)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_generate_database_model(description: str) -> str:
    """Wrapper for database model generation."""
    try:
        params = json.loads(description)
        result = generate_database_models(
            entity_name=params.get("entity_name", "Entity"),
            fields=params.get("fields", {}),
            language=params.get("language", "python"),
            framework=params.get("framework", "sqlalchemy"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_generate_migration(description: str) -> str:
    """Wrapper for migration generation."""
    try:
        params = json.loads(description)
        result = generate_migration(
            operation=params.get("operation", "create_table"),
            entity_name=params.get("entity_name", "Entity"),
            fields=params.get("fields"),
            language=params.get("language", "python"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_security_analysis(code: str) -> str:
    """Wrapper for security analysis."""
    try:
        result = analyze_security(code, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_security_recommendations(tech_stack: str) -> str:
    """Wrapper for security recommendations."""
    try:
        result = get_security_recommendations(tech_stack)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# Phase 2: Advanced Code Review
def _tool_advanced_code_review(code: str) -> str:
    """Wrapper for advanced code analysis and review."""
    try:
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code, language="python")
        
        # Format for agent consumption
        formatted = {
            "score": result["score"],
            "total_issues": result["summary"]["total"],
            "critical": result["summary"]["critical"],
            "high": result["summary"]["high"],
            "medium": result["summary"]["medium"],
            "low": result["summary"]["low"],
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "line": issue.line,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in result["issues"][:10]  # Top 10 issues
            ],
            "recommendations": result["recommendations"]
        }
        
        return json.dumps(formatted, indent=2)
    except Exception as e:
        logger.error(f"Code review error: {e}")
        return f"Error: {str(e)}"


# Phase 2: Git Integration
def _tool_git_commit(description: str) -> str:
    """Wrapper for Git commit operations."""
    try:
        params = json.loads(description)
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.commit(
            message=params.get("message", "Auto-commit from Piddy"),
            files=params.get("files"),
            auto_stage=params.get("auto_stage", True)
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git commit error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_git_push(description: str) -> str:
    """Wrapper for Git push operations."""
    try:
        params = json.loads(description)
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.push(
            branch=params.get("branch"),
            force=params.get("force", False)
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git push error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_git_status(*args, **kwargs) -> str:
    """Wrapper for checking Git status."""
    try:
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.get_status()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git status error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Phase 2: Memory & Context
def _tool_save_conversation_context(description: str) -> str:
    """Wrapper for saving conversation context."""
    try:
        params = json.loads(description)
        memory = get_memory()
        
        success = memory.create_conversation(
            conversation_id=params.get("conversation_id", ""),
            user_id=params.get("user_id", ""),
            channel_id=params.get("channel_id", ""),
            project_context=params.get("project_context", ""),
            title=params.get("title", "")
        )
        
        return json.dumps({
            "success": success,
            "message": "Context saved" if success else "Context already exists"
        })
    except Exception as e:
        logger.error(f"Save context error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_save_generated_artifact(description: str) -> str:
    """Wrapper for saving generated artifacts."""
    try:
        params = json.loads(description)
        memory = get_memory()
        
        success = memory.save_artifact(
            conversation_id=params.get("conversation_id", ""),
            artifact_type=params.get("artifact_type", "code"),
            content=params.get("content", ""),
            filename=params.get("filename", ""),
            file_path=params.get("file_path", ""),
            language=params.get("language", "python")
        )
        
        return json.dumps({
            "success": success,
            "message": "Artifact saved" if success else "Error saving artifact"
        })
    except Exception as e:
        logger.error(f"Save artifact error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Phase 2: File Writing
def _tool_write_generated_code(description: str) -> str:
    """Wrapper for writing generated code to files."""
    try:
        params = json.loads(description)
        
        file_type = FileType[params.get("file_type", "OTHER").upper()]
        
        result = write_generated_file(
            filename=params.get("filename", "generated.py"),
            content=params.get("content", ""),
            file_type=file_type,
            subdir=params.get("subdir")
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Write file error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Phase 33: Autonomous Planning Loop
_planning_integration = None  # Lazy initialized


def _get_planning_integration() -> Phase33PlanningIntegration:
    """Get or create planning integration"""
    global _planning_integration
    if _planning_integration is None:
        _planning_integration = Phase33PlanningIntegration('.piddy_callgraph.db')
    return _planning_integration


def _tool_execute_autonomous_mission(description: str) -> str:
    """Wrapper for autonomous mission execution"""
    try:
        params = json.loads(description) if isinstance(description, str) else description
        planner = _get_planning_integration()
        
        goal = params.get("goal", "")
        context = params.get("context", {})
        
        if not goal:
            return json.dumps({"success": False, "error": "Goal is required"})
        
        mission = planner.execute_autonomous_mission(goal, context)
        
        return json.dumps({
            "success": True,
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "progress": mission.progress,
            "tasks": len(mission.tasks),
            "completed": mission.completed_tasks,
            "confidence": mission.confidence,
        }, indent=2)
    except Exception as e:
        logger.error(f"Mission execution error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_extract_service_autonomously(description: str) -> str:
    """Wrapper for autonomous service extraction"""
    try:
        params = json.loads(description) if isinstance(description, str) else description
        planner = _get_planning_integration()
        
        mission = planner.extract_service(
            source_module=params.get("source_module", ""),
            target_service=params.get("target_service", ""),
            functions=params.get("functions", [])
        )
        
        return json.dumps({
            "success": True,
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "progress": mission.progress,
            "completed_tasks": mission.completed_tasks,
            "confidence": mission.confidence,
        }, indent=2)
    except Exception as e:
        logger.error(f"Service extraction error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_improve_coverage_autonomously(coverage: str) -> str:
    """Wrapper for autonomous coverage improvement"""
    try:
        planner = _get_planning_integration()
        
        target = float(coverage) if coverage else 0.85
        mission = planner.improve_coverage(target_coverage=target)
        
        return json.dumps({
            "success": True,
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "progress": mission.progress,
            "target_coverage": target,
            "completed_tasks": mission.completed_tasks,
            "confidence": mission.confidence,
        }, indent=2)
    except Exception as e:
        logger.error(f"Coverage improvement error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_cleanup_dead_code_autonomously(min_confidence: str = "0.9") -> str:
    """Wrapper for autonomous dead code cleanup"""
    try:
        planner = _get_planning_integration()
        
        confidence = float(min_confidence) if min_confidence else 0.9
        mission = planner.cleanup_dead_code(min_confidence=confidence)
        
        return json.dumps({
            "success": True,
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "progress": mission.progress,
            "min_confidence": confidence,
            "completed_tasks": mission.completed_tasks,
            "confidence": mission.confidence,
        }, indent=2)
    except Exception as e:
        logger.error(f"Dead code cleanup error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_fix_architecture_autonomously(*args, **kwargs) -> str:
    """Wrapper for autonomous architecture fix"""
    try:
        planner = _get_planning_integration()
        mission = planner.fix_architecture()
        
        return json.dumps({
            "success": True,
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "status": mission.status.value,
            "progress": mission.progress,
            "completed_tasks": mission.completed_tasks,
            "confidence": mission.confidence,
        }, indent=2)
    except Exception as e:
        logger.error(f"Architecture fix error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_query_mission_capability(goal: str) -> str:
    """Wrapper for querying mission capability"""
    try:
        planner = _get_planning_integration()
        capability = planner.query_autonomous_capability(goal)
        
        return json.dumps(capability, indent=2)
    except Exception as e:
        logger.error(f"Capability query error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_get_mission_status(mission_id: str) -> str:
    """Wrapper for getting mission status"""
    try:
        planner = _get_planning_integration()
        mission = planner.get_mission(mission_id)
        
        if mission is None:
            return json.dumps({"success": False, "error": f"Mission {mission_id} not found"})
        
        return json.dumps(mission.to_dict(), indent=2)
    except Exception as e:
        logger.error(f"Mission status error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Autonomous Monitoring Tools - Wrappers for async functions
def _tool_autonomous_monitor_start(interval_str: str = "3600") -> str:
    """Wrapper for starting autonomous monitoring"""
    try:
        interval = int(interval_str) if interval_str else 3600
        result = _run_async_in_thread(autonomous_monitor_start(interval))
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Autonomous monitor start error: {e}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error: {str(e)}", "error": str(e)})


def _tool_autonomous_monitor_stop(*args, **kwargs) -> str:
    """Wrapper for stopping autonomous monitoring"""
    try:
        result = _run_async_in_thread(autonomous_monitor_stop())
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Autonomous monitor stop error: {e}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error: {str(e)}", "error": str(e)})


def _tool_autonomous_monitor_status(*args, **kwargs) -> str:
    """Wrapper for getting autonomous monitor status"""
    try:
        result = _run_async_in_thread(autonomous_monitor_status())
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Autonomous monitor status error: {e}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error: {str(e)}", "error": str(e)})


def _tool_autonomous_analyze_now(*args, **kwargs) -> str:
    """Wrapper for running code analysis immediately"""
    try:
        result = _run_async_in_thread(autonomous_analyze_now())
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Autonomous analyze error: {e}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error: {str(e)}", "error": str(e)})


def _tool_autonomous_get_prs(*args, **kwargs) -> str:
    """Wrapper for getting list of created PRs"""
    try:
        result = _run_async_in_thread(autonomous_get_prs())
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Autonomous get PRs error: {e}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error: {str(e)}", "error": str(e)})


def get_all_tools() -> List[Tool]:
    """Get all available tools for the agent."""
    tools = []
    
    # Code Generation Tools
    tools.extend([
        Tool(
            name="generate_rest_endpoint",
            func=_tool_generate_rest_endpoint,
            description="Generate complete REST API endpoints in FastAPI, Django, Flask, Express, NestJS, Spring Boot, Gin, or Actix. Pass JSON with: endpoint_name, method (GET/POST/PUT/DELETE), path, language, framework"
        ),
        Tool(
            name="generate_graphql_endpoint",
            func=lambda x: "GraphQL endpoint generation - pass query/mutation definition",
            description="Generate GraphQL endpoints and resolver functions"
        ),
    ])
    
    # Code Analysis & Review Tools
    tools.extend([
        Tool(
            name="analyze_code_quality",
            func=_tool_analyze_code,
            description="Analyze code for quality issues, performance problems, security issues, and best practice violations"
        ),
        Tool(
            name="suggest_refactoring",
            func=_tool_suggest_refactoring,
            description="Get refactoring suggestions to improve code quality, performance, and maintainability"
        ),
    ])
    
    # Design Pattern Tools
    tools.extend([
        Tool(
            name="get_design_pattern",
            func=_tool_get_design_pattern,
            description="Get implementation template for design patterns: singleton, factory, strategy, observer, decorator, adapter, builder, repository, middleware, or dependency_injection"
        ),
        Tool(
            name="get_architecture_pattern",
            func=_tool_get_architecture,
            description="Get architecture blueprint: layered, microservices, event_driven, or hexagonal"
        ),
    ])
    
    # Database Tools
    tools.extend([
        Tool(
            name="generate_database_models",
            func=_tool_generate_database_model,
            description="Generate database models for SQLAlchemy, Django ORM, Pydantic, Mongoose, TypeORM, or JPA. Pass JSON with: entity_name, fields dict, language, framework"
        ),
        Tool(
            name="generate_database_migration",
            func=_tool_generate_migration,
            description="Generate database migration scripts for Alembic or Knex. Pass JSON with: operation (create_table/add_column), entity_name, fields"
        ),
    ])
    
    # Security Tools
    tools.extend([
        Tool(
            name="security_analysis",
            func=_tool_security_analysis,
            description="Comprehensive security analysis checking for vulnerabilities, injection attacks, hardcoded credentials, and best practice violations"
        ),
        Tool(
            name="security_recommendations",
            func=_tool_security_recommendations,
            description="Get security best practices and recommendations for your tech stack"
        ),
    ])
    
    # Phase 2: Advanced Code Review
    tools.extend([
        Tool(
            name="advanced_code_review",
            func=_tool_advanced_code_review,
            description="Perform advanced code review analyzing security vulnerabilities, performance issues, best practices, error handling, and type safety. Pass the code to review."
        ),
    ])
    
    # Phase 2: Git Integration
    tools.extend([
        Tool(
            name="git_commit",
            func=_tool_git_commit,
            description="Create a Git commit with generated code. Pass JSON with: message (commit message), files (optional list), auto_stage (true to stage all)."
        ),
        Tool(
            name="git_push",
            func=_tool_git_push,
            description="Push commits to remote repository. Pass JSON with: branch (optional, current branch used if not specified), force (false by default)."
        ),
        Tool(
            name="git_status",
            func=_tool_git_status,
            description="Check current Git repository status including staged, unstaged, and untracked files."
        ),
    ])
    
    # Phase 2: Memory & Context
    tools.extend([
        Tool(
            name="save_conversation_context",
            func=_tool_save_conversation_context,
            description="Save conversation context for future reference. Pass JSON with: conversation_id, user_id, channel_id, project_context, title."
        ),
        Tool(
            name="save_generated_artifact",
            func=_tool_save_generated_artifact,
            description="Save generated code/artifacts to memory. Pass JSON with: conversation_id, artifact_type (code/schema/config), content, filename, file_path, language."
        ),
    ])
    
    # Phase 2: File Writing
    tools.extend([
        Tool(
            name="write_generated_code",
            func=_tool_write_generated_code,
            description="Write generated code to appropriate project location. Pass JSON with: filename, content, file_type (MODEL/ROUTE/UTILITY/SERVICE/SCHEMA/TEST/CONFIG), subdir (optional)."
        ),
    ])
    
    # Phase 3: Multi-Language Support
    tools.extend([
        Tool(
            name="analyze_code_multilingual",
            func=lambda x: json.dumps(analyze_code_multilingual(x), indent=2, default=str),
            description="Analyze code across multiple programming languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby, Kotlin). Auto-detects language if not specified. Returns quality score, security issues, performance issues, and recommendations."
        ),
        Tool(
            name="generate_boilerplate_code",
            func=lambda x: json.dumps(generate_boilerplate_code(x, "api"), indent=2, default=str),
            description="Generate boilerplate code for different programming languages and project types (api, web, cli). Helps bootstrap new projects quickly."
        ),
    ])
    
    # Phase 3: Performance Optimization & Caching
    tools.extend([
        Tool(
            name="get_cache_statistics",
            func=lambda x: json.dumps(get_cache_statistics(), indent=2),
            description="Get cache performance statistics including hit rate, evictions, and current size. Useful for monitoring performance optimization."
        ),
        Tool(
            name="clear_cache",
            func=lambda x: json.dumps(clear_cache(x or "all"), indent=2),
            description="Clear cache to free up memory. Pass 'memory' or 'all' as argument."
        ),
    ])
    
    # Phase 3: Security Hardening
    tools.extend([
        Tool(
            name="check_rate_limit",
            func=lambda user_id: json.dumps(check_rate_limit(user_id), indent=2),
            description="Check rate limit status for a user. Shows remaining requests and limits."
        ),
        Tool(
            name="get_audit_log",
            func=lambda user_id: json.dumps(get_audit_log(user_id, 50), indent=2),
            description="Get audit log for a specific user showing all commands and actions performed."
        ),
        Tool(
            name="get_security_incidents",
            func=lambda hours: json.dumps(get_security_incidents(int(hours) if hours else 24), indent=2),
            description="Get recent security incidents. Pass hours to check (default 24)."
        ),
    ])
    
    # Phase 3: Monitoring & Metrics
    tools.extend([
        Tool(
            name="get_system_health",
            func=lambda x: json.dumps(get_system_health(), indent=2),
            description="Get current system health status including error rates and warnings."
        ),
        Tool(
            name="get_metrics_summary",
            func=lambda minutes: json.dumps(get_metrics_summary(int(minutes) if minutes else 60), indent=2),
            description="Get metrics summary for monitoring. Shows performance metrics over specified time period (minutes)."
        ),
    ])
    
    # Phase 3: Self-Improvement & Learning
    tools.extend([
        Tool(
            name="get_learning_recommendations",
            func=lambda language: json.dumps(get_learning_recommendations(language), indent=2),
            description="Get AI recommendations based on learned patterns from successful code generations. Pass programming language."
        ),
        Tool(
            name="get_code_quality_trend",
            func=lambda language: json.dumps(get_code_quality_trend(language), indent=2),
            description="Get code quality trend analysis for a programming language to see improvement over time."
        ),
        Tool(
            name="get_failure_analysis",
            func=lambda hours: json.dumps(get_failure_analysis(int(hours) if hours else 24), indent=2),
            description="Analyze recent failures to prevent recurrence. Pass hours to analyze (default 24)."
        ),
    ])
    
    # Phase 4: Distributed Caching (Redis)
    tools.extend([
        Tool(
            name="get_redis_cache_stats",
            func=lambda x: json.dumps(get_redis_cache_stats(), indent=2),
            description="Get distributed Redis cache statistics including memory usage, connections, and throughput."
        ),
        Tool(
            name="clear_cache_namespace",
            func=lambda namespace: json.dumps(clear_cache_namespace(namespace or "default"), indent=2),
            description="Clear all cache entries in a specific namespace. Useful for invalidating categories of cached data."
        ),
        Tool(
            name="get_cache_entry",
            func=lambda x: json.dumps(get_cache_entry(x.get('key', '') if isinstance(x, dict) else x, x.get('namespace', 'default') if isinstance(x, dict) else 'default'), indent=2),
            description="Retrieve a specific cache entry by key. Pass JSON with: key, namespace (optional)."
        ),
        Tool(
            name="set_cache_entry",
            func=lambda x: json.dumps(set_cache_entry(x.get('key', ''), x.get('value') if isinstance(x, dict) else None, x.get('ttl', 3600) if isinstance(x, dict) else 3600, x.get('namespace', 'default') if isinstance(x, dict) else 'default'), indent=2),
            description="Set a cache entry with custom TTL. Pass JSON with: key, value, ttl (seconds), namespace (optional)."
        ),
    ])
    
    # Phase 4: ML Pattern Detection
    tools.extend([
        Tool(
            name="detect_code_patterns",
            func=lambda x: json.dumps(detect_code_patterns(x.get('code', '') if isinstance(x, dict) else x, x.get('language', 'python') if isinstance(x, dict) else 'python'), indent=2, default=str),
            description="Use ML to detect patterns, anti-patterns, and optimization opportunities in code. Pass JSON with: code, language (optional, default python)."
        ),
        Tool(
            name="get_pattern_recommendations",
            func=lambda language: json.dumps(get_pattern_recommendations(language or "python"), indent=2, default=str),
            description="Get AI-driven recommendations based on learned code patterns. Pass programming language."
        ),
        Tool(
            name="learn_from_code",
            func=lambda x: json.dumps(learn_from_code(x.get('code', ''), x.get('language', ''), x.get('outcome', ''), x.get('metadata') if isinstance(x, dict) else {}), indent=2),
            description="Teach ML system from successful/failed code patterns. Pass JSON with: code, language, outcome (success/failure), metadata (optional)."
        ),
    ])
    
    # Phase 4: At-Rest Encryption
    tools.extend([
        Tool(
            name="encrypt_sensitive_data",
            func=lambda x: json.dumps(encrypt_sensitive_data(x), indent=2),
            description="Encrypt sensitive data using AES-128 authenticated encryption. Pass data to encrypt (JSON serializable)."
        ),
        Tool(
            name="decrypt_sensitive_data",
            func=lambda x: json.dumps(decrypt_sensitive_data(x.get('encrypted_data', '') if isinstance(x, dict) else x, x.get('return_type', 'auto') if isinstance(x, dict) else 'auto'), indent=2),
            description="Decrypt encrypted data. Pass JSON with: encrypted_data, return_type (optional)."
        ),
        Tool(
            name="auto_encrypt_config",
            func=lambda x: json.dumps(auto_encrypt_config(x), indent=2),
            description="Automatically encrypt sensitive fields in configuration (tokens, passwords, keys, etc)."
        ),
        Tool(
            name="get_encryption_key_fingerprint",
            func=lambda x: json.dumps(get_encryption_key_fingerlogger.info(), indent=2),
            description="Get fingerprint of current encryption key for verification and auditing."
        ),
    ])
    
    # Phase 4: Multi-Agent Coordination
    tools.extend([
        Tool(
            name="submit_task_to_agent_pool",
            func=lambda x: json.dumps(submit_task_to_agent_pool(x.get('task_type', '') if isinstance(x, dict) else '', x.get('description', '') if isinstance(x, dict) else '', x.get('priority', 2) if isinstance(x, dict) else 2, x.get('required_role') if isinstance(x, dict) else None, x.get('required_capabilities') if isinstance(x, dict) else None, x.get('metadata') if isinstance(x, dict) else None), indent=2),
            description="Submit task to multi-agent coordination pool. Pass JSON with: task_type, description, priority (1-4, default 2), required_role (optional), required_capabilities (optional)."
        ),
        Tool(
            name="get_agent_pool_status",
            func=lambda x: json.dumps(get_agent_pool_status(), indent=2),
            description="Get status of multi-agent coordination pool including agents, tasks, and metrics."
        ),
        Tool(
            name="register_ai_agent",
            func=lambda x: json.dumps(register_ai_agent(x.get('agent_name', '') if isinstance(x, dict) else x, x.get('agent_role', '') if isinstance(x, dict) else '', x.get('capabilities', []) if isinstance(x, dict) else []), indent=2),
            description="Register new AI agent in coordination pool. Pass JSON with: agent_name, agent_role, capabilities (list)."
        ),
        Tool(
            name="get_agent_recommendations",
            func=lambda x: json.dumps(get_agent_recommendations(), indent=2),
            description="Get optimization recommendations for agent pool performance."
        ),
    ])
    
    # Phase 4: Advanced CI/CD Integration
    tools.extend([
        Tool(
            name="trigger_ci_pipeline",
            func=lambda x: json.dumps(trigger_ci_pipeline(x.get('platform', '') if isinstance(x, dict) else '', x.get('job_name', '') if isinstance(x, dict) else '', x.get('parameters') if isinstance(x, dict) else None), indent=2),
            description="Trigger CI/CD pipeline on specified platform. Pass JSON with: platform (github_actions, jenkins, gitlab_ci), job_name, parameters (optional)."
        ),
        Tool(
            name="get_ci_build_metrics",
            func=lambda platform: json.dumps(get_ci_build_metrics(platform or None if isinstance(platform, str) else None), indent=2),
            description="Get CI/CD build metrics and success rates. Pass platform name or leave empty for all platforms."
        ),
        Tool(
            name="get_ci_pipeline_status",
            func=lambda x: json.dumps(get_ci_pipeline_status(), indent=2),
            description="Get comprehensive CI/CD orchestrator status and pipeline information."
        ),
        Tool(
            name="verify_ci_webhook",
            func=lambda x: json.dumps(verify_ci_webhook(x.get('platform', '') if isinstance(x, dict) else '', x.get('payload', '') if isinstance(x, dict) else '', x.get('signature', '') if isinstance(x, dict) else '', x.get('secret', '') if isinstance(x, dict) else ''), indent=2),
            description="Verify CI/CD webhook signature for security. Pass JSON with: platform, payload, signature, secret."
        ),
    ])
    
    # Phase 32: Production Hardening & Autonomous Reasoning
    tools.extend([
        Tool(
            name="evaluate_refactoring_safety",
            func=evaluate_refactoring_safety,
            description="Evaluate if a function can be safely refactored using Phase 32 unified reasoning. Pass JSON with: func_id (function identifier), change (type of change: 'optimize'/'bugfix'/'refactor')."
        ),
        Tool(
            name="get_refactoring_plan",
            func=get_refactoring_plan,
            description="Get detailed step-by-step refactoring plan for autonomous agent execution. Pass JSON with: func_id (function identifier)."
        ),
        Tool(
            name="prioritize_testing",
            func=prioritize_testing,
            description="Get AI-prioritized list of functions that need tests, ranked by risk and usefulness. Pass JSON with: limit (optional, default 10)."
        ),
        Tool(
            name="find_refactoring_opportunities",
            func=find_refactoring_opportunities,
            description="Identify code hotspots, duplicate code, and other refactoring opportunities using Phase 32 analysis."
        ),
        Tool(
            name="verify_type_safety",
            func=verify_type_safety,
            description="Verify type compatibility before making a function call. Pass JSON with: caller_id, callee_id, arg_types (list of types being passed)."
        ),
        Tool(
            name="check_api_compatibility",
            func=check_api_compatibility,
            description="Check if API changes would break compatibility with existing contracts. Pass JSON with: func_id, proposed_signature."
        ),
        Tool(
            name="plan_service_refactoring",
            func=plan_service_refactoring,
            description="Plan service extraction or refactoring with safety assessment. Pass JSON with: functions (list of function names), new_service_name."
        ),
    ])
    
    # Phase 33: Autonomous Planning Loop - Multi-Step Missions
    tools.extend([
        Tool(
            name="execute_autonomous_mission",
            func=_tool_execute_autonomous_mission,
            description="Execute a multi-step autonomous mission with Phase 32 validation. Pass JSON with: goal (mission objective), context (optional context dict). Enables coordinated refactoring, testing, cleanup, and architecture work."
        ),
        Tool(
            name="extract_service_autonomously",
            func=_tool_extract_service_autonomously,
            description="Autonomously extract functions into a new service. Handles dependencies, imports, types, tests, contracts, and PR generation. Pass JSON with: source_module, target_service, functions (list of function names)."
        ),
        Tool(
            name="improve_coverage_autonomously",
            func=_tool_improve_coverage_autonomously,
            description="Autonomously improve test coverage to target percentage. Finds gaps, generates tests, validates them, and runs suite. Pass coverage percentage (e.g., '0.85' for 85%) or leave empty for 85%."
        ),
        Tool(
            name="cleanup_dead_code_autonomously",
            func=_tool_cleanup_dead_code_autonomously,
            description="Autonomously remove unreachable code with high confidence. Uses call graph analysis to identify and safely delete dead functions. Pass min_confidence threshold (default 0.9) or leave empty."
        ),
        Tool(
            name="fix_architecture_autonomously",
            func=_tool_fix_architecture_autonomously,
            description="Autonomously fix architectural violations like circular dependencies. Detects issues, plans fixes, validates contracts and types, generates PR."
        ),
        Tool(
            name="query_mission_capability",
            func=_tool_query_mission_capability,
            description="Check if Piddy can autonomously handle a given goal before committing to execution. Pass the goal description to get capability assessment and recommendations."
        ),
        Tool(
            name="get_mission_status",
            func=_tool_get_mission_status,
            description="Get detailed status of a running or completed mission. Pass mission_id to retrieve progress, task list, confidence scores, and results."
        ),
    ])
    
    # Autonomous Monitoring & Self-Healing
    tools.extend([
        Tool(
            name="autonomous_monitor_start",
            func=_tool_autonomous_monitor_start,
            description="Start autonomous code monitoring and self-healing. Optionally pass interval_seconds (default 3600=1 hour). Piddy will continuously analyze codebase, detect issues, and create PRs for fixes."
        ),
        Tool(
            name="autonomous_monitor_stop",
            func=_tool_autonomous_monitor_stop,
            description="Stop autonomous code monitoring. Piddy will no longer analyze codebase or create PRs automatically."
        ),
        Tool(
            name="autonomous_monitor_status",
            func=_tool_autonomous_monitor_status,
            description="Get current status of autonomous monitoring system. Shows enabled/disabled status, issues detected, PRs created, and issue breakdown by severity and type."
        ),
        Tool(
            name="autonomous_analyze_now",
            func=_tool_autonomous_analyze_now,
            description="Run code analysis immediately. Scans entire codebase for print statements, broad exceptions, and TODO comments. Returns detailed issue summary with file locations."
        ),
        Tool(
            name="autonomous_get_prs",
            func=_tool_autonomous_get_prs,
            description="Get list of pull requests created by autonomous monitoring system. Shows PR titles, URLs, and status."
        ),
    ])
    
    return tools
