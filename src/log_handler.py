"""
JSON-lines log handler for Piddy dashboard.

Writes structured log entries to data/service.log and data/dashboard.log
in the format expected by the dashboard's /api/logs endpoint:

    {"timestamp": "...", "level": "INFO", "source": "...", "message": "...", "details": null}

Usage:
    from src.log_handler import install_dashboard_logging
    install_dashboard_logging()          # call once at startup

After installation every WARNING+ log from any Piddy module is
appended to both log files as a JSON line.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent / "data"
_SERVICE_LOG = _DATA_DIR / "service.log"
_DASHBOARD_LOG = _DATA_DIR / "dashboard.log"

# Max file size before rotation (5 MB)
_MAX_LOG_BYTES = 5 * 1024 * 1024


class DashboardLogHandler(logging.Handler):
    """Logging handler that writes JSON-lines to data/*.log files."""

    def __init__(self, log_path: Path, max_bytes: int = _MAX_LOG_BYTES):
        super().__init__()
        self._path = log_path
        self._max_bytes = max_bytes
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord):
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "source": record.name,
                "message": self.format(record),
                "details": None,
            }

            # Attach exception info if present
            if record.exc_info and record.exc_info[1]:
                entry["details"] = {"exception": str(record.exc_info[1])}

            line = json.dumps(entry, default=str) + "\n"

            # Simple size-based rotation: truncate to last half when over limit
            self._rotate_if_needed()

            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)

        except Exception:
            # Never let logging blow up the app
            pass

    def _rotate_if_needed(self):
        """Trim the log file if it exceeds the max size."""
        try:
            if not self._path.exists():
                return
            size = self._path.stat().st_size
            if size <= self._max_bytes:
                return

            # Keep the last half of the file
            with open(self._path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            keep = lines[len(lines) // 2:]
            with open(self._path, "w", encoding="utf-8") as f:
                f.writelines(keep)
        except Exception:
            pass


def install_dashboard_logging(level: int = logging.WARNING):
    """
    Install JSON-lines handlers on the root logger.

    Call once during startup (e.g. in start_piddy.py or dashboard_api.py).
    All loggers under 'src', 'piddy', 'config' will have their messages
    captured at WARNING level and above.
    """

    # Service log — captures everything from src.* and piddy.*
    service_handler = DashboardLogHandler(_SERVICE_LOG)
    service_handler.setLevel(level)
    service_handler.setFormatter(logging.Formatter("%(message)s"))

    # Dashboard log — captures dashboard_api and dashboard_manager
    dashboard_handler = DashboardLogHandler(_DASHBOARD_LOG)
    dashboard_handler.setLevel(level)
    dashboard_handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root.addHandler(service_handler)

    # Also attach dashboard handler to dashboard-specific loggers
    for name in ("src.dashboard_api", "src.dashboard_manager", "src.approval_dashboard"):
        logging.getLogger(name).addHandler(dashboard_handler)

    logging.getLogger(__name__).info("Dashboard JSON-lines logging installed")
