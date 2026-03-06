"""Main application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from config.settings import get_settings, setup_logging
from src.api.agent_commands import router as agent_router
from src.api.slack_commands import router as slack_router


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
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Piddy",
            "description": "Backend Developer AI Agent",
            "version": "0.1.0",
            "docs": "/docs",
        }
    
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
