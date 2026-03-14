#!/usr/bin/env python3
"""
PIDDY Background Service Manager

Manages the autonomous background service:
  - Start/stop the service
  - Check service status
  - View service logs
  - Run in foreground or daemon mode
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime


class ServiceManager:
    """Manages the background service lifecycle"""
    
    SERVICE_PID_FILE = Path("data/service.pid")
    SERVICE_LOG_FILE = Path("data/service.log")
    SERVICE_PYTHON = Path("src/autonomous_background_service.py")
    
    @classmethod
    def ensure_data_dir(cls):
        """Ensure data directory exists"""
        Path("data").mkdir(exist_ok=True)
    
    @classmethod
    def is_running(cls) -> bool:
        """Check if service is currently running"""
        if not cls.SERVICE_PID_FILE.exists():
            return False
        
        try:
            with open(cls.SERVICE_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
            return True
        except (ValueError, ProcessLookupError, OSError):
            return False
    
    @classmethod
    def get_pid(cls) -> int:
        """Get service process ID"""
        if cls.SERVICE_PID_FILE.exists():
            try:
                with open(cls.SERVICE_PID_FILE, 'r') as f:
                    return int(f.read().strip())
            except ValueError:
                pass
        return None
    
    @classmethod
    def start(cls, foreground: bool = False) -> bool:
        """
        Start the background service
        
        Args:
            foreground: If True, run in foreground (blocking). Otherwise, run as daemon.
        """
        cls.ensure_data_dir()
        
        if cls.is_running():
            print("⚠️  Service is already running!")
            pid = cls.get_pid()
            print(f"   Process ID: {pid}")
            print(f"   View logs: tail -f {cls.SERVICE_LOG_FILE}")
            return False
        
        print("🚀 Starting PIDDY Background Service...")
        print(f"   Service: {cls.SERVICE_PYTHON}")
        print(f"   Mode: {'Foreground' if foreground else 'Daemon'}")
        
        if foreground:
            # Run in foreground (blocking)
            try:
                subprocess.run([sys.executable, str(cls.SERVICE_PYTHON)], check=True)
                return True
            except KeyboardInterrupt:
                print("\n⏹️  Service stopped (Ctrl+C)")
                return False
            except subprocess.CalledProcessError as e:
                print(f"❌ Service error: {e}")
                return False
        else:
            # Run as daemon
            try:
                # Start process and redirect output to log
                with open(cls.SERVICE_LOG_FILE, 'a') as log_file:
                    log_file.write(f"\n{'='*80}\n")
                    log_file.write(f"Service started: {datetime.now()}\n")
                    log_file.write(f"{'='*80}\n\n")
                
                process = subprocess.Popen(
                    [sys.executable, str(cls.SERVICE_PYTHON)],
                    stdout=open(cls.SERVICE_LOG_FILE, 'a'),
                    stderr=subprocess.STDOUT,
                    start_new_session=True  # Detach from terminal
                )
                
                # Save PID
                with open(cls.SERVICE_PID_FILE, 'w') as f:
                    f.write(str(process.pid))
                
                print(f"✅ Service started successfully!")
                print(f"   Process ID: {process.pid}")
                print(f"   Log file: {cls.SERVICE_LOG_FILE}")
                print(f"\n💡 To view logs: tail -f {cls.SERVICE_LOG_FILE}")
                print(f"💡 To stop: python src/service_manager.py --stop")
                print(f"💡 To check: python src/service_manager.py --status")
                
                return True
            
            except Exception as e:
                print(f"❌ Failed to start service: {e}")
                return False
    
    @classmethod
    def stop(cls) -> bool:
        """Stop the background service"""
        print("🛑 Stopping PIDDY Background Service...")
        
        if not cls.is_running():
            print("⚠️  Service is not running")
            return False
        
        try:
            pid = cls.get_pid()
            print(f"   Stopping process {pid}...")
            
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to exit
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
            if cls.SERVICE_PID_FILE.exists():
                cls.SERVICE_PID_FILE.unlink()
            
            print("✅ Service stopped successfully!")
            return True
        
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    @classmethod
    def status(cls) -> bool:
        """Check and display service status"""
        print("📊 PIDDY Background Service Status\n")
        
        if cls.is_running():
            pid = cls.get_pid()
            print(f"✅ Status: RUNNING")
            print(f"   Process ID: {pid}")
            print(f"   Memory: Check with: ps aux | grep {pid}")
        else:
            print(f"❌ Status: NOT RUNNING")
        
        print(f"\nℹ️  Configuration:")
        print(f"   Service file: {cls.SERVICE_PYTHON}")
        print(f"   Log file: {cls.SERVICE_LOG_FILE}")
        print(f"   PID file: {cls.SERVICE_PID_FILE}")
        
        if cls.SERVICE_LOG_FILE.exists():
            size = cls.SERVICE_LOG_FILE.stat().st_size
            lines = sum(1 for _ in open(cls.SERVICE_LOG_FILE))
            print(f"\nℹ️  Logs:")
            print(f"   Size: {size:,} bytes")
            print(f"   Lines: {lines:,}")
            print(f"   View: tail -f {cls.SERVICE_LOG_FILE}")
        
        return True
    
    @classmethod
    def tail_logs(cls, lines: int = 50):
        """Display recent log entries"""
        if not cls.SERVICE_LOG_FILE.exists():
            print("❌ No log file found")
            return
        
        print(f"📋 Recent logs ({lines} lines):\n")
        with open(cls.SERVICE_LOG_FILE, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines[-lines:]:
                print(line, end='')
    
    @classmethod
    def clear_logs(cls):
        """Clear service logs"""
        try:
            if cls.SERVICE_LOG_FILE.exists():
                cls.SERVICE_LOG_FILE.unlink()
            print("✅ Logs cleared")
        except Exception as e:
            print(f"❌ Error clearing logs: {e}")


def print_help():
    """Print help information"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║    PIDDY BACKGROUND SERVICE MANAGER                               ║
╚════════════════════════════════════════════════════════════════════╝

Usage: python src/service_manager.py [COMMAND]

Commands:
  --start              Start service as daemon (background)
  --start-fg           Start service in foreground (blocking)
  --stop               Stop the running service
  --status             Check service status
  --logs               Show recent logs (tail -f style)
  --logs N             Show last N log lines (default: 50)
  --clear-logs         Clear all log files
  --restart            Restart the service

Examples:
  python src/service_manager.py --start       # Start in background
  python src/service_manager.py --status      # Check if running
  tail -f data/service.log                    # View live logs
  python src/service_manager.py --stop        # Stop service

Features:
  ✅ Runs as background daemon (doesn't block terminal)
  ✅ Automatic PID file management
  ✅ Graceful shutdown with SIGTERM
  ✅ Log file rotation (appends to same file)
  ✅ Easy status checking
  ✅ Can restart without manual PID cleanup
    """)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PIDDY Background Service Manager", add_help=False)
    parser.add_argument("--start", action="store_true", help="Start as daemon")
    parser.add_argument("--start-fg", action="store_true", help="Start in foreground")
    parser.add_argument("--stop", action="store_true", help="Stop service")
    parser.add_argument("--status", action="store_true", help="Check status")
    parser.add_argument("--logs", nargs='?', const=50, type=int, help="Show logs")
    parser.add_argument("--clear-logs", action="store_true", help="Clear logs")
    parser.add_argument("--restart", action="store_true", help="Restart service")
    parser.add_argument("--help", action="store_true", help="Show help")
    
    args = parser.parse_args()
    
    if args.help or len(sys.argv) == 1:
        print_help()
        return
    
    if args.start:
        ServiceManager.start(foreground=False)
    elif args.start_fg:
        ServiceManager.start(foreground=True)
    elif args.stop:
        ServiceManager.stop()
    elif args.status:
        ServiceManager.status()
    elif args.logs is not None:
        ServiceManager.tail_logs(args.logs)
    elif args.clear_logs:
        ServiceManager.clear_logs()
    elif args.restart:
        ServiceManager.stop()
        time.sleep(1)
        ServiceManager.start(foreground=False)


if __name__ == "__main__":
    main()
