#!/bin/bash
# Piddy Desktop App Build Script
# Builds Piddy as a standalone desktop application for distribution

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="$PROJECT_ROOT/desktop"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Piddy Desktop App Build System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Install from: https://nodejs.org/${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm $NPM_VERSION${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Install from: https://python.org/${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

echo ""

# Setup
echo -e "${YELLOW}📦 Setting up build environment...${NC}"

# Create build directories
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

# Install Electron dependencies
echo -e "${YELLOW}📦 Installing Electron dependencies...${NC}"
cd "$DESKTOP_DIR"
npm install --legacy-peer-deps

echo -e "${GREEN}✓ Electron dependencies installed${NC}"

# Build React frontend
echo -e "${YELLOW}🎨 Building React frontend...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  Installing frontend dependencies...${NC}"
    npm install --legacy-peer-deps
fi

npm run build
echo -e "${GREEN}✓ Frontend built${NC}"

# Return to desktop directory
cd "$DESKTOP_DIR"

# Build for all platforms or specific platform
PLATFORM=${1:-all}

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔨 Building for: ${PLATFORM}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

case "$PLATFORM" in
    "all")
        echo -e "${YELLOW}📦 Building for Windows, macOS, and Linux...${NC}"
        npm run dist
        ;;
    "win" | "windows")
        echo -e "${YELLOW}📦 Building for Windows...${NC}"
        npm run dist:win
        ;;
    "mac" | "macos")
        echo -e "${YELLOW}📦 Building for macOS...${NC}"
        npm run dist:mac
        ;;
    "linux")
        echo -e "${YELLOW}📦 Building for Linux...${NC}"
        npm run dist:linux
        ;;
    *)
        echo -e "${RED}❌ Unknown platform: $PLATFORM${NC}"
        echo "Usage: $0 [all|windows|macos|linux]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Build complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# List built artifacts
if [ -d "dist" ]; then
    echo -e "${BLUE}📦 Built artifacts:${NC}"
    ls -lh dist/
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Test the built application"
echo -e "  2. Upload to GitHub Releases"
echo -e "  3. Configure auto-update in Electron app"
echo ""
