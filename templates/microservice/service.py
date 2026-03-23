"""
Microservice Template
=====================
Standalone service with health check, graceful shutdown, and Docker support.

Usage:
    cp -r templates/microservice/ services/my_service/
    # Update SERVICE_NAME, add your logic, build with Docker
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import asyncio

SERVICE_NAME = "my-service"
SERVICE_VERSION = "0.1.0"

logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{SERVICE_NAME} v{SERVICE_VERSION} starting")
    # Startup: initialize connections, load models, etc.
    yield
    # Shutdown: close connections, flush buffers, etc.
    logger.info(f"{SERVICE_NAME} shutting down")


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/ready")
async def ready():
    # Add actual readiness checks (DB connected, model loaded, etc.)
    return {"ready": True}


# --- Add your service routes below ---
