"""Database configuration and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.models.user import Base
import logging

logger = logging.getLogger(__name__)

# Database URL - use SQLite for now
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./piddy.db")

# Create engine with appropriate pool settings for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialization complete")
