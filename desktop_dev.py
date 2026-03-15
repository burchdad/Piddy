"""
This script runs in development mode to test the desktop app with auto-reload
"""

import subprocess
import sys
import os

def main():
    os.chdir(os.path.join(os.path.dirname(__file__), 'desktop'))
    
    print("🚀 Starting Piddy Desktop App in development mode...")
    print("Press Ctrl+C to stop")
    
    try:
        # Start the dev server (concurrently watches both React and Electron)
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except KeyboardInterrupt:
        print("\n✅ Development server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
