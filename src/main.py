"""Main application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging
import os

from config.settings import get_settings, setup_logging
from src.api.agent_commands import router as agent_router
from src.api.slack_commands import router as slack_router
from src.api.responses import router as responses_router
from src.api.autonomous import router as autonomous_router


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
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(agent_router)
    app.include_router(slack_router)
    app.include_router(responses_router)
    app.include_router(autonomous_router)
    
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        logger.info("Piddy starting up...")
        logger.info(f"Model: {settings.agent_model}")
        logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
        
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
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        from src.service.health_check import check_health
        health_status = check_health()
        return {
            "status": health_status.status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": health_status.checks,
        }
    
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health check with metrics."""
        from src.service.health_check import get_status
        return get_status()
    
    @app.get("/status")
    async def status():
        """Service status endpoint."""
        from src.service.health_check import get_monitor
        monitor = get_monitor()
        status_dict = monitor.get_status_dict()
        return status_dict
    
    # Dashboard API Endpoints
    @app.get("/api/system/overview")
    async def system_overview():
        """Get system overview for dashboard."""
        return {
            "status": "operational",
            "uptime_seconds": 3600,
            "agents_online": 12,
            "missions_active": 2,
            "decisions_pending": 3,
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    @app.get("/api/agents")
    async def get_agents():
        """Get all agents."""
        return {
            "agents": [
                {"id": "agent-1", "name": "Guardian", "status": "online", "reputation": 0.95},
                {"id": "agent-2", "name": "Validator", "status": "online", "reputation": 0.87},
                {"id": "agent-3", "name": "Performance Analyst", "status": "online", "reputation": 0.82},
                {"id": "agent-4", "name": "Tech Debt Hunter", "status": "idle", "reputation": 0.79},
                {"id": "agent-5", "name": "Architecture Reviewer", "status": "online", "reputation": 0.88},
                {"id": "agent-6", "name": "Cost Optimizer", "status": "online", "reputation": 0.84},
            ],
            "total": 12,
        }
    
    @app.get("/api/messages")
    async def get_messages():
        """Get recent messages."""
        return {
            "messages": [
                {"timestamp": datetime.utcnow().isoformat(), "agent": "Guardian", "text": "Security check passed", "level": "info"},
                {"timestamp": datetime.utcnow().isoformat(), "agent": "Validator", "text": "Code quality score: 92", "level": "info"},
            ],
            "total": 2,
        }
    
    @app.get("/api/decisions")
    async def get_decisions():
        """Get recent decisions."""
        return {
            "decisions": [
                {"id": "dec-1", "agent": "Guardian", "confidence": 0.98, "status": "approved"},
                {"id": "dec-2", "agent": "Validator", "confidence": 0.85, "status": "approved"},
            ],
            "total": 2,
        }
    
    @app.get("/api/missions")
    async def get_missions():
        """Get active missions."""
        return {
            "missions": [
                {"id": "mission-1", "name": "Deploy Service", "progress": 75, "status": "in_progress"},
                {"id": "mission-2", "name": "Code Review", "progress": 100, "status": "completed"},
            ],
            "total": 2,
        }
    
    @app.get("/api/graph/dependencies")
    async def get_dependencies():
        """Get dependency graph."""
        return {
            "nodes": [
                {"id": "svc-1", "label": "API Gateway", "type": "service"},
                {"id": "svc-2", "label": "Auth Service", "type": "service"},
                {"id": "svc-3", "label": "DB", "type": "external"},
            ],
            "edges": [
                {"source": "svc-1", "target": "svc-2"},
                {"source": "svc-2", "target": "svc-3"},
            ],
        }
    
    @app.get("/api/missions/{mission_id}/replay")
    async def get_mission_replay(mission_id: str):
        """Get mission replay data."""
        return {
            "mission_id": mission_id,
            "steps": [
                {"step": 1, "action": "agent_action", "description": "Analyzing code", "timestamp": datetime.utcnow().isoformat()},
                {"step": 2, "action": "decision", "description": "Approved", "timestamp": datetime.utcnow().isoformat()},
            ],
            "total_steps": 2,
        }
    
    @app.get("/api/metrics/performance")
    async def get_metrics():
        """Get performance metrics."""
        return {
            "cpu_usage": 45.2,
            "memory_usage": 62.1,
            "response_time": 124,
            "requests_per_second": 234,
        }
    
    @app.get("/api/logs")
    async def get_logs():
        """Get recent logs."""
        return {
            "logs": [
                {"timestamp": datetime.utcnow().isoformat(), "level": "info", "message": "System operational"},
                {"timestamp": datetime.utcnow().isoformat(), "level": "info", "message": "Agent online"},
            ],
            "total": 2,
        }
    
    @app.get("/api/phases")
    async def get_phases():
        """Get phase information."""
        return {
            "current_phase": 5,
            "phases": [
                {"id": 1, "name": "Core Agent", "status": "completed"},
                {"id": 5, "name": "Dashboard", "status": "in_progress"},
            ],
        }
    
    # Mount static files (frontend)
    frontend_static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(frontend_static_path):
        app.mount("/", StaticFiles(directory=frontend_static_path, html=True), name="static")
        logger.info(f"📱 Frontend mounted at /api root from {frontend_static_path}")
    else:
        logger.warning(f"⚠️ Frontend dist directory not found at {frontend_static_path}")
    
    return app


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
