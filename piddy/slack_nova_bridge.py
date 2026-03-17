"""
Slack → Nova Bridge

Enables Slack users to trigger Nova code execution directly.
Supports commands like:
  - "nova create test for validation"
  - "nova generate API endpoint"
  - "nova fix bug in auth module"
  - "nova refactor database queries"
"""

import logging
import asyncio
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Try to import RPC client for calling Nova endpoints
try:
    from piddy.rpc_client import RPCClient
    HAS_RPC_CLIENT = True
except ImportError:
    HAS_RPC_CLIENT = False
    logger.warning("⚠️ RPC client not available - Nova execution disabled")

# Try to import RPC endpoints directly for in-process calls
try:
    from piddy.rpc_endpoints import _get_event_loop
    from piddy.nova_executor import execute_task, get_execution_status, get_all_executions
    HAS_DIRECT_RPC = True
except ImportError:
    HAS_DIRECT_RPC = False


class SlackNovaIntegration:
    """Bridge Slack commands to Nova execution"""
    
    # Nova command patterns
    COMMAND_PATTERNS = {
        "test": [
            r"nova\s+(?:create|write|generate)\s+(?:test|tests?|unit test)",
            r"nova\s+test(?:ing)?",
        ],
        "feature": [
            r"nova\s+(?:create|generate|add)\s+(?:feature|endpoint|api)",
            r"nova\s+add\s+(?:support|functionality)",
        ],
        "bugfix": [
            r"nova\s+(?:fix|debug|repair)\s+(?:bug|issue|error)",
            r"nova\s+fix(?:ing)?",
        ],
        "refactor": [
            r"nova\s+(?:refactor|clean|optimize|rewrite)",
            r"nova\s+(?:cleanup|reorg|reorganize)",
        ],
        "docs": [
            r"nova\s+(?:document|doc|write\s+docs?|create\s+docs?)",
            r"nova\s+documentation",
        ],
    }
    
    def __init__(self):
        """Initialize Slack → Nova bridge"""
        self.rpc_client = None
        if HAS_RPC_CLIENT:
            self.rpc_client = RPCClient()
        self.execution_cache = {}  # Track recent executions for status queries
    
    def detect_nova_command(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect if message contains a Nova command
        
        Returns: (is_nova_command, command_type, full_task_description)
        """
        text_lower = text.lower().strip()
        
        # Check if starts with "nova"
        if not text_lower.startswith("nova"):
            return False, None, None
        
        # Detect command type
        for cmd_type, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return True, cmd_type, text
        
        # Fallback: if starts with "nova" but no specific pattern, it's a general task
        return True, "general", text
    
    async def execute_nova_command(
        self,
        text: str,
        agent: str = "nova",
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Nova command triggered from Slack
        
        Returns: {
            "status": "success" | "failed",
            "mission_id": str,
            "task_id": str,
            "output": str,
            "files_changed": List[str],
            "commits": List[str],
            "error": Optional[str],
            "duration_ms": int,
        }
        """
        try:
            mission_id = str(uuid.uuid4())[:8]
            
            logger.info(f"🚀 Nova command from Slack: {text[:50]}... (mission: {mission_id})")
            
            # Call Nova executor
            result = None
            if HAS_DIRECT_RPC:
                # Direct in-process call (faster)
                logger.info("  Using direct in-process Nova execution")
                result = execute_task(mission_id, agent, text)
            elif self.rpc_client:
                # RPC client call (for remote/distributed setup)
                logger.info("  Using RPC client for Nova execution")
                result = await self.rpc_client.call("nova.execute_task", mission_id, agent, text)
            else:
                return {
                    "status": "failed",
                    "error": "Nova execution not available",
                    "mission_id": mission_id,
                }
            
            # Cache execution
            self.execution_cache[mission_id] = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "channel_id": channel_id,
                "text": text,
                "result": result,
            }
            
            logger.info(f"✅ Nova execution complete: {result.get('status')}")
            return {
                "status": "success",
                "mission_id": mission_id,
                "task_id": result.get("task_id") or result.get("mission_id"),
                "output": result.get("output", ""),
                "files_changed": result.get("files_changed", []),
                "commits": result.get("commits", []),
                "duration_ms": result.get("duration_ms", 0),
                "error": result.get("error"),
            }
        
        except Exception as e:
            logger.error(f"❌ Nova execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "mission_id": mission_id,
            }
    
    def format_nova_result_for_slack(self, result: Dict[str, Any]) -> List[Dict]:
        """
        Format Nova execution result as Slack blocks
        
        Returns: List of Slack block dicts
        """
        if result["status"] == "failed":
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ Nova execution failed\n`{result.get('error', 'Unknown error')}`"
                    }
                }
            ]
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ Nova execution complete\n*Mission:* `{result['mission_id']}`\n*Duration:* {result.get('duration_ms', 0)}ms"
                }
            }
        ]
        
        # Show files changed
        if result.get("files_changed"):
            files_text = "\n".join(f"  • {f}" for f in result["files_changed"][:5])
            if len(result["files_changed"]) > 5:
                files_text += f"\n  • ... and {len(result['files_changed']) - 5} more"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Files Changed:*\n{files_text}"
                }
            })
        
        # Show commits
        if result.get("commits"):
            commits_text = "\n".join(f"  • `{c[:8]}`" for c in result["commits"][:3])
            if len(result["commits"]) > 3:
                commits_text += f"\n  • ... and {len(result['commits']) - 3} more"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Commits:*\n{commits_text}"
                }
            })
        
        # Show output snippet
        if result.get("output"):
            output_snippet = result["output"][:200]
            if len(result["output"]) > 200:
                output_snippet += "\n... (truncated)"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Output:*\n```{output_snippet}```"
                }
            })
        
        return blocks
    
    async def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get status of a Nova mission"""
        try:
            if mission_id in self.execution_cache:
                cached = self.execution_cache[mission_id]
                return {
                    "found": True,
                    "mission_id": mission_id,
                    "timestamp": cached["timestamp"],
                    "result": cached["result"],
                }
            
            # Try to get from database via RPC
            if HAS_DIRECT_RPC:
                result = get_execution_status(mission_id)
                return {
                    "found": result is not None,
                    "mission_id": mission_id,
                    "result": result,
                }
            
            return {
                "found": False,
                "mission_id": mission_id,
                "error": "Mission not found"
            }
        
        except Exception as e:
            logger.error(f"Failed to get mission status: {e}")
            return {
                "found": False,
                "mission_id": mission_id,
                "error": str(e)
            }
    
    async def list_recent_missions(self, limit: int = 5) -> List[Dict]:
        """List recent Nova missions"""
        try:
            if HAS_DIRECT_RPC:
                all_executions = get_all_executions()
                return all_executions[:limit]
            
            return []
        except Exception as e:
            logger.error(f"Failed to list missions: {e}")
            return []


# Global instance
_nova_bridge = None

def get_slack_nova_integration() -> SlackNovaIntegration:
    """Get or create Slack → Nova bridge"""
    global _nova_bridge
    if _nova_bridge is None:
        _nova_bridge = SlackNovaIntegration()
    return _nova_bridge
