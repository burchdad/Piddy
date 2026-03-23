#!/usr/bin/env python3
"""
Test script to verify dashboard setup and all components
"""
import os
import json
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def check_component_file(filepath):
    """Check if a React component file exists and has valid content"""
    if not os.path.exists(filepath):
        return False, "File not found"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for key component patterns
    has_use_state = 'useState' in content
    has_use_effect = 'useEffect' in content
    has_fetch = 'fetch(' in content
    has_export = 'export' in content
    
    if not (has_export):
        return False, "No export found"
    
    if not has_fetch:
        return False, "No API fetch found"
        
    return True, "OK"

def check_api_endpoint(filepath, endpoint):
    """Check if an API endpoint exists in the Python file"""
    if not os.path.exists(filepath):
        return False, "File not found"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if f'"{endpoint}"' in content or f"'{endpoint}'" in content:
        return True, "OK"
    return False, "Endpoint not found"

def main():
    """Run all verification checks"""
    logger.info("\n" + "="*60)
    logger.info("PIDDY DASHBOARD SETUP VERIFICATION")
    logger.info("="*60 + "\n")
    
    # Check React Components
    logger.info("📋 Checking React Components:")
    logger.info("-" * 60)
    components = [
        "frontend/src/components/Tests.jsx",
        "frontend/src/components/Metrics.jsx",
        "frontend/src/components/Phases.jsx",
        "frontend/src/components/Security.jsx",
        "frontend/src/components/Decisions.jsx",
        "frontend/src/components/Logs.jsx",
        "frontend/src/components/Missions.jsx",
        "frontend/src/components/DependencyGraph.jsx",
        "frontend/src/components/MissionReplay.jsx",
        "frontend/src/components/RateLimits.jsx",
        "frontend/src/components/Sidebar.jsx",
        "frontend/src/components/App.jsx",
    ]
    
    components_ok = 0
    for comp in components:
        exists, msg = check_component_file(comp)
        status = "✅" if exists else "❌"
        logger.info(f"{status} {comp.split('/')[-1]:<25} - {msg}")
        if exists:
            components_ok += 1
    
    logger.info(f"\nComponents: {components_ok}/{len(components)} ✓\n")
    
    # Check CSS
    logger.info("🎨 Checking Stylesheets:")
    logger.info("-" * 60)
    css_file = "frontend/src/styles/components.css"
    if os.path.exists(css_file):
        with open(css_file, 'r') as f:
            lines = len(f.readlines())
        logger.info(f"✅ components.css                  - {lines} lines")
    else:
        logger.info(f"❌ components.css                  - Not found")
    
    logger.info()
    
    # Check API Endpoints
    logger.info("📡 Checking API Endpoints:")
    logger.info("-" * 60)
    api_endpoints = [
        "/api/tests",
        "/api/tests/summary",
        "/api/metrics/performance",
        "/api/phases",
        "/api/security/audit",
        "/api/decisions",
        "/api/logs",
        "/api/missions",
        "/api/graph/dependencies",
        "/api/rate-limits/dashboard",
        "/api/rate-limits/status",
        "/api/rate-limits/metrics",
    ]
    
    api_file = "src/dashboard_api.py"
    endpoints_ok = 0
    for endpoint in api_endpoints:
        exists, msg = check_api_endpoint(api_file, endpoint)
        status = "✅" if exists else "❌"
        logger.info(f"{status} {endpoint:<40} - {msg}")
        if exists:
            endpoints_ok += 1
    
    logger.info(f"\nEndpoints: {endpoints_ok}/{len(api_endpoints)} ✓\n")
    
    # Check Files
    logger.info("📁 Checking Key Files:")
    logger.info("-" * 60)
    key_files = [
        ("src/services/rate_limiter.py", "Rate Limiter Service"),
        ("src/dashboard_api.py", "Dashboard API"),
        ("src/agent/core.py", "Agent Core"),
        ("frontend/src/main.jsx", "Frontend Entry"),
        ("frontend/package.json", "NPM Config"),
        ("requirements.txt", "Python Dependencies"),
    ]
    
    files_ok = 0
    for filepath, desc in key_files:
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        logger.info(f"{status} {desc:<30} - {filepath}")
        if exists:
            files_ok += 1
    
    logger.info(f"\nFiles: {files_ok}/{len(key_files)} ✓\n")
    
    # Summary
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    total_checks = len(components) + 1 + len(api_endpoints) + len(key_files)
    total_passed = components_ok + (1 if os.path.exists(css_file) else 0) + endpoints_ok + files_ok
    
    logger.info(f"\nTotal Checks: {total_passed}/{total_checks}")
    logger.info(f"Success Rate: {(total_passed/total_checks)*100:.1f}%")
    
    if total_passed == total_checks:
        logger.info("\n✅ All checks passed! Dashboard is ready for deployment.\n")
        return 0
    else:
        logger.info("\n⚠️  Some checks failed. Please review above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
