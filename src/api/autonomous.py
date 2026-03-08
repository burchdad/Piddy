"""API endpoints for autonomous monitoring and PR management."""

from fastapi import APIRouter, HTTPException
from src.services.autonomous_monitor import get_autonomous_monitor
from src.services.pr_manager import get_pr_manager
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/autonomous", tags=["autonomous"])


@router.get("/monitor/status")
async def get_monitor_status():
    """
    Get status of autonomous monitoring system.
    
    Returns:
        Current monitoring status and issue summary
    """
    monitor = get_autonomous_monitor()
    return {
        "monitoring_enabled": monitor.monitoring_enabled,
        "summary": monitor.get_issue_summary(),
        "issues": [
            {
                "type": issue.issue_type,
                "severity": issue.severity,
                "file": issue.file_path,
                "line": issue.line_number,
                "description": issue.description
            }
            for issue in monitor.issues[:20]  # Last 20 issues
        ]
    }


@router.post("/monitor/start")
async def start_monitoring(interval_seconds: int = 3600):
    """
    Start autonomous monitoring loop.
    
    Args:
        interval_seconds: Check interval in seconds
        
    Returns:
        Status confirmation
    """
    import asyncio
    monitor = get_autonomous_monitor()
    
    if monitor.monitoring_enabled:
        return {"status": "already_running"}
    
    monitor.monitoring_enabled = True
    
    # Run in background
    asyncio.create_task(monitor.run_monitoring_loop(interval_seconds))
    
    return {"status": "monitoring_started", "interval_seconds": interval_seconds}


@router.post("/monitor/stop")
async def stop_monitoring():
    """Stop autonomous monitoring."""
    monitor = get_autonomous_monitor()
    monitor.monitoring_enabled = False
    return {"status": "monitoring_stopped"}


@router.get("/monitor/analyze-now")
async def analyze_now():
    """Run analysis immediately."""
    import asyncio
    monitor = get_autonomous_monitor()
    
    issues = await monitor.analyze_codebase()
    return {
        "issues_found": len(issues),
        "summary": monitor.get_issue_summary(),
        "latest_issues": [
            {
                "type": issue.issue_type,
                "severity": issue.severity,
                "file": issue.file_path,
                "line": issue.line_number,
                "description": issue.description
            }
            for issue in issues[:10]
        ]
    }


@router.get("/prs/created")
async def get_created_prs():
    """Get list of PRs created by autonomous system."""
    monitor = get_autonomous_monitor()
    return {
        "total_prs": len(monitor.created_prs),
        "prs": monitor.created_prs
    }


@router.post("/pr/create")
async def create_manual_pr(
    title: str,
    description: str,
    branch_name: str
):
    """
    Manually create a PR (for testing).
    
    Args:
        title: PR title
        description: PR description
        branch_name: Feature branch name
        
    Returns:
        PR creation result
    """
    pr_manager = get_pr_manager()
    result = pr_manager.create_pr(
        title=title,
        description=description,
        branch_name=branch_name
    )
    
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="Failed to create PR")


@router.get("/status")
async def get_autonomous_status():
    """Get overall autonomous system status."""
    monitor = get_autonomous_monitor()
    pr_manager = get_pr_manager()
    
    return {
        "monitor": {
            "enabled": monitor.monitoring_enabled,
            "issues_detected": len(monitor.issues),
            "issues_fixed": len(monitor.fixed_issues)
        },
        "pr_manager": {
            "prs_created": len(monitor.created_prs),
            "github_configured": bool(pr_manager.github_token)
        },
        "summary": monitor.get_issue_summary()
    }
