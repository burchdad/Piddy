"""
Piddy Background Service Runner

Runs Piddy as a continuous background service with health monitoring,
process management, and automatic restart capabilities.
"""

import os
import sys
import time
import logging
import signal
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.piddy_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ServiceStatus:
    """Track service health and status."""
    
    def __init__(self, status_file: str = ".piddy_service_status.json"):
        self.status_file = status_file
        self.start_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self.messages_processed = 0
        self.errors = 0
        self.is_running = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "status": "running" if self.is_running else "stopped",
            "start_time": self.start_time.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "messages_processed": self.messages_processed,
            "errors": self.errors,
            "timestamp": datetime.now().isoformat(),
        }
    
    def save(self):
        """Persist status to file."""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    def heartbeat(self):
        """Record a heartbeat."""
        self.last_heartbeat = datetime.now()
        self.messages_processed += 1
        self.save()
    
    def record_error(self):
        """Record an error."""
        self.errors += 1
        self.save()


class PiddyServiceRunner:
    """
    Manages Piddy as a background service with health monitoring.
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.status = ServiceStatus()
        self.running = False
        
        # Signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGHUP, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start Piddy background service."""
        logger.info("🚀 Starting Piddy background service...")
        
        if self.process and self.process.poll() is None:
            logger.warning("⚠️  Piddy is already running (PID: {})".format(self.process.pid))
            return
        
        try:
            # Start Piddy process
            self.process = subprocess.Popen(
                ["bash", "start-slack.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            self.running = True
            self.status.is_running = True
            self.status.save()
            
            logger.info(f"✅ Piddy started successfully (PID: {self.process.pid})")
            logger.info("📡 Listening for Slack messages...")
            
            # Monitor process
            self._monitor()
        
        except Exception as e:
            logger.error(f"❌ Failed to start Piddy: {e}")
            self.status.record_error()
            raise
    
    def stop(self):
        """Stop Piddy service gracefully."""
        logger.info("🛑 Stopping Piddy service...")
        
        if not self.process:
            logger.warning("No process to stop")
            return
        
        try:
            # Terminate gracefully
            self.process.terminate()
            
            # Wait for graceful shutdown (10 seconds)
            try:
                self.process.wait(timeout=10)
                logger.info("✅ Piddy stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if not responsive
                logger.warning("⚠️  Force killing Piddy process...")
                self.process.kill()
                self.process.wait()
                logger.info("✅ Piddy force stopped")
        
        except Exception as e:
            logger.error(f"Error stopping Piddy: {e}")
        
        finally:
            self.running = False
            self.status.is_running = False
            self.status.save()
    
    def _monitor(self):
        """Monitor process and handle restarts."""
        retry_count = 0
        max_retries = 5
        
        while self.running:
            try:
                # Check if process is still alive
                if self.process.poll() is not None:
                    exit_code = self.process.returncode
                    logger.error(f"❌ Piddy process exited with code {exit_code}")
                    self.status.record_error()
                    
                    # Attempt restart
                    if retry_count < max_retries:
                        retry_count += 1
                        wait_time = min(2 ** retry_count, 60)  # Exponential backoff, max 60s
                        logger.info(f"🔄 Restarting Piddy in {wait_time}s (attempt {retry_count}/{max_retries})...")
                        time.sleep(wait_time)
                        
                        # Restart
                        self.process = subprocess.Popen(
                            ["bash", "start-slack.sh"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                        logger.info(f"✅ Piddy restarted (PID: {self.process.pid})")
                        retry_count = 0  # Reset retry count on successful restart
                    else:
                        logger.critical("❌ Max restart attempts exceeded, stopping service")
                        self.running = False
                
                # Check health periodically
                self.status.heartbeat()
                
                # Sleep before next check
                time.sleep(5)
            
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                self.running = False
            
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                self.status.record_error()
                time.sleep(5)
    
    def get_status(self) -> dict:
        """Get current service status."""
        status_dict = self.status.to_dict()
        
        if self.process:
            status_dict["pid"] = self.process.pid
            status_dict["process_alive"] = self.process.poll() is None
        
        return status_dict
    
    @staticmethod
    def check_prerequisites() -> bool:
        """Check if all prerequisites are met."""
        logger.info("🔍 Checking prerequisites...")
        
        checks = {
            ".env file exists": Path(".env").exists(),
            "Slack bot token configured": bool(os.getenv("SLACK_BOT_TOKEN")),
            "Anthropic API key configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "start-slack.sh exists": Path("start-slack.sh").exists(),
            "Virtual environment ready": Path("venv/bin/python").exists() or Path("venv\\Scripts\\python.exe").exists(),
        }
        
        all_ok = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"{status} {check}")
            if not result:
                all_ok = False
        
        return all_ok


def main():
    """Main entry point for service."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Piddy Background Service")
    parser.add_argument("command", choices=["start", "stop", "status", "restart", "check"],
                       help="Service command")
    parser.add_argument("--check", action="store_true", help="Check prerequisites")
    
    args = parser.parse_args()
    
    runner = PiddyServiceRunner()
    
    try:
        if args.command == "check":
            if runner.check_prerequisites():
                logger.info("✅ All prerequisites met, ready to start Piddy")
            else:
                logger.error("❌ Some prerequisites missing, cannot start Piddy")
                sys.exit(1)
        
        elif args.command == "start":
            if not runner.check_prerequisites():
                logger.error("❌ Prerequisites check failed")
                sys.exit(1)
            runner.start()
        
        elif args.command == "stop":
            runner.stop()
        
        elif args.command == "status":
            status = runner.get_status()
            logger.info(f"Service Status: {json.dumps(status, indent=2)}")
        
        elif args.command == "restart":
            runner.stop()
            time.sleep(2)
            if runner.check_prerequisites():
                runner.start()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        runner.stop()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
