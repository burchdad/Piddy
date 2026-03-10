"""API endpoints for agent command interface."""

from fastapi import APIRouter, HTTPException
from typing import List

from src.models.command import Command, CommandResponse, CommandType
from src.agent.core import BackendDeveloperAgent
import logging
import asyncio


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agent", tags=["agent"])
agent = BackendDeveloperAgent()


@router.post("/command", response_model=CommandResponse)
async def execute_command(command: Command) -> CommandResponse:
    """
    Execute a backend development command.
    
    This is the main interface for other AI agents to communicate with Piddy.
    """
    response = await agent.process_command(command)
    return response


@router.get("/health")
async def health_check():
    """Check agent health status."""
    return await agent.health_check()


@router.get("/capabilities")
async def get_capabilities():
    """Get list of agent capabilities."""
    return {
        "agent": "Piddy",
        "version": "0.1.0",
        "capabilities": [ct.value for ct in CommandType],
        "tools_available": len(agent.tools),
    }


@router.post("/command/batch", response_model=List[CommandResponse])
async def execute_batch_commands(commands: List[Command]) -> List[CommandResponse]:
    """
    Execute multiple commands in sequence.
    
    Args:
        commands: List of commands to execute
        
    Returns:
        List of responses for each command
    """
    responses = []
    for command in commands:
        response = await agent.process_command(command)
        responses.append(response)
    return responses
