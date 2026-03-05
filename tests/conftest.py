"""Test configuration and fixtures."""

import pytest
from httpx import AsyncClient
from src.main import create_app


@pytest.fixture
async def app():
    """Create test app."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def sample_command():
    """Sample command for testing."""
    return {
        "command_type": "code_generation",
        "description": "Generate a simple Python function",
        "context": {"language": "python"},
        "priority": 5,
    }
