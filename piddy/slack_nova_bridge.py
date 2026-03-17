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
        Execute a Nova command triggered from Slack with FULL integrated pipeline:
        1. Phase 40: Mission Simulation (predict impact)
        2. Phase 50: Multi-Agent Voting (get consensus)
        3. Code Execution (Nova executor)
        4. PR Generation (Phase 37)
        5. Push to GitHub (PR Manager)
        
        Returns: {
            "status": "success" | "failed" | "rejected",
            "mission_id": str,
            "task_id": str,
            "output": str,
            "files_changed": List[str],
            "commits": List[str],
            "pr_url": Optional[str],
            "error": Optional[str],
            "duration_ms": int,
            "stages": Dict,  # Full pipeline stage results
        }
        """
        try:
            mission_id = str(uuid.uuid4())[:8]
            
            logger.info(f"🚀 Nova command from Slack: {text[:50]}... (mission: {mission_id})")
            logger.info(f"   User: {user_id}, Channel: {channel_id}")
            
            # Try to use the integrated pipeline (nova_coordinator) for full safety gates
            try:
                from src.nova_coordinator import get_nova_coordinator
                coordinator = get_nova_coordinator()
                
                logger.info("  Using integrated Nova coordinator (Phase 40 → 50 → Execute → PR → Push)")
                
                # Run the full integrated pipeline
                result = await coordinator.execute_with_consensus(
                    task=text,
                    requester=f"slack:{user_id}" if user_id else "slack:unknown",
                    consensus_type="WEIGHTED"
                )
                
                # Cache execution
                self.execution_cache[mission_id] = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "text": text,
                    "result": result,
                }
                
                # Format result from coordinator
                logger.info(f"✅ Nova coordinator pipeline complete: {result.get('status')}")
                
                if result.get("status") == "success":
                    return {
                        "status": "success",
                        "mission_id": mission_id,
                        "task_id": result.get("mission_id"),
                        "output": "",  # Coordinator doesn't return direct output
                        "files_changed": result.get("stages", {}).get("execution", {}).get("files_changed", []),
                        "commits": result.get("stages", {}).get("execution", {}).get("commits", []),
                        "pr_url": result.get("stages", {}).get("push", {}).get("pr_url"),
                        "duration_ms": result.get("stages", {}).get("execution", {}).get("duration_ms", 0),
                        "error": None,
                        "stages": result.get("stages", {}),
                    }
                elif result.get("status") == "rejected":
                    return {
                        "status": "rejected",
                        "mission_id": mission_id,
                        "task_id": result.get("mission_id"),
                        "error": result.get("reason", "Consensus not reached"),
                        "stages": result.get("stages", {}),
                    }
                else:
                    return {
                        "status": "failed",
                        "mission_id": mission_id,
                        "task_id": result.get("mission_id"),
                        "error": result.get("error", "Unknown error"),
                        "stages": result.get("stages", {}),
                    }
            
            except ImportError:
                # Fallback to simple nova_executor if coordinator not available
                logger.warning("  Coordinator not available, falling back to simple Nova executor")
                
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
                
                logger.info(f"✅ Nova executor complete: {result.get('status')}")
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
        
        Handles both:
        - Simple executor result (status, files, commits)
        - Integrated coordinator result (with stages, approval voting, PR URL)
        
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
        
        if result["status"] == "rejected":
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⛔ Mission rejected\n*Reason:* {result.get('error', 'No consensus reached')}\n*Mission:* `{result.get('mission_id')}`"
                    }
                }
            ]
        
        # Success - build rich result blocks
        blocks = []
        
        # Main status with mission ID
        mission_id = result.get('mission_id', 'unknown')
        duration_ms = result.get('duration_ms', 0)
        
        status_text = f"✅ Nova mission complete\n*Mission:* `{mission_id}`\n*Duration:* {duration_ms}ms"
        
        # If we have stages (coordinator result), show voting results
        stages = result.get("stages", {})
        if stages:
            voting = stages.get("voting", {})
            if voting:
                voted_count = voting.get("total_agents", 0)
                consensus = voting.get("consensus_result", "UNKNOWN")
                status_text += f"\n*Consensus:* {consensus} ({voted_count}/12 agents)"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": status_text
            }
        })
        
        # Show files changed
        files = result.get("files_changed", [])
        if files:
            files_text = "\n".join(f"  • {f}" for f in files[:5])
            if len(files) > 5:
                files_text += f"\n  • ... and {len(files) - 5} more"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Files Changed:* {len(files)}\n{files_text}"
                }
            })
        
        # Show commits
        commits = result.get("commits", [])
        if commits:
            commits_text = "\n".join(f"  • `{c[:8]}`" for c in commits[:3])
            if len(commits) > 3:
                commits_text += f"\n  • ... and {len(commits) - 3} more"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Commits:* {len(commits)}\n{commits_text}"
                }
            })
        
        # Show PR URL (if coordinator was used)
        pr_url = result.get("pr_url")
        if pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*PR Created:*\n<{pr_url}|View Pull Request>"
                }
            })
        
        # Show voting details if available
        if stages and stages.get("voting"):
            voting = stages["voting"]
            votes = voting.get("votes", [])
            if votes:
                # Show first 5 agents who voted
                vote_txt = "🗳️ *Agent Votes:*\n"
                for vote in votes[:5]:
                    agent_name = vote.get("agent", "Unknown")
                    confidence = int(vote.get("confidence", 0) * 100)
                    vote_txt += f"  • {agent_name}: ✅ {confidence}%\n"
                if len(votes) > 5:
                    vote_txt += f"  • ... and {len(votes) - 5} more agents"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": vote_txt
                    }
                })
        
        # Show output snippet (only for simple executor result)
        output = result.get("output")
        if output:
            output_snippet = output[:200]
            if len(output) > 200:
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
