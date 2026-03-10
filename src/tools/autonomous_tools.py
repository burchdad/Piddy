"""Tools for Piddy to control its own autonomous monitoring system."""

import logging
import httpx
from typing import Dict, Any, Optional
import asyncio


logger = logging.getLogger(__name__)


async def autonomous_monitor_start(interval_seconds: int = 3600) -> Dict[str, Any]:
    """
    Start autonomous code monitoring.
    
    Args:
        interval_seconds: Monitoring interval in seconds (default 1 hour)
        
    Returns:
        Status of monitoring start
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "get_config().localhost:8000",
                params={"interval_seconds": interval_seconds}
            )
            result = response.json()
            logger.info(f"✅ Autonomous monitoring started: {result}")
            return {
                "success": True,
                "message": f"🤖 Autonomous monitoring enabled. I'll analyze the codebase every {interval_seconds}s ({interval_seconds//60} minutes) and create PRs for issues.",
                "details": result
            }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return {
            "success": False,
            "message": f"❌ Failed to start monitoring: {str(e)}",
            "error": str(e)
        }


async def autonomous_monitor_stop() -> Dict[str, Any]:
    """Stop autonomous monitoring."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "get_config().localhost:8000"
            )
            result = response.json()
            logger.info("✅ Autonomous monitoring stopped")
            return {
                "success": True,
                "message": "🛑 Autonomous monitoring stopped.",
                "details": result
            }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return {
            "success": False,
            "message": f"❌ Failed to stop monitoring: {str(e)}",
            "error": str(e)
        }


async def autonomous_monitor_status() -> Dict[str, Any]:
    """Get current monitoring status."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "get_config().localhost:8000"
            )
            result = response.json()
            
            status = result.get("monitor", {})
            summary = result.get("summary", {})
            
            # Format response
            message = f"""📊 **Autonomous Monitoring Status**

**Monitor**: {'🟢 ENABLED' if status.get('enabled') else '🔴 DISABLED'}
**Issues Detected**: {summary.get('total_issues', 0)}
**Issues Fixed**: {status.get('issues_fixed', 0)}
**PRs Created**: {summary.get('created_prs', 0)}

**Issues by Severity**:
- 🔴 Critical: {summary.get('by_severity', {}).get('critical', 0)}
- 🟠 High: {summary.get('by_severity', {}).get('high', 0)}
- 🟡 Medium: {summary.get('by_severity', {}).get('medium', 0)}
- 🟢 Low: {summary.get('by_severity', {}).get('low', 0)}

**Issues by Type**:
"""
            for issue_type, count in summary.get('by_type', {}).items():
                message += f"- {issue_type.replace('_', ' ').title()}: {count}\n"
            
            message += f"\n**GitHub Configured**: {'✅ Yes' if result.get('pr_manager', {}).get('github_configured') else '❌ No'}"
            
            return {
                "success": True,
                "message": message,
                "details": result
            }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "success": False,
            "message": f"❌ Failed to get status: {str(e)}",
            "error": str(e)
        }


async def autonomous_analyze_now() -> Dict[str, Any]:
    """Run code analysis immediately."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "get_config().localhost:8000",
                timeout=30.0
            )
            result = response.json()
            
            issues_found = result.get('issues_found', 0)
            summary = result.get('summary', {})
            latest = result.get('latest_issues', [])
            
            message = f"""🔍 **Code Analysis Results**

**Total Issues Found**: {issues_found}

**By Severity**:
"""
            for severity, count in summary.get('by_severity', {}).items():
                message += f"- {severity.upper()}: {count}\n"
            
            message += f"\n**By Type**:\n"
            for issue_type, count in summary.get('by_type', {}).items():
                message += f"- {issue_type.replace('_', ' ').title()}: {count}\n"
            
            if latest:
                message += f"\n**Latest Issues**:\n"
                for issue in latest[:5]:
                    message += f"- **{issue.get('type', 'unknown').replace('_', ' ').title()}** ({issue.get('severity', '').upper()})\n"
                    message += f"  File: `{issue.get('file')}:{issue.get('line')}`\n"
                    message += f"  {issue.get('description')}\n"
            
            return {
                "success": True,
                "message": message,
                "details": result
            }
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return {
            "success": False,
            "message": f"❌ Analysis failed: {str(e)}",
            "error": str(e)
        }


async def autonomous_get_prs() -> Dict[str, Any]:
    """Get list of PRs created by autonomous system."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "get_config().localhost:8000"
            )
            result = response.json()
            
            prs = result.get('prs', [])
            total = result.get('total_prs', 0)
            
            if total == 0:
                message = "📝 No PRs created yet by autonomous system."
            else:
                message = f"📝 **Created PRs**: {total}\n\n"
                for pr in prs:
                    message += f"- [{pr.get('title')}]({pr.get('pr_url')})\n"
            
            return {
                "success": True,
                "message": message,
                "details": result
            }
    except Exception as e:
        logger.error(f"Error getting PRs: {e}")
        return {
            "success": False,
            "message": f"❌ Failed to get PRs: {str(e)}",
            "error": str(e)
        }
