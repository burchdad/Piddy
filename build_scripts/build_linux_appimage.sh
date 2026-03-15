#!/bin/bash
# Piddy Linux AppImage Builder

set -e

DESKTOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/desktop"
APP_NAME="Piddy"
APPIMAGE_NAME="Piddy-1.0.0.AppImage"

echo "🐧 Building Linux AppImage for $APP_NAME..."

# Check for required tools
if ! command -v appimagetool &> /dev/null; then
    echo "⚠️  appimagetool not found. Installing AppImage tools..."
    sudo apt-get update
    sudo apt-get install -y appimage-builder
fi

cd "$DESKTOP_DIR"

# Build the app
npm run dist:linux

# AppImage should be created in dist/ directory
if [ -f "dist/$APPIMAGE_NAME" ]; then
    echo "✅ AppImage created: dist/$APPIMAGE_NAME"
    echo ""
    echo "📦 Package contents:"
    ls -lh "dist/$APPIMAGE_NAME"
    
    # Make executable
    chmod +x "dist/$APPIMAGE_NAME"
    echo "✅ Made executable"
else
    echo "❌ Failed to create AppImage"
    exit 1
fi
