"""
Piddy Desktop Application Launcher
Handles startup when running as a desktop application
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class DesktopAppLauncher:
    """Manages Piddy when running as a desktop application"""

    def __init__(self):
        """Initialize the desktop launcher"""
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / "data"
        self.config_dir = self.app_dir / "config"
        self.log_dir = self.data_dir / "logs"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        self._setup_logging()
        logger.info("✅ Desktop launcher initialized")

    def _setup_logging(self):
        """Setup logging for desktop environment"""
        log_file = self.log_dir / f"piddy_desktop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(fh)
        root_logger.addHandler(ch)
        
        logger.info(f"📝 Logging to: {log_file}")

    def start_desktop_app(self):
        """
        Start Piddy in desktop mode
        This starts the full application stack with desktop-specific optimizations
        """
        logger.info("🚀 Starting Piddy Desktop Application")
        logger.info(f"App directory: {self.app_dir}")
        logger.info(f"Data directory: {self.data_dir}")
        
        # Import and start the unified startup
        try:
            from start_piddy import (
                check_dependencies,
                check_configuration,
                install_frontend_dependencies,
                start_background_service,
                start_dashboard,
                start_frontend,
                health_check,
                open_browser
            )
            
            # Run startup checks
            logger.info("📋 Running startup checks...")
            if not check_dependencies():
                logger.error("❌ Dependency check failed")
                return False
            
            logger.info("✅ Dependencies OK")
            
            if not check_configuration():
                logger.warning("⚠️ Configuration incomplete, using defaults")
            
            logger.info("✅ Configuration OK")
            
            # Install frontend deps if needed
            logger.info("📦 Installing frontend dependencies...")
            if not install_frontend_dependencies():
                logger.warning("⚠️ Frontend dependency installation had issues")
            
            # Start services
            logger.info("🔄 Starting background service...")
            bg_process = start_background_service()
            
            logger.info("🔄 Starting dashboard API...")
            api_process = start_dashboard()
            
            logger.info("🔄 Starting frontend...")
            frontend_process = start_frontend()
            
            # Verify health
            logger.info("🏥 Checking system health...")
            if not health_check():
                logger.warning("⚠️ Some health checks failed but system is running")
            
            logger.info("✅ Piddy Desktop Application is ready!")
            logger.info("🌐 Dashboard available at http://localhost:3000")
            
            # Open browser to dashboard (Electron will handle this)
            open_browser("http://localhost:3000")
            
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested")
                if bg_process:
                    bg_process.terminate()
                if api_process:
                    api_process.terminate()
                if frontend_process:
                    frontend_process.terminate()
                return True
                
        except ImportError as e:
            logger.error(f"❌ Failed to import startup module: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False

    def get_config(self):
        """Get desktop app configuration"""
        config_file = self.config_dir / "desktop_config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Return defaults
        return {
            "window_width": 1400,
            "window_height": 900,
            "theme": "dark",
            "auto_update": True,
            "telemetry": False
        }

    def save_config(self, config: dict):
        """Save desktop app configuration"""
        config_file = self.config_dir / "desktop_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 Configuration saved to {config_file}")

    def get_app_info(self):
        """Get application information"""
        return {
            "name": "Piddy",
            "version": "1.0.0",
            "description": "AI Backend Developer Agent - Desktop Edition",
            "app_dir": str(self.app_dir),
            "data_dir": str(self.data_dir),
            "config_dir": str(self.config_dir)
        }


def main():
    """Main entry point for desktop launcher"""
    parser = argparse.ArgumentParser(description="Piddy Desktop Application")
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--data-dir",
        help="Override data directory",
        default=None
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    try:
        launcher = DesktopAppLauncher()
        success = launcher.start_desktop_app()
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
