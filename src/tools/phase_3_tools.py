"""
Phase 3 tools: Multi-language analysis, performance caching, security, monitoring, and self-improvement.
"""

import json
import logging
from typing import Dict, Any

from src.utils.language_support import MultiLanguageAnalyzer, Language
from src.utils.cache_manager import get_analysis_cache, get_cache_manager
from src.utils.security_hardening import (
    get_rate_limiter, get_audit_logger, SecurityPolicy
)
from src.utils.monitoring import (
    get_metrics_collector, get_performance_monitor, get_health_check
)
from src.utils.self_improvement import (
    get_pattern_learner, get_code_evolution_tracker, get_failure_analyzer,
    GeneratedCode
)

logger = logging.getLogger(__name__)


def analyze_code_multilingual(code: str, language: str = "auto") -> Dict[str, Any]:
    """Analyze code across multiple programming languages."""
    try:
        # Validate code security
        is_safe, error = SecurityPolicy.validate_code(code)
        if not error:
            is_safe, error = SecurityPolicy.validate_input(code)
        
        if not is_safe:
            return {
                "success": False,
                "error": f"Code security check failed: {error}",
                "severity": "CRITICAL"
            }
        
        # Check rate limiting
        user_id = "system"  # In real use, pass from context
        allowed, limit_info = get_rate_limiter().is_allowed(user_id)
        if not allowed:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "limit_info": limit_info
            }
        
        # Auto-detect language if not specified
        if language == "auto":
            analyzer = MultiLanguageAnalyzer()
            language_enum = analyzer.switcher.detect_language(code)
        else:
            try:
                language_enum = Language[language.upper()]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}. Supported: {[l.value for l in Language]}"
                }
        
        # Check cache
        cache = get_analysis_cache()
        cached = cache.get_analysis(code, language_enum.value)
        if cached:
            logger.debug(f"Cache hit for {language_enum.value} analysis")
            return {"success": True, "cached": True, **cached}
        
        # Start metrics
        collector = get_metrics_collector()
        timer = collector.start_timer("analyze_code_multilingual")
        
        # Perform analysis
        analyzer = MultiLanguageAnalyzer()
        result = analyzer.analyze(code, language_enum)
        
        # Stop timer and record
        elapsed = collector.stop_timer(timer, {"language": language_enum.value})
        collector.increment_counter("tool_analysis_count", tags={"language": language_enum.value})
        
        # Cache result
        cache.set_analysis(code, language_enum.value, result)
        
        # Log audit event
        audit = get_audit_logger()
        audit.log_command(
            user_id="system",
            channel_id="system",
            command="analyze_code_multilingual",
            details={
                "language": language_enum.value,
                "lines": len(code.split('\n')),
                "duration_ms": elapsed * 1000,
            }
        )
        
        return {
            "success": True,
            "language": result["language"],
            "quality_score": result["quality_score"],
            "total_issues": result["total_issues"],
            "security_issues": result["security_issues"][:5],  # Top 5
            "performance_issues": result["performance_issues"][:5],
            "recommendations": result["recommendations"],
            "duration_ms": elapsed * 1000,
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_code_multilingual: {e}")
        get_failure_analyzer().record_failure(
            "analyze_code_multilingual",
            language,
            str(e),
            {"code_length": len(code)}
        )
        return {"success": False, "error": str(e)}


def generate_boilerplate_code(language: str, project_type: str = "api") -> Dict[str, Any]:
    """Generate boilerplate code for different languages and project types."""
    try:
        try:
            language_enum = Language[language.upper()]
        except KeyError:
            return {
                "success": False,
                "error": f"Unsupported language: {language}"
            }
        
        analyzer = MultiLanguageAnalyzer()
        boilerplate = analyzer.generate_boilerplate(language_enum, project_type)
        
        # Record in code evolution tracker
        code_obj = GeneratedCode(
            code=boilerplate,
            language=language,
            tool_used="generate_boilerplate_code",
            quality_score=0.85
        )
        get_code_evolution_tracker().record_generation(code_obj)
        
        # Record pattern
        get_pattern_learner().record_pattern(
            f"boilerplate_{project_type}",
            language,
            {"framework_used": "standard"},
            success=True
        )
        
        return {
            "success": True,
            "language": language,
            "project_type": project_type,
            "boilerplate": boilerplate,
        }
    
    except Exception as e:
        logger.error(f"Error in generate_boilerplate_code: {e}")
        return {"success": False, "error": str(e)}


def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics."""
    try:
        cache = get_cache_manager()
        stats = cache.get_stats()
        
        return {
            "success": True,
            "cache_stats": stats,
        }
    
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"success": False, "error": str(e)}


def clear_cache(cache_type: str = "all") -> Dict[str, Any]:
    """Clear cache to free up memory."""
    try:
        cache = get_cache_manager()
        
        if cache_type == "all" or cache_type == "memory":
            cache.clear()
        
        return {
            "success": True,
            "message": f"Cleared {cache_type} cache",
        }
    
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"success": False, "error": str(e)}


def check_rate_limit(user_id: str) -> Dict[str, Any]:
    """Check rate limit status for a user."""
    try:
        limiter = get_rate_limiter()
        allowed, info = limiter.is_allowed(user_id)
        stats = limiter.get_user_stats(user_id)
        
        return {
            "success": True,
            "allowed": allowed,
            "remaining": info if allowed else None,
            "limit_info": info if not allowed else None,
            "stats": stats,
        }
    
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return {"success": False, "error": str(e)}


def get_audit_log(user_id: str, limit: int = 50) -> Dict[str, Any]:
    """Get audit log for a specific user."""
    try:
        audit = get_audit_logger()
        events = audit.get_events_for_user(user_id, limit)
        
        return {
            "success": True,
            "user_id": user_id,
            "events_count": len(events),
            "events": events,
        }
    
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        return {"success": False, "error": str(e)}


def get_security_incidents(hours: int = 24) -> Dict[str, Any]:
    """Get recent security incidents."""
    try:
        audit = get_audit_logger()
        incidents = audit.get_security_incidents(hours)
        
        return {
            "success": True,
            "hours": hours,
            "incident_count": len(incidents),
            "incidents": incidents,
        }
    
    except Exception as e:
        logger.error(f"Error getting security incidents: {e}")
        return {"success": False, "error": str(e)}


def get_system_health() -> Dict[str, Any]:
    """Get system health status."""
    try:
        collector = get_metrics_collector()
        health = get_health_check()
        
        health_status = health.check_health(collector)
        
        return {
            "success": True,
            "health": health_status,
        }
    
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {"success": False, "error": str(e)}


def get_metrics_summary(minutes: int = 60) -> Dict[str, Any]:
    """Get metrics summary for monitoring."""
    try:
        collector = get_metrics_collector()
        summary = collector.get_summary(minutes)
        
        return {
            "success": True,
            "period_minutes": minutes,
            "metrics": summary,
        }
    
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {"success": False, "error": str(e)}


def get_learning_recommendations(language: str) -> Dict[str, Any]:
    """Get AI recommendations based on learned patterns."""
    try:
        learner = get_pattern_learner()
        recommendations = learner.get_recommendations(language)
        
        successful_patterns = learner.get_successful_patterns(language)
        
        return {
            "success": True,
            "language": language,
            "recommendations": recommendations,
            "successful_patterns": successful_patterns,
        }
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return {"success": False, "error": str(e)}


def get_code_quality_trend(language: str) -> Dict[str, Any]:
    """Get code quality trend analysis."""
    try:
        tracker = get_code_evolution_tracker()
        trend = tracker.get_quality_trend(language)
        
        return {
            "success": True,
            "trend": trend,
        }
    
    except Exception as e:
        logger.error(f"Error getting quality trend: {e}")
        return {"success": False, "error": str(e)}


def get_failure_analysis(hours: int = 24) -> Dict[str, Any]:
    """Analyze recent failures for improvement."""
    try:
        analyzer = get_failure_analyzer()
        failures = analyzer.get_frequent_failures(hours)
        
        return {
            "success": True,
            "hours": hours,
            "failure_count": len(failures),
            "frequent_failures": failures,
        }
    
    except Exception as e:
        logger.error(f"Error analyzing failures: {e}")
        return {"success": False, "error": str(e)}
