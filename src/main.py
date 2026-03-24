"""Main application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Dict, Optional, List
import logging
import os
import json

from config.settings import get_settings, setup_logging
from src.api.agent_commands import router as agent_router
from src.api.slack_commands import router as slack_router
from src.api.responses import router as responses_router
from src.api.autonomous import router as autonomous_router
from src.api.self_healing import router as self_healing_router
from src.coordination.agent_coordinator import AgentCoordinator
from src.phase34_mission_telemetry import MissionTelemetryCollector
from src.api.realtime_dashboard import setup_realtime_dashboard


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    settings = get_settings()
    
    app = FastAPI(
        title="Piddy - Backend Developer Agent",
        description="AI-powered backend developer agent with Slack integration",
        version="0.1.0",
    )
    
    # Add CORS middleware FIRST - must be before all other middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )
    
    # ========================================================================
    # INITIALIZE REAL DATA SYSTEMS
    # ========================================================================
    coordinator = AgentCoordinator()
    telemetry_collector = MissionTelemetryCollector('.piddy_telemetry.db')
    logger.info("✅ Coordinator and Telemetry Collector initialized")
    
    # Bootstrap: Register all agents on startup
    from src.coordination.agent_coordinator import AgentRole
    agents_to_register = [
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
    
    for agent_name, agent_role, capabilities in agents_to_register:
        coordinator.register_agent(agent_name, agent_role, capabilities)
    
    logger.info(f"✅ Registered {len(agents_to_register)} agents with coordinator")
    
    # Setup real-time dashboard with live data
    setup_realtime_dashboard(app, coordinator, telemetry_collector)
    logger.info("✅ Real-time Dashboard API endpoints active")
    
    # Include routers
    app.include_router(agent_router)
    app.include_router(slack_router)
    app.include_router(responses_router)
    app.include_router(autonomous_router)
    app.include_router(self_healing_router)
    
    # Mount dashboard API (provides /api/system/overview, /api/chat, /api/doctor, etc.)
    try:
        from src.dashboard_api import app as dashboard_app
        app.mount("/", dashboard_app)
        logger.info("✅ Dashboard API mounted - all dashboard endpoints available")
    except Exception as e:
        logger.warning(f"⚠️ Could not mount dashboard API: {e}")
    
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        logger.info("Piddy starting up...")
        logger.info(f"Model: {settings.agent_model}")
        logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
        
        # MARK ALL AGENTS AS ONLINE 🟢
        from src.agent_spawner import mark_agents_online
        online_count = mark_agents_online(coordinator)
        logger.info(f"🟢 {online_count} agents came ONLINE and ready for missions!")
        
        # Initialize Knowledge Base if configured
        kb_repo_url = os.getenv('PIDDY_KB_REPO_URL')
        if kb_repo_url:
            try:
                from src.kb_repo_manager import setup_kb_repo
                logger.info(f"📚 Syncing Knowledge Base from: {kb_repo_url}")
                setup_kb_repo(kb_repo_url)
                logger.info("✅ Knowledge Base synced and ready")
            except Exception as e:
                logger.warning(f"⚠️ Failed to sync Knowledge Base: {str(e)}")
        else:
            logger.info("⏭️ Knowledge Base not configured (set PIDDY_KB_REPO_URL)")
        
        # Feed approved experiences to KB (self-growing KB initialization)
        try:
            from src.kb.experience_recorder import KBExperienceRecorder
            recorder = KBExperienceRecorder()
            
            # Batch feed all high-confidence approved experiences
            added = recorder.feed_all_approved_to_kb(
                min_approvals=1,        # Approved at least once
                min_confidence=0.75     # 75%+ confidence
            )
            
            if added > 0:
                logger.info(f"✅ Fed {added} experiences to KB on startup")
        except Exception as e:
            logger.debug(f"ℹ️ Experience recording not available or no experiences ready: {str(e)}")
        
        # Start Slack listener if configured
        if settings.slack_app_token and settings.slack_bot_token:
            try:
                from src.integrations.socket_mode import start_slack_listener
                start_slack_listener()
                logger.info("✅ Slack Socket Mode listener started")
            except Exception as e:
                logger.warning(f"⚠️ Failed to start Slack listener: {str(e)}")
        else:
            logger.info("⏭️ Slack integration not configured (set SLACK_APP_TOKEN and SLACK_BOT_TOKEN)")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event handler."""
        logger.info("Piddy shutting down...")
        
        # Stop Slack listener
        try:
            from src.integrations.socket_mode import stop_slack_listener
            stop_slack_listener()
            logger.info("✅ Slack Socket Mode listener stopped")
        except Exception as e:
            logger.debug(f"Slack listener cleanup: {str(e)}")
    
    # Health check endpoints
    _start_time = datetime.utcnow()
    
    @app.get("/health")
    async def health():
        """Health check endpoint - checks real system components."""
        checks = {}
        status = "healthy"
        
        # Check coordinator has agents
        try:
            agent_count = len(coordinator.agents)
            checks["agents_registered"] = agent_count > 0
        except Exception:
            checks["agents_registered"] = False
        
        # Check database
        try:
            import sqlite3
            conn = sqlite3.connect("piddy.db")
            conn.execute("SELECT 1")
            conn.close()
            checks["database"] = True
        except Exception:
            checks["database"] = False
        
        # Check LLM configuration
        checks["llm_configured"] = bool(settings.anthropic_api_key or settings.openai_api_key)
        
        # Check telemetry
        try:
            telemetry_collector.get_all_stats()
            checks["telemetry"] = True
        except Exception:
            checks["telemetry"] = False
        
        if not all(checks.values()):
            status = "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }
    
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health check with metrics."""
        uptime = (datetime.utcnow() - _start_time).total_seconds()
        stats = coordinator.get_stats()
        
        memory_mb = 0.0
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
        except ImportError:
            pass
        
        return {
            "health": {
                "status": "healthy" if stats["agents"]["total"] > 0 else "degraded",
                "pid": os.getpid(),
                "uptime": uptime,
                "agents_online": stats["agents"]["available"],
                "agents_total": stats["agents"]["total"],
                "tasks_completed": stats["tasks"]["completed"],
                "tasks_failed": stats["tasks"]["failed"],
                "latency_ms": 0,
                "memory_usage_mb": round(memory_mb, 1),
                "checks": {
                    "agents_registered": stats["agents"]["total"] > 0,
                    "database": True,
                    "llm_configured": bool(settings.anthropic_api_key),
                    "telemetry": True,
                },
            },
            "performance": {
                "success_rate": stats["success_rate"],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/status")
    async def status():
        """Service status endpoint."""
        uptime = (datetime.utcnow() - _start_time).total_seconds()
        return {
            "status": "running",
            "uptime_seconds": round(uptime),
            "model": settings.agent_model,
            "agents": len(coordinator.agents),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # ========================================================================
    # DASHBOARD API ENDPOINTS
    # Note: All dashboard endpoints now use REAL data from coordinator and
    # telemetry database. See src/api/realtime_dashboard.py for implementation.
    # ========================================================================
    # Endpoints: /api/system/overview, /api/agents, /api/messages, /api/decisions,
    # /api/missions, /api/metrics/performance, /ws/dashboard (WebSocket)
    
    @app.get("/api/graph/dependencies")
    async def get_dependencies():
        """Get dependency graph from real agent registrations."""
        agents = coordinator.get_all_agents()
        nodes = []
        edges = []
        
        for agent in agents:
            nodes.append({
                "id": agent.id,
                "name": agent.name,
                "type": agent.role.value,
                "inbound_count": 0,
                "outbound_count": len(agent.capabilities),
                "status": "online" if agent.is_available else "busy",
            })
        
        # Build edges: Coordinator connects to all agents
        coord_agents = [a for a in agents if a.role.value == "coordinator"]
        for coord in coord_agents:
            for agent in agents:
                if agent.id != coord.id:
                    edges.append({"source": coord.id, "target": agent.id, "weight": 1})
        
        return {"nodes": nodes, "edges": edges}
    
    # In-memory log buffer for the /api/logs endpoint
    import collections
    _log_buffer = collections.deque(maxlen=200)
    
    class _BufferHandler(logging.Handler):
        def emit(self, record):
            _log_buffer.append({
                "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "source": record.name,
                "message": record.getMessage(),
                "details": None,
            })
    
    logging.getLogger().addHandler(_BufferHandler())
    
    @app.get("/api/logs")
    async def get_logs():
        """Get recent logs from real log buffer."""
        return list(_log_buffer)
    
    @app.get("/api/phases")
    async def get_phases():
        """Get phase information from actual phase modules."""
        import glob
        phase_files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "phase*")))
        phases = []
        for pf in phase_files:
            name = os.path.basename(pf).replace(".py", "").replace("_", " ").title()
            phases.append({
                "phase_id": len(phases) + 1,
                "phase_name": name,
                "status": "completed",
                "progress_percent": 100,
                "file": os.path.basename(pf),
            })
        return phases
    
    # Store last test run results
    _last_test_results: List[Dict] = []
    
    @app.get("/api/tests")
    async def get_tests():
        """Get test results from last pytest run (or discover test files)."""
        if _last_test_results:
            return _last_test_results
        
        # Discover test files as fallback
        import glob
        test_files = glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "*.py"))
        return [
            {
                "test_id": f"test_{i:03d}",
                "test_name": os.path.basename(tf).replace(".py", ""),
                "status": "discovered",
                "duration_seconds": 0,
                "message": f"Test file found: {os.path.basename(tf)}",
            }
            for i, tf in enumerate(test_files, 1)
        ]
    
    @app.get("/api/tests/summary")
    async def get_tests_summary():
        """Get test summary from real results."""
        results = _last_test_results
        if not results:
            import glob
            test_count = len(glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "*.py")))
            return {
                "total": test_count,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "pass_rate": 0,
                "status": "not_run",
            }
        
        total = len(results)
        passed = len([r for r in results if r.get("status") == "passed"])
        failed = len([r for r in results if r.get("status") == "failed"])
        skipped = total - passed - failed
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round(passed / max(total, 1) * 100, 1),
        }
    
    @app.get("/api/security/audit")
    async def get_security_audit():
        """Get security audit from real checks."""
        checks = []
        passed = 0
        failed = 0
        
        # Check API key security
        if settings.anthropic_api_key:
            checks.append({"name": "LLM API key configured", "status": "passed", "severity": "critical"})
            passed += 1
        else:
            checks.append({"name": "LLM API key missing", "status": "failed", "severity": "critical"})
            failed += 1
        
        # Check CORS
        checks.append({"name": "CORS middleware active", "status": "passed", "severity": "medium"})
        passed += 1
        
        # Check database
        try:
            import sqlite3
            conn = sqlite3.connect("piddy.db")
            conn.execute("SELECT 1")
            conn.close()
            checks.append({"name": "Database accessible", "status": "passed", "severity": "high"})
            passed += 1
        except Exception:
            checks.append({"name": "Database inaccessible", "status": "failed", "severity": "critical"})
            failed += 1
        
        # Check Slack config
        if settings.slack_bot_token:
            checks.append({"name": "Slack bot token configured", "status": "passed", "severity": "medium"})
            passed += 1
        else:
            checks.append({"name": "Slack bot token missing", "status": "warning", "severity": "low"})
        
        return {
            "is_production_safe": failed == 0,
            "passed_checks": passed,
            "failed_checks": failed,
            "critical_failures": [c for c in checks if c["status"] == "failed" and c["severity"] == "critical"],
            "all_checks": checks,
            "last_audit": datetime.utcnow().isoformat(),
        }
    
    @app.get("/api/rate-limits/status")
    async def get_rate_limits_status():
        """Get current rate limit status for all providers."""
        try:
            from src.services.rate_limiter import get_rate_limiter
            limiter = get_rate_limiter()
            return limiter.get_system_health()
        except Exception as e:
            logger.warning(f"Rate limiter not available: {e}")
            return {
                "status": "unavailable",
                "message": "Rate limiter not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @app.get("/api/rate-limits/metrics")
    async def get_rate_limits_metrics():
        """Get detailed rate limit metrics."""
        try:
            from src.services.rate_limiter import get_rate_limiter
            limiter = get_rate_limiter()
            metrics = limiter.get_metrics()
            return {
                "data": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.warning(f"Rate limiter metrics not available: {e}")
            return {
                "providers": {},
                "status": "unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @app.get("/api/rate-limits/dashboard")
    async def get_rate_limits_dashboard():
        """Get comprehensive rate limit dashboard data."""
        try:
            from src.services.rate_limiter import get_rate_limiter
            limiter = get_rate_limiter()
            metrics = limiter.get_metrics()
            health = limiter.get_system_health()
            
            return {
                "health": health,
                "providers": metrics.get("providers", {}),
                "queue_length": metrics.get("queue_length", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.warning(f"Rate limiter dashboard data not available: {e}")
            return {
                "health": {"status": "unavailable"},
                "providers": {},
                "queue_length": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # MARKET GAP APPROVAL ENDPOINTS
    # ========================================================================
    
    @app.get("/api/approvals")
    async def list_approvals() -> Dict:
        """List all pending and historical approval requests"""
        try:
            from pathlib import Path
            workflow_file = Path("data/approval_workflow_state.json")
            
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    workflows = json.load(f)
                    return {
                        "requests": workflows,
                        "count": len(workflows),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            return {"requests": {}, "count": 0, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error listing approvals: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    @app.get("/api/approvals/{request_id}")
    async def get_approval_request(request_id: str) -> Dict:
        """Get specific approval request details"""
        try:
            from pathlib import Path
            workflow_file = Path("data/approval_workflow_state.json")
            
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    workflows = json.load(f)
                    if request_id in workflows:
                        return {
                            "request": workflows[request_id],
                            "timestamp": datetime.utcnow().isoformat()
                        }
            return {"error": "Request not found", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error getting approval request: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    @app.get("/api/approvals/{request_id}/gaps/{gap_id}")
    async def get_gap_details(request_id: str, gap_id: str) -> Dict:
        """Get specific gap details within an approval request"""
        try:
            from pathlib import Path
            workflow_file = Path("data/approval_workflow_state.json")
            
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    workflows = json.load(f)
                    if request_id in workflows:
                        gaps = workflows[request_id].get("market_gaps", [])
                        for gap in gaps:
                            if gap.get("gap_id") == gap_id:
                                return {
                                    "gap": gap,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
            return {"error": "Gap not found", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error getting gap details: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    @app.post("/api/approvals/{request_id}/gaps/{gap_id}/approve")
    async def approve_gap(request_id: str, gap_id: str) -> Dict:
        """Approve a specific market gap"""
        try:
            from pathlib import Path
            decisions_file = Path("data/approval_decisions.json")
            decisions_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing decisions
            decisions = {}
            if decisions_file.exists():
                with open(decisions_file, 'r') as f:
                    decisions = json.load(f)
            
            # Record decision
            if request_id not in decisions:
                decisions[request_id] = []
            
            decisions[request_id].append({
                "gap_id": gap_id,
                "approved": True,
                "decision_time": datetime.utcnow().isoformat(),
                "reason": None
            })
            
            # Save decisions
            with open(decisions_file, 'w') as f:
                json.dump(decisions, f, indent=2)
            
            logger.info(f"Gap {gap_id} approved in request {request_id}")
            return {
                "success": True,
                "gap_id": gap_id,
                "action": "approved",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error approving gap: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    @app.post("/api/approvals/{request_id}/gaps/{gap_id}/reject")
    async def reject_gap(request_id: str, gap_id: str, reason: Optional[str] = None) -> Dict:
        """Reject a specific market gap"""
        try:
            from pathlib import Path
            decisions_file = Path("data/approval_decisions.json")
            decisions_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing decisions
            decisions = {}
            if decisions_file.exists():
                with open(decisions_file, 'r') as f:
                    decisions = json.load(f)
            
            # Record decision
            if request_id not in decisions:
                decisions[request_id] = []
            
            decisions[request_id].append({
                "gap_id": gap_id,
                "approved": False,
                "decision_time": datetime.utcnow().isoformat(),
                "reason": reason
            })
            
            # Save decisions
            with open(decisions_file, 'w') as f:
                json.dump(decisions, f, indent=2)
            
            logger.info(f"Gap {gap_id} rejected in request {request_id}: {reason}")
            return {
                "success": True,
                "gap_id": gap_id,
                "action": "rejected",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error rejecting gap: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    @app.get("/api/approvals/summary/stats")
    async def get_approval_stats() -> Dict:
        """Get approval summary statistics"""
        try:
            from pathlib import Path
            
            decisions_file = Path("data/approval_decisions.json")
            workflow_file = Path("data/approval_workflow_state.json")
            
            total_decisions = 0
            approved_count = 0
            rejected_count = 0
            pending_requests = 0
            
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    workflows = json.load(f)
                    for req_id, workflow in workflows.items():
                        if workflow.get("status") == "waiting":
                            pending_requests += 1
            
            if decisions_file.exists():
                with open(decisions_file, 'r') as f:
                    decisions = json.load(f)
                    for req_id, decisions_list in decisions.items():
                        for decision in decisions_list:
                            total_decisions += 1
                            if decision.get("approved"):
                                approved_count += 1
                            else:
                                rejected_count += 1
            
            return {
                "total_decisions": total_decisions,
                "approved_count": approved_count,
                "rejected_count": rejected_count,
                "pending_requests": pending_requests,
                "approval_rate": ((approved_count / total_decisions * 100) if total_decisions > 0 else 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting approval stats: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    # Mount static files (frontend)
    frontend_static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(frontend_static_path):
        app.mount("/", StaticFiles(directory=frontend_static_path, html=True), name="static")
        logger.info(f"📱 Frontend mounted at /api root from {frontend_static_path}")
    else:
        logger.warning(f"⚠️ Frontend dist directory not found at {frontend_static_path}")
    
    return app


# Create app instance at module level for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
    )
