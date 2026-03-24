from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Annotated
import httpx
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql+asyncpg://user:pass@db/app"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class User(BaseModel):
    id: int
    email: str

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def get_current_user(authorization: Annotated[str, Header(...)], db: AsyncSession = Depends(get_db)) -> User:
    token = authorization.removeprefix("Bearer ")
    # Simulate decoding and querying the database for user
    return User(id=1, email="user@example.com")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.3f}s)")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/api/v1/resources", status_code=201)
async def create_resource(db: AsyncSession = Depends(get_db)):
    # Simulate creating a resource
    return {"id": 1, "name": "Resource 1", "description": "This is a test resource"}

@app.get("/api/v1/resources/me")
async def get_profile(user: User = Depends(get_current_user)):
    return user

@app.get("/health")
async def health_check():
    return {"status": "ok"}
