#!/bin/bash
# Piddy macOS DMG Package Builder

set -e

DESKTOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/desktop"
APP_NAME="Piddy"
DMG_NAME="Piddy-1.0.0.dmg"

echo "🍎 Building macOS DMG package for $APP_NAME..."

cd "$DESKTOP_DIR"

# Build the app
npm run dist:mac

# DMG should be created in dist/ directory
if [ -f "dist/$DMG_NAME" ]; then
    echo "✅ DMG created: dist/$DMG_NAME"
    echo ""
    echo "📦 Package contents:"
    ls -lh "dist/$DMG_NAME"
else
    echo "❌ Failed to create DMG"
    exit 1
fi
