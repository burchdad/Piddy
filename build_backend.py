#!/usr/bin/env python
"""
Build script for Piddy backend executable using PyInstaller

This script:
1. Validates environment
2. Builds the backend using PyInstaller
3. Copies the binary to desktop/resources for Electron packaging
4. Generates a build report

Usage:
  python build_backend.py
  python build_backend.py --clean
  python build_backend.py --skip-copy
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def log(level, msg):
    """Simple logging"""
    levels = {"INFO": "✅", "WARN": "⚠️", "ERROR": "❌"}
    symbol = levels.get(level, "•")
    print(f"{symbol} [{level}] {msg}")

def validate_environment():
    """Check if all requirements are met"""
    log("INFO", "Validating environment...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        log("ERROR", f"Python 3.9+ required, got {sys.version}")
        return False
    log("INFO", f"Python version: {sys.version}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        log("INFO", f"PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        log("ERROR", "PyInstaller not installed. Run: pip install pyinstaller")
        return False
    
    # Check required packages
    required = ['fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 'python-dotenv']
    for pkg in required:
        try:
            __import__(pkg)
            log("INFO", f"✓ {pkg} installed")
        except ImportError:
            log("WARN", f"{pkg} not installed. Run: pip install -r requirements.txt")
            return False
    
    # Check spec file
    if not Path('build_backend.spec').exists():
        log("ERROR", "build_backend.spec not found")
        return False
    log("INFO", "build_backend.spec found")
    
    return True

def clean_builds():
    """Clean previous builds"""
    log("INFO", "Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '.spec']
    for d in dirs_to_clean:
        if Path(d).exists():
            shutil.rmtree(d)
            log("INFO", f"Removed {d}")

def build_backend():
    """Run PyInstaller"""
    log("INFO", "Building backend executable...")
    
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        'build_backend.spec',
        '--clean'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        log("INFO", "Backend build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        log("ERROR", f"Build failed: {e.stderr}")
        return False

def get_binary_path():
    """Get path to built binary"""
    binary_name = 'piddy-backend.exe' if sys.platform == 'win32' else 'piddy-backend'
    binary_path = Path('dist') / binary_name
    
    if not binary_path.exists():
        log("ERROR", f"Binary not found at {binary_path}")
        return None
    
    log("INFO", f"Binary found: {binary_path}")
    return binary_path

def copy_to_electron(binary_path):
    """Copy binary to Electron resources"""
    log("INFO", "Copying binary to Electron resources...")
    
    # Create resources directory if needed
    resources_dir = Path('desktop/resources')
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    binary_name = binary_path.name
    dest_path = resources_dir / binary_name
    
    try:
        shutil.copy2(binary_path, dest_path)
        log("INFO", f"Copied to {dest_path}")
        return True
    except Exception as e:
        log("ERROR", f"Failed to copy: {e}")
        return False

def print_summary(binary_path):
    """Print build summary"""
    if binary_path:
        size_mb = binary_path.stat().st_size / (1024 * 1024)
        log("INFO", f"✅ Build Summary:")
        print(f"   Binary: {binary_path}")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Location for Electron: desktop/resources/{binary_path.name}")
        print()
        print("   Next steps:")
        print("   1. cd desktop")
        print("   2. npm run build")
        print("   3. npm start")
        print()
    else:
        log("ERROR", "Build failed - see errors above")

def main():
    parser = argparse.ArgumentParser(description='Build Piddy backend executable')
    parser.add_argument('--clean', action='store_true', help='Clean previous builds')
    parser.add_argument('--skip-copy', action='store_true', help='Skip copying to Electron resources')
    args = parser.parse_args()
    
    print()
    print("=" * 80)
    print("  Piddy Backend Executable Builder")
    print("=" * 80)
    print()
    
    # Validate
    if not validate_environment():
        print()
        log("ERROR", "Environment validation failed")
        sys.exit(1)
    
    print()
    
    # Clean if requested
    if args.clean:
        clean_builds()
        print()
    
    # Build
    if not build_backend():
        print()
        log("ERROR", "Build failed")
        sys.exit(1)
    
    print()
    
    # Get binary
    binary_path = get_binary_path()
    if not binary_path:
        log("ERROR", "Could not locate built binary")
        sys.exit(1)
    
    print()
    
    # Copy if not skipped
    if not args.skip_copy:
        if not copy_to_electron(binary_path):
            log("WARN", "Failed to copy to Electron, but build succeeded")
    
    print()
    
    # Summary
    print_summary(binary_path)
    print("=" * 80)
    print()

if __name__ == '__main__':
    main()
