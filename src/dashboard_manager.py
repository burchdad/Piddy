#!/usr/bin/env python3
"""
PIDDY Unified Dashboard Manager

Manages the unified Piddy dashboard (monitoring + approvals):
  - Start/stop the dashboard server
  - Configure dashboard port and settings
  - Open dashboard in browser
  - Check dashboard status

Integrates:
  - System monitoring & observability
  - Market gap approval workflow
  - Agent status & reputation
  - Phase deployments
"""

import os
import sys
import time
import subprocess
import signal
import webbrowser
from pathlib import Path
from datetime import datetime


class DashboardManager:
    """Manages the unified Piddy dashboard"""
    
    DASHBOARD_PYTHON = Path("src/dashboard_api.py")
    DASHBOARD_PID_FILE = Path("data/dashboard.pid")
    DASHBOARD_LOG_FILE = Path("data/dashboard.log")
    
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 8000
    
    @classmethod
    def ensure_data_dir(cls):
        """Ensure data directory exists"""
        Path("data").mkdir(exist_ok=True)
    
    @classmethod
    def is_running(cls) -> bool:
        """Check if dashboard is running"""
        if not cls.DASHBOARD_PID_FILE.exists():
            return False
        
        try:
            with open(cls.DASHBOARD_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, 0)  # Signal 0 = check only
            return True
        except (ValueError, ProcessLookupError, OSError):
            return False
    
    @classmethod
    def get_pid(cls) -> int:
        """Get dashboard process ID"""
        if cls.DASHBOARD_PID_FILE.exists():
            try:
                with open(cls.DASHBOARD_PID_FILE, 'r') as f:
                    return int(f.read().strip())
            except ValueError:
                pass
        return None
    
    @classmethod
    def start(cls, host: str = None, port: int = None, foreground: bool = False, 
              open_browser: bool = True) -> bool:
        """
        Start the approval dashboard
        
        Args:
            host: Server host (default: localhost)
            port: Server port (default: 8000)
            foreground: Run in foreground instead of daemon
            open_browser: Auto-open dashboard in browser
        """
        cls.ensure_data_dir()
        
        host = host or cls.DEFAULT_HOST
        port = port or cls.DEFAULT_PORT
        
        if cls.is_running():
            print("⚠️  Dashboard is already running!")
            pid = cls.get_pid()
            print(f"   Process ID: {pid}")
            print(f"   URL: http://{host}:{port}")
            print(f"   View logs: tail -f {cls.DASHBOARD_LOG_FILE}")
            return False
        
        print("🚀 Starting PIDDY Approval Dashboard...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   URL: http://{host}:{port}")
        print(f"   Mode: {'Foreground' if foreground else 'Daemon'}")
        
        # Build uvicorn command
        uvicorn_cmd = [
            sys.executable, "-m", "uvicorn",
            "dashboard_api:app",
            "--host", host,
            "--port", str(port),
            "--reload",  # Auto-reload on file changes
        ]
        
        if foreground:
            try:
                # Run in foreground
                subprocess.run(uvicorn_cmd, cwd="src", check=True)
                return True
            except KeyboardInterrupt:
                print("\n⏹️  Dashboard stopped (Ctrl+C)")
                return False
            except subprocess.CalledProcessError as e:
                print(f"❌ Dashboard error: {e}")
                return False
        else:
            try:
                # Run as daemon
                with open(cls.DASHBOARD_LOG_FILE, 'a') as log_file:
                    log_file.write(f"\n{'='*80}\n")
                    log_file.write(f"Dashboard started: {datetime.now()}\n")
                    log_file.write(f"URL: http://{host}:{port}\n")
                    log_file.write(f"{'='*80}\n\n")
                
                process = subprocess.Popen(
                    uvicorn_cmd,
                    cwd="src",
                    stdout=open(cls.DASHBOARD_LOG_FILE, 'a'),
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
                
                # Save PID
                with open(cls.DASHBOARD_PID_FILE, 'w') as f:
                    f.write(str(process.pid))
                
                # Wait a moment for server to start
                time.sleep(2)
                
                if not cls.is_running():
                    print("❌ Dashboard failed to start. Check logs:")
                    print(f"   tail {cls.DASHBOARD_LOG_FILE}")
                    return False
                
                print(f"✅ Dashboard started successfully!")
                print(f"   Process ID: {process.pid}")
                print(f"   URL: http://{host}:{port}")
                print(f"   Log file: {cls.DASHBOARD_LOG_FILE}")
                
                # Try to open in browser
                if open_browser:
                    try:
                        webbrowser.open(f"http://{host}:{port}")
                        print(f"   Opening browser...")
                    except Exception as e:
                        print(f"   (Browser open failed: {e})")
                
                print(f"\n💡 Commands:")
                print(f"   View: http://{host}:{port}")
                print(f"   Logs: tail -f {cls.DASHBOARD_LOG_FILE}")
                print(f"   Stop: python src/dashboard_manager.py --stop")
                
                return True
            
            except Exception as e:
                print(f"❌ Failed to start dashboard: {e}")
                return False
    
    @classmethod
    def stop(cls) -> bool:
        """Stop the dashboard"""
        print("🛑 Stopping PIDDY Approval Dashboard...")
        
        if not cls.is_running():
            print("⚠️  Dashboard is not running")
            return False
        
        try:
            pid = cls.get_pid()
            print(f"   Stopping process {pid}...")
            
            # Graceful shutdown
            os.kill(pid, signal.SIGTERM)
            
            for i in range(10):
                time.sleep(0.5)
                if not cls.is_running():
                    break
            
            # Force kill if still running
            if cls.is_running():
                print("   Force killing process...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
            
            # Remove PID file
            if cls.DASHBOARD_PID_FILE.exists():
                cls.DASHBOARD_PID_FILE.unlink()
            
            print("✅ Dashboard stopped successfully!")
            return True
        
        except Exception as e:
            print(f"❌ Error stopping dashboard: {e}")
            return False
    
    @classmethod
    def status(cls) -> None:
        """Check dashboard status"""
        print("📊 PIDDY Approval Dashboard Status\n")
        
        host = cls.DEFAULT_HOST
        port = cls.DEFAULT_PORT
        
        if cls.is_running():
            pid = cls.get_pid()
            print(f"✅ Status: RUNNING")
            print(f"   Process ID: {pid}")
            print(f"   URL: http://{host}:{port}")
        else:
            print(f"❌ Status: NOT RUNNING")
        
        print(f"\nℹ️  Configuration:")
        print(f"   Dashboard file: {cls.DASHBOARD_PYTHON}")
        print(f"   Log file: {cls.DASHBOARD_LOG_FILE}")
        print(f"   Default host: {host}")
        print(f"   Default port: {port}")
        
        if cls.DASHBOARD_LOG_FILE.exists():
            size = cls.DASHBOARD_LOG_FILE.stat().st_size
            lines = sum(1 for _ in open(cls.DASHBOARD_LOG_FILE))
            print(f"\nℹ️  Logs:")
            print(f"   Size: {size:,} bytes")
            print(f"   Lines: {lines:,}")


def print_help():
    """Print help"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║    PIDDY UNIFIED DASHBOARD MANAGER                                ║
╚════════════════════════════════════════════════════════════════════╝

Usage: python src/dashboard_manager.py [COMMAND]

Commands:
  --start              Start dashboard UI (background)
  --start-fg           Start dashboard in foreground
  --stop               Stop the dashboard
  --status             Check dashboard status
  --open               Open dashboard in browser
  --restart            Restart the dashboard
  --help               Show this help

Options:
  --host HOST          Server host (default: localhost)
  --port PORT          Server port (default: 8000)

Examples:
  python src/dashboard_manager.py --start           # Start background
  python src/dashboard_manager.py --start --port 9000  # Custom port
  python src/dashboard_manager.py --status          # Check status
  python src/dashboard_manager.py --open            # Open in browser

Features:
  ✅ Unified monitoring + market gap approvals
  ✅ Runs as background daemon
  ✅ Auto-opens in browser on first start
  ✅ FastAPI with auto-reload
  ✅ Easy status checking
  ✅ Graceful shutdown

Dashboard Sections:
  📊 System Monitoring
    - Agent status & reputation
    - Real-time message feeds
    - Phase deployments
    - Performance metrics

  📋 Market Gap Approvals
    - Review pending gaps
    - Approve/reject with security assessment
    - Risk indicators (🚨 HIGH / ⚠️ MEDIUM / ✅ LOW)
    - Rejection reason tracking
    - Audit trail
    """)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PIDDY Unified Dashboard Manager - Monitoring + Approvals", add_help=False)
    parser.add_argument("--start", action="store_true", help="Start as daemon")
    parser.add_argument("--start-fg", action="store_true", help="Start in foreground")
    parser.add_argument("--stop", action="store_true", help="Stop dashboard")
    parser.add_argument("--status", action="store_true", help="Check status")
    parser.add_argument("--open", action="store_true", help="Open in browser")
    parser.add_argument("--restart", action="store_true", help="Restart dashboard")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--help", action="store_true", help="Show help")
    
    args = parser.parse_args()
    
    if args.help or len(sys.argv) == 1:
        print_help()
        return
    
    if args.start:
        DashboardManager.start(host=args.host, port=args.port, open_browser=True)
    elif args.start_fg:
        DashboardManager.start(host=args.host, port=args.port, foreground=True)
    elif args.stop:
        DashboardManager.stop()
    elif args.status:
        DashboardManager.status()
    elif args.open:
        if DashboardManager.is_running():
            webbrowser.open(f"http://{args.host}:{args.port}")
            print(f"✅ Opening http://{args.host}:{args.port}")
        else:
            print("❌ Dashboard is not running. Start it first:")
            print(f"   python src/dashboard_manager.py --start")
    elif args.restart:
        DashboardManager.stop()
        time.sleep(1)
        DashboardManager.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
