"""Utility functions."""

import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()
