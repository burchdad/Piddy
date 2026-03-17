#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Piddy Unified Startup Script - Start Everything

Starts all Piddy components:
- Background service (market gap detection, email, approvals)
- Dashboard API (system monitoring + approvals)
- Frontend (React app)
- Health checks and verification

Usage:
    python start_piddy.py                    # Start all in background
    python start_piddy.py --foreground       # Start main service in foreground (debug)
    python start_piddy.py --dashboard-only   # Start only dashboard
    python start_piddy.py --service-only     # Start only background service
    python start_piddy.py --frontend-only    # Start only frontend
    python start_piddy.py --configure        # Setup email configuration first
"""

import os
import sys
import time
import subprocess
import signal
import json
import argparse
import shutil
import requests
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    """Log info message"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def log_success(msg):
    """Log success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def log_warning(msg):
    """Log warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def log_error(msg):
    """Log error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def log_header(msg):
    """Log header message"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def check_dependencies():
    """Check if all required dependencies are available"""
    log_header("🔍 Checking Dependencies")
    
    dependencies = {
        "python": "python3",
        "node": "nodejs (for frontend)",
        "npm": "npm (for frontend)",
    }
    
    all_good = True
    for name, desc in dependencies.items():
        try:
            result = subprocess.run(
                [name, "--version"],
                capture_output=True,
                timeout=2,
                text=True
            )
            log_success(f"{desc} - {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            if name == "npm":
                log_warning(f"{desc} - optional (for frontend)")
            else:
                log_error(f"{desc} - NOT FOUND")
                all_good = False
    
    if not all_good:
        log_error("Missing required dependencies!")
        sys.exit(1)
    
    log_success("All dependencies available")

def check_configuration():
    """Check if email configuration exists"""
    log_header("⚙️ Checking Configuration")
    
    config_file = Path(".env")
    if config_file.exists():
        log_success("Environment configuration found (.env)")
    else:
        log_warning("No .env file found - using defaults")
    
    # Check if email config exists
    email_config = Path("config/email_config.json")
    if email_config.exists():
        try:
            with open(email_config, 'r') as f:
                config = json.load(f)
            log_success(f"Email configured for: {config.get('email', 'unknown')}")
        except:
            log_warning("Email config exists but couldn't be read")
    else:
        log_warning("Email not configured - approval emails won't be sent")
        log_info("Run: python src/email_config.py --profile gmail to configure")

def install_frontend_dependencies():
    """Install npm dependencies for frontend - skip if already built or in desktop mode"""
    log_header("📦 Installing Frontend Dependencies")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        log_warning("Frontend directory not found - skipping")
        return False
    
    # Skip npm install if frontend is already built (dist folder exists)
    dist_dir = frontend_dir / "dist"
    if dist_dir.exists():
        log_info("Frontend already built (dist/ exists) - skipping npm install")
        return True
    
    # Skip npm install if we don't have access to npm in this environment
    try:
        import shutil
        if not shutil.which("npm"):
            log_warning("npm not found in PATH - skipping frontend build")
            log_warning("Frontend dist must be built separately: cd frontend && npm install && npm run build")
            return False
    except:
        pass
    
    try:
        log_info("Installing npm packages...")
        subprocess.run(
            ["npm", "install"],
            cwd="frontend",
            check=True,
            timeout=120
        )
        log_success("Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to install frontend dependencies: {e}")
        return False
    except subprocess.TimeoutExpired:
        log_error("Frontend dependency installation timed out")
        return False

def build_frontend():
    """Build frontend (Vite)"""
    log_header("🏗️ Building Frontend")
    
    try:
        log_info("Building frontend with Vite...")
        subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            check=True,
            timeout=60
        )
        log_success("Frontend built successfully")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Frontend build failed: {e}")
        return False
    except subprocess.TimeoutExpired:
        log_error("Frontend build timed out")
        return False

def start_background_service(foreground=False):
    """Start background service"""
    log_header("🎯 Starting Background Service")
    
    try:
        if foreground:
            log_info("Starting background service in foreground...")
            result = subprocess.run(
                [sys.executable, "src/service_manager.py", "--start-fg"],
                cwd="."
            )
            if result.returncode != 0:
                log_error(f"Background service exited with code {result.returncode}")
                return False
        else:
            log_info("Starting background service in background...")
            # Capture output for debugging
            proc = subprocess.Popen(
                [sys.executable, "src/service_manager.py", "--start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="."
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if proc.poll() is not None:
                # Process exited already
                stdout, stderr = proc.communicate()
                log_error(f"Background service failed to start (exit code {proc.returncode})")
                if stdout:
                    log_error(f"STDOUT: {stdout}")
                if stderr:
                    log_error(f"STDERR: {stderr}")
                return False
            
            log_success("Background service started")
    except FileNotFoundError:
        log_error("service_manager.py not found")
        return False
    except Exception as e:
        log_error(f"Failed to start background service: {e}")
        return False
    
    return True

def start_dashboard(foreground=False):
    """Start dashboard API"""
    log_header("📊 Starting Dashboard API")
    
    try:
        log_info("Starting dashboard...")
        
        # Build command - use sys.executable to get the same Python that's running this script
        cmd = [sys.executable, "src/dashboard_manager.py"]
        if foreground:
            cmd.append("--start-fg")  # Use --start-fg for foreground
        else:
            cmd.append("--start")
        
        # If foreground mode, don't suppress output
        if foreground:
            log_info(f"Running in foreground: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=".")
            if result.returncode != 0:
                log_error(f"Dashboard exited with code {result.returncode}")
                return False
        else:
            log_info(f"Running in background: {' '.join(cmd)}")
            # For background mode, capture output for debugging
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if proc.poll() is not None:
                # Process exited already
                stdout, stderr = proc.communicate()
                log_error(f"Dashboard failed to start (exit code {proc.returncode})")
                if stdout:
                    log_error(f"STDOUT: {stdout}")
                if stderr:
                    log_error(f"STDERR: {stderr}")
                return False
            
            log_success("Dashboard started")
    except FileNotFoundError as e:
        log_error(f"dashboard_manager.py not found: {e}")
        return False
    except Exception as e:
        log_error(f"Failed to start dashboard: {e}")
        return False
    
    return True

def start_frontend():
    """Start frontend dev server"""
    log_header("🎨 Starting Frontend")
    
    try:
        log_info("Starting frontend dev server...")
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        log_success("Frontend dev server started")
    except FileNotFoundError:
        log_error("npm not found")
        return False
    except Exception as e:
        log_error(f"Failed to start frontend: {e}")
        return False
    
    return True

def health_check():
    """Check if all services are running"""
    log_header("🏥 Health Check")
    
    checks = {
        "Dashboard API": {
            "url": "http://localhost:8001/api/system/overview",
            "timeout": 5
        },
        "Approval Endpoints": {
            "url": "http://localhost:8001/api/approvals",
            "timeout": 5
        },
    }
    
    all_healthy = True
    for service, config in checks.items():
        try:
            response = requests.get(config["url"], timeout=config["timeout"])
            if response.status_code == 200:
                log_success(f"{service} - OK")
            else:
                log_warning(f"{service} - HTTP {response.status_code}")
                if response.text:
                    log_info(f"  Response: {response.text[:100]}")
        except requests.exceptions.ConnectionError as e:
            log_error(f"{service} - Connection refused")
            log_info(f"  Error: {str(e)}")
            all_healthy = False
        except requests.exceptions.Timeout:
            log_error(f"{service} - Timeout")
            all_healthy = False
        except Exception as e:
            log_warning(f"{service} - {str(e)}")

    
    return all_healthy

def show_status():
    """Show startup status and next steps"""
    log_header("🚀 Piddy Unified Startup Complete!")
    
    print("""
    📊 Dashboard:     http://localhost:8001/
    🎨 Frontend:      http://localhost:5173/ (dev server)
    📋 Approvals:     http://localhost:8001/#/approvals
    
    ✨ Key Features:
    • Market gap detection & reporting
    • Automatic email notifications
    • Approval workflow with security assessment
    • Unified monitoring dashboard
    • Real-time system metrics
    
    📝 Next Steps:
    1. Open http://localhost:8001 in your browser
    2. Click on "Approvals" tab in the sidebar
    3. Review pending market gaps
    4. Approve/reject gaps based on security & business needs
    5. Check system monitoring in other tabs
    
    🔧 Configuration:
    • Email config:    python src/email_config.py --profile gmail
    • Logs:            tail -f data/service.log
    • Database:        sqlite data/.piddy_audit.db
    
    📚 Documentation:
    • Quick Start:     cat UNIFIED_DASHBOARD_INTEGRATION.md
    • Approvals:       cat APPROVAL_SYSTEM_QUICKSTART.md
    • Deployment:      cat DEPLOYMENT_GUIDE_APPROVAL_SYSTEM.md
    
    💡 Tips:
    • Monitor logs: tail -f data/service.log
    • Check health: curl http://localhost:8001/api/system/overview
    • View approvals: curl http://localhost:8001/api/approvals
    • Stop services: python src/service_manager.py --stop
    
    """)

def configure_email():
    """Configure email settings"""
    log_header("✉️ Email Configuration")
    
    try:
        subprocess.run(
            ["python", "src/email_config.py", "--interactive"],
            check=True
        )
        log_success("Email configured successfully")
        return True
    except FileNotFoundError:
        log_error("email_config.py not found")
        return False
    except subprocess.CalledProcessError:
        log_error("Email configuration failed")
        return False
    except Exception as e:
        log_error(f"Error during email configuration: {e}")
        return False

def cleanup():
    """Clean up on exit"""
    log_info("\nShutting down services...")
    try:
        subprocess.run(
            ["python", "src/service_manager.py", "--stop"],
            timeout=5,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass

def main():
    # Force UTF-8 encoding on Windows
    import sys
    import platform
    if platform.system() == 'Windows':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(
        description="🚀 Piddy Unified Startup - Start all system components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_piddy.py                    # Start all services
  python start_piddy.py --foreground       # Debug: run service in foreground
  python start_piddy.py --dashboard-only   # Start only dashboard
  python start_piddy.py --service-only     # Start only background service
  python start_piddy.py --configure        # Configure email first
        """
    )
    
    parser.add_argument("--foreground", action="store_true", 
                       help="Run background service in foreground (for debugging)")
    parser.add_argument("--dashboard-only", action="store_true",
                       help="Start only dashboard API")
    parser.add_argument("--service-only", action="store_true",
                       help="Start only background service")
    parser.add_argument("--frontend-only", action="store_true",
                       help="Start only frontend dev server")
    parser.add_argument("--no-frontend", action="store_true",
                       help="Start all services except frontend")
    parser.add_argument("--no-health-check", action="store_true",
                       help="Skip health checks")
    parser.add_argument("--configure", action="store_true",
                       help="Configure email before starting")
    parser.add_argument("--desktop", action="store_true",
                       help="Run in desktop app mode (called from Electron)")
    parser.add_argument("--rpc-mode", action="store_true",
                       help="Run in RPC mode (direct IPC, no HTTP ports)")
    
    args = parser.parse_args()
    
    # Print header
    print(f"""{Colors.BOLD}{Colors.CYAN}
    ╔════════════════════════════════════════╗
    ║   🚀 Piddy Unified System Startup      ║
    ║      Market-Driven Autonomous Agent    ║
    ╚════════════════════════════════════════╝
    {Colors.END}
    """)
    
    # Register cleanup
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    
    # Check dependencies first
    check_dependencies()
    check_configuration()
    
    # Configure email if requested
    if args.configure:
        configure_email()
        time.sleep(1)
    
    # RPC Mode - Initialize RPC server instead of HTTP
    if args.rpc_mode:
        log_header("🔌 Starting RPC Mode (Zero-Port IPC)")
        log_info("Initializing RPC server for direct Python-Electron communication...")
        
        try:
            from piddy.rpc_server import get_rpc_server, register_default_endpoints, start_rpc_server
            
            # Register all API endpoints
            if not register_default_endpoints():
                log_error("❌ Failed to register RPC endpoints")
                sys.exit(1)
            
            log_success("✅ RPC server initialized with all endpoints")
            log_info("RPC Server listening on stdin/stdout (zero external ports)")
            
            # Start RPC server - this blocks until shutdown
            start_rpc_server()
            
        except Exception as e:
            log_error(f"❌ RPC mode initialization failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        return
    
    # Start specific components
    if args.dashboard_only:
        start_dashboard(foreground=True)  # Run in foreground for --dashboard-only
        if not args.no_health_check:
            time.sleep(1)
            health_check()
        show_status()
        return
    
    if args.service_only:
        start_background_service(args.foreground)
        return
    
    if args.frontend_only:
        install_frontend_dependencies()
        start_frontend()
        log_info("Frontend running on http://localhost:5173")
        return
    
    # Desktop app mode - start all services
    if args.desktop:
        log_header("🎯 Starting Piddy Desktop Application")
        log_info("Running from Electron desktop app")
        log_info("Frontend already built and served via HTTP static server in Electron")
        
        # Skip frontend dependency installation - frontend is bundled
        log_info("Frontend already bundled in distribution")
        
        # Start only backend services (Electron provides frontend)
        # Use background mode for both (not foreground)
        service_ok = start_background_service(foreground=False)
        dashboard_ok = start_dashboard(foreground=False)
        
        if not (service_ok and dashboard_ok):
            log_error("⚠️  Some backend services failed to start, but continuing...")
        
        # Health checks
        if not args.no_health_check:
            time.sleep(2)
            health_check()
        
        # Show status
        show_status()
        log_success("✅ Piddy Desktop App is running!")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup()
            log_info("Piddy Desktop App shutting down...")
            sys.exit(0)
        return
    
    # Start all services
    log_header("🎯 Starting All Services")
    
    # Install frontend dependencies
    install_frontend_dependencies()
    
    # Build frontend (optional, for production-like setup)
    # Uncomment below to build instead of running dev server
    # build_frontend()
    
    # Start services
    start_background_service(args.foreground)
    start_dashboard(foreground=args.foreground)
    
    if not args.no_frontend:
        start_frontend()
    
    # Health checks
    if not args.no_health_check:
        time.sleep(2)
        health_check()
    
    # Show status
    show_status()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
