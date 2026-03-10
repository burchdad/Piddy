"""Test cases for agent commands."""

import pytest
import asyncio


class TestAgentCommands:
    """Test agent command endpoints."""
    
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/api/v1/agent/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    async def test_capabilities(self, client):
        """Test capabilities endpoint."""
        response = await client.get("/api/v1/agent/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert len(data["capabilities"]) > 0
    
    async def test_execute_command(self, client, sample_command):
        """Test command execution."""
        response = await client.post(
            "/api/v1/agent/command",
            json=sample_command
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "result" in data
