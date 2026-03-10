"""Tiered self-healing engine: Local → Claude → OpenAI fallback."""

import logging
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class TokenTracker:
    """Track token usage for Claude and OpenAI."""
    
    def __init__(self):
        self.claude_tokens_used = 0
        self.claude_session_limit = 1000000  # 1M tokens per session
        self.openai_tokens_used = 0
        self.openai_session_limit = 500000  # 500K tokens per session
        self.session_start = datetime.now()
        self.last_claude_usage: Optional[datetime] = None
        self.last_openai_usage: Optional[datetime] = None
    
    def add_claude_tokens(self, tokens: int):
        """Record Claude token usage."""
        self.claude_tokens_used += tokens
        self.last_claude_usage = datetime.now()
        logger.info(f"🔵 Claude: +{tokens} tokens (total: {self.claude_tokens_used}/{self.claude_session_limit})")
    
    def add_openai_tokens(self, tokens: int):
        """Record OpenAI token usage."""
        self.openai_tokens_used += tokens
        self.last_openai_usage = datetime.now()
        logger.info(f"🟢 OpenAI: +{tokens} tokens (total: {self.openai_tokens_used}/{self.openai_session_limit})")
    
    def claude_available(self) -> Tuple[bool, str]:
        """Check if Claude has available tokens."""
        remaining = self.claude_session_limit - self.claude_tokens_used
        if self.claude_tokens_used >= self.claude_session_limit:
            return False, f"Claude limit reached: {self.claude_tokens_used}/{self.claude_session_limit}"
        return True, f"Claude available: {remaining} tokens remaining"
    
    def openai_available(self) -> Tuple[bool, str]:
        """Check if OpenAI has available tokens."""
        remaining = self.openai_session_limit - self.openai_tokens_used
        if self.openai_tokens_used >= self.openai_session_limit:
            return False, f"OpenAI limit reached: {self.openai_tokens_used}/{self.openai_session_limit}"
        return True, f"OpenAI available: {remaining} tokens remaining"
    
    def summary(self) -> Dict[str, Any]:
        """Get token usage summary."""
        return {
            "claude": {
                "used": self.claude_tokens_used,
                "limit": self.claude_session_limit,
                "remaining": self.claude_session_limit - self.claude_tokens_used,
                "last_used": self.last_claude_usage.isoformat() if self.last_claude_usage else None
            },
            "openai": {
                "used": self.openai_tokens_used,
                "limit": self.openai_session_limit,
                "remaining": self.openai_session_limit - self.openai_tokens_used,
                "last_used": self.last_openai_usage.isoformat() if self.last_openai_usage else None
            },
            "session_start": self.session_start.isoformat()
        }


# Global token tracker
_token_tracker = TokenTracker()


def get_token_tracker() -> TokenTracker:
    """Get global token tracker."""
    return _token_tracker


async def tier_1_local_healing(code_issues: Optional[Dict] = None) -> Dict[str, Any]:
    """
    TIER 1: Local pattern-based healing (NO external AI).
    
    Returns:
        Dict with fixes or None if it can't handle the issues.
    """
    logger.info("🔧 TIER 1: Attempting local self-healing (pattern-based)...")
    
    try:
        from src.self_healing_engine import run_local_self_healing
        
        results = await run_local_self_healing()
        
        total_fixes = results.get("total_fixes", 0)
        if total_fixes > 0:
            logger.info(f"✅ TIER 1 SUCCESS: Local healing fixed {total_fixes} issues!")
            return {
                "tier": 1,
                "status": "success",
                "engine": "local_self_healing",
                "fixes": total_fixes,
                "details": results
            }
        else:
            logger.info("⚠️ TIER 1: No local patterns matched. Escalating to TIER 2...")
            return {
                "tier": 1,
                "status": "no_matches",
                "message": "Local patterns didn't match issues. Need Claude analysis."
            }
    
    except Exception as e:
        logger.error(f"❌ TIER 1 failed: {e}. Escalating to TIER 2...")
        return {
            "tier": 1,
            "status": "error",
            "error": str(e),
            "message": "Local healing failed. Escalating to Claude."
        }


async def tier_2_claude_healing(code_issues: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    TIER 2: Claude (Anthropic) AI analysis and fixing.
    
    Returns:
        Dict with Claude-generated fixes or None if Claude unavailable.
    """
    logger.info("🔵 TIER 2: Attempting Claude analysis...")
    
    tracker = get_token_tracker()
    claude_available, claude_status = tracker.claude_available()
    
    if not claude_available:
        logger.warning(f"⚠️ Claude unavailable: {claude_status}. Escalating to TIER 3...")
        return {
            "tier": 2,
            "status": "unavailable",
            "reason": claude_status,
            "message": "Claude token limit reached. Escalating to OpenAI."
        }
    
    try:
        from config.settings import get_settings
        from langchain_anthropic import ChatAnthropic
        
        settings = get_settings()
        
        if not settings.anthropic_api_key:
            logger.warning("⚠️ No Claude API key configured. Escalating to TIER 3...")
            return {
                "tier": 2,
                "status": "unavailable",
                "reason": "No API key",
                "message": "Claude not configured. Using OpenAI fallback."
            }
        
        # Initialize Claude
        claude = ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model="claude-opus-4-1-20250805",
            temperature=0.7,
            max_tokens=4096
        )
        
        # Create analysis prompt
        issue_summary = json.dumps(code_issues, indent=2)
        prompt = f"""You are Piddy's internal AI self-healing engine. Analyze these code issues and provide specific fixes:

{issue_summary}

For each issue, provide:
1. Root cause analysis
2. Specific code changes needed
3. File paths to modify
4. Exact replacement code

Format your response as valid JSON."""
        
        # Get Claude's analysis
        logger.info("🤖 Sending to Claude for analysis...")
        response = await asyncio.to_thread(lambda: claude.invoke(prompt))
        
        response_text = response.content
        
        # Extract token estimate (rough approximation)
        estimated_tokens = len(response_text) // 4
        tracker.add_claude_tokens(estimated_tokens)
        
        logger.info(f"✅ TIER 2 SUCCESS: Claude analyzed issues!")
        
        return {
            "tier": 2,
            "status": "success",
            "engine": "claude",
            "model": "claude-opus-4-1-20250805",
            "analysis": response_text,
            "tokens_used": estimated_tokens,
            "token_summary": tracker.summary()
        }
    
    except Exception as e:
        logger.error(f"❌ TIER 2 failed: {e}. Escalating to TIER 3...")
        return {
            "tier": 2,
            "status": "error",
            "error": str(e),
            "message": "Claude analysis failed. Using OpenAI fallback."
        }


async def tier_3_openai_healing(code_issues: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    TIER 3: OpenAI (gpt-4o) as final fallback.
    
    Returns:
        Dict with OpenAI-generated fixes or None if OpenAI unavailable.
    """
    logger.info("🟢 TIER 3: Attempting OpenAI analysis (final fallback)...")
    
    tracker = get_token_tracker()
    openai_available_status, openai_status = tracker.openai_available()
    
    if not openai_available_status:
        logger.error(f"❌ Both Claude and OpenAI unavailable: {openai_status}")
        return {
            "tier": 3,
            "status": "unavailable",
            "reason": openai_status,
            "message": "All AI tiers exhausted. Manual intervention required."
        }
    
    try:
        from config.settings import get_settings
        from langchain_openai import ChatOpenAI
        
        settings = get_settings()
        
        if not settings.openai_api_key:
            logger.error("❌ No OpenAI API key configured. All healing tiers exhausted.")
            return {
                "tier": 3,
                "status": "unavailable",
                "reason": "No API key",
                "message": "OpenAI not configured. All healing tiers exhausted."
            }
        
        # Initialize OpenAI
        openai = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model or "gpt-4o",
            temperature=0.7,
            max_tokens=4096
        )
        
        # Create analysis prompt
        issue_summary = json.dumps(code_issues, indent=2)
        prompt = f"""You are Piddy's final fallback AI self-healing engine. Claude couldn't handle these issues, so you MUST.

Analyze these code issues and provide specific, actionable fixes:

{issue_summary}

For each issue, provide:
1. Root cause analysis
2. Specific code changes needed
3. File paths to modify
4. Exact replacement code

Format your response as valid JSON."""
        
        # Get OpenAI's analysis
        logger.info("🤖 Sending to OpenAI (final fallback)...")
        response = await asyncio.to_thread(lambda: openai.invoke(prompt))
        
        response_text = response.content
        
        # Extract token estimate
        estimated_tokens = len(response_text) // 4
        tracker.add_openai_tokens(estimated_tokens)
        
        logger.info(f"✅ TIER 3 SUCCESS: OpenAI analyzed issues!")
        
        return {
            "tier": 3,
            "status": "success",
            "engine": "openai",
            "model": settings.openai_model or "gpt-4o",
            "analysis": response_text,
            "tokens_used": estimated_tokens,
            "warning": "OpenAI is final fallback - consider optimizing local patterns",
            "token_summary": tracker.summary()
        }
    
    except Exception as e:
        logger.error(f"❌ TIER 3 failed: {e}. All healing tiers exhausted!")
        return {
            "tier": 3,
            "status": "error",
            "error": str(e),
            "message": "All AI healing tiers failed. Manual intervention required."
        }


async def run_tiered_self_healing(
    code_issues: Optional[Dict[str, Any]] = None,
    force_tier: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run tiered self-healing: Local → Claude → OpenAI.
    
    Args:
        code_issues: Optional dict of code issues to analyze
        force_tier: Force use of specific tier (1, 2, or 3) for testing
    
    Returns:
        Dict with healing results and which tier was used
    """
    logger.info("🚀 STARTING TIERED SELF-HEALING SEQUENCE...")
    logger.info("   Tier 1: Local pattern-based healing (no AI)")
    logger.info("   Tier 2: Claude for complex issues (with token tracking)")
    logger.info("   Tier 3: OpenAI as final fallback")
    
    results = {
        "sequence": [],
        "final_result": None,
        "token_summary": get_token_tracker().summary()
    }
    
    try:
        # TIER 1: Local healing
        if not force_tier or force_tier == 1:
            tier_1_result = await tier_1_local_healing(code_issues)
            results["sequence"].append(tier_1_result)
            
            if tier_1_result["status"] == "success":
                logger.info("✅ HEALING COMPLETE at Tier 1 (Local)")
                results["final_result"] = tier_1_result
                results["token_summary"] = get_token_tracker().summary()
                return results
        
        # TIER 2: Claude
        if not force_tier or force_tier == 2:
            tier_2_result = await tier_2_claude_healing(code_issues or {})
            results["sequence"].append(tier_2_result)
            
            if tier_2_result and tier_2_result.get("status") == "success":
                logger.info("✅ HEALING COMPLETE at Tier 2 (Claude)")
                results["final_result"] = tier_2_result
                results["token_summary"] = get_token_tracker().summary()
                return results
        
        # TIER 3: OpenAI
        if not force_tier or force_tier == 3:
            tier_3_result = await tier_3_openai_healing(code_issues or {})
            results["sequence"].append(tier_3_result)
            
            logger.info(f"🏁 HEALING SEQUENCE COMPLETE (Tier {tier_3_result.get('tier', 3)} result)")
            results["final_result"] = tier_3_result
            results["token_summary"] = get_token_tracker().summary()
            return results
        
    except Exception as e:
        logger.error(f"❌ Tiered healing sequence failed: {e}")
        results["error"] = str(e)
        results["token_summary"] = get_token_tracker().summary()
        return results
    
    return results


def get_healing_status() -> Dict[str, Any]:
    """Get current healing system status."""
    tracker = get_token_tracker()
    claude_ok, claude_msg = tracker.claude_available()
    openai_ok, openai_msg = tracker.openai_available()
    
    return {
        "system": "tiered_healing_engine",
        "status": "operational",
        "tiers": {
            "tier_1": {
                "name": "Local Pattern Healing",
                "status": "always_available",
                "cost": "zero"
            },
            "tier_2": {
                "name": "Claude Analysis",
                "status": "available" if claude_ok else "unavailable",
                "message": claude_msg,
                "tokens": tracker.claude_tokens_used
            },
            "tier_3": {
                "name": "OpenAI Fallback",
                "status": "available" if openai_ok else "unavailable",
                "message": openai_msg,
                "tokens": tracker.openai_tokens_used
            }
        },
        "token_usage": tracker.summary()
    }
