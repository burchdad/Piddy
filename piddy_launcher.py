"""
Piddy Desktop Launcher
Double-click to start Piddy dashboard and open it in your browser.
"""

import io
import os
import sys
import time
import webbrowser
import threading
import signal

# ── UTF-8 fix for Windows console ──────────────────────────────────────────
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Ensure project root is on sys.path ─────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

HOST = "localhost"
PORT = 8001
URL = f"http://{HOST}:{PORT}"


def _open_browser():
    """Open the dashboard in the default browser after a short delay."""
    time.sleep(3)
    print(f"\n  Opening {URL} in your browser...\n")
    webbrowser.open(URL)


def main():
    # ── Install structured logging early ────────────────────────────────────
    try:
        from src.log_handler import install_dashboard_logging
        install_dashboard_logging()
    except Exception:
        pass

    print(r"""
    ====================================================
      ____  _     _     _
     |  _ \(_) __| | __| |_   _
     | |_) | |/ _` |/ _` | | | |
     |  __/| | (_| | (_| | |_| |
     |_|   |_|\__,_|\__,_|\__, |
                           |___/
      AI Backend Developer Agent
    ====================================================
    """)
    print(f"  Dashboard: {URL}")
    print(f"  Press Ctrl+C to stop\n")

    # Open browser in background thread
    threading.Thread(target=_open_browser, daemon=True).start()

    # ── Start uvicorn directly (no subprocess) ──────────────────────────────
    try:
        import uvicorn
    except ImportError:
        print("  [ERROR] uvicorn not installed. Run: pip install uvicorn")
        input("  Press Enter to exit...")
        sys.exit(1)

    # Graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

    try:
        uvicorn.run(
            "src.dashboard_api:app",
            host=HOST,
            port=PORT,
            log_level="warning",
        )
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        input("  Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
