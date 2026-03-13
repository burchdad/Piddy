"""Audit logging database model."""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuditLogDB(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), default="success", nullable=False)  # success, failure, denied
    signature = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, timestamp={self.timestamp})>"
