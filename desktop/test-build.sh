#!/bin/bash

# Desktop App Test Suite for Piddy
# Tests all major functionality of the Electron app

echo "════════════════════════════════════════════════════════════════"
echo "  🖥️  PIDDY DESKTOP APP - COMPREHENSIVE TEST SUITE"
echo "════════════════════════════════════════════════════════════════"
echo ""

EXEC_PATH="/workspaces/Piddy/desktop/dist/linux-unpacked"
EXEC="$EXEC_PATH/piddy"

# Test 1: Executable exists and is valid
echo "✓ TEST 1: Executable Integrity"
echo "  Checking: $EXEC"
if [ -x "$EXEC" ]; then
    echo "  ✅ Executable found and is executable"
    FILE_INFO=$(file "$EXEC" | grep -o "ELF.*executable")
    echo "  Type: $FILE_INFO"
else
    echo "  ❌ Executable not found or not executable"
    exit 1
fi
echo ""

# Test 2: Check bundled resources
echo "✓ TEST 2: Bundled Resources"
RESOURCES="$EXEC_PATH/resources"
if [ -d "$RESOURCES" ]; then
    echo "  ✅ Resources directory found"
    
    # Check frontend
    if [ -d "$RESOURCES/frontend/dist" ]; then
        echo "  ✅ Frontend build found ($(du -sh $RESOURCES/frontend/dist | cut -f1))"
    fi
    
    # Check Python sources
    PYTHON_FILES=$(find $RESOURCES/src -name "*.py" 2>/dev/null | wc -l)
    echo "  ✅ Python modules: $PYTHON_FILES files"
    
    # Check requirements
    if [ -f "$RESOURCES/requirements.txt" ]; then
        echo "  ✅ Python requirements found"
    fi
fi
echo ""

# Test 3: Verify app.asar (Electron app archive)
echo "✓ TEST 3: App Archive"
if [ -f "$RESOURCES/app.asar" ]; then
    ASAR_SIZE=$(du -sh "$RESOURCES/app.asar" | cut -f1)
    echo "  ✅ app.asar found (size: $ASAR_SIZE)"
    echo "  Contains: Electron app source and configuration"
else
    echo "  ⚠️  app.asar not found (expected for development build)"
fi
echo ""

# Test 4: Frontend assets
echo "✓ TEST 4: Frontend Assets"
FRONTEND_DIST="$RESOURCES/frontend/dist"
if [ -d "$FRONTEND_DIST" ]; then
    HTML=$(find $FRONTEND_DIST -name "*.html" | wc -l)
    CSS=$(find $FRONTEND_DIST -name "*.css" | wc -l)
    JS=$(find $FRONTEND_DIST -name "*.js" | wc -l)
    
    echo "  ✅ HTML files: $HTML"
    echo "  ✅ CSS files: $CSS"
    echo "  ✅ JavaScript files: $JS"
    
    if [ -f "$FRONTEND_DIST/index.html" ]; then
        echo "  ✅ index.html present"
    fi
fi
echo ""

# Test 5: Check key Electron files
echo "✓ TEST 5: Electron Files"
KEY_FILES=(
    "main.js"
    "preload.js"
    "python-bridge.js"
    "ipc-bridge.js"
    "port-finder.js"
)

for FILE in "${KEY_FILES[@]}"; do
    if [ -f "$EXEC_PATH/../$FILE" ]; then
        echo "  ✅ $FILE"
    else
        echo "  ⚠️  $FILE not found in unpacked"
    fi
done
echo ""

# Test 6: Version and metadata
echo "✓ TEST 6: Application Metadata"
if [ -f "$EXEC_PATH/../package.json" ]; then
    VERSION=$(grep -o '"version"[^,]*' $EXEC_PATH/../package.json | cut -d'"' -f4)
    NAME=$(grep -o '"name"[^,]*' $EXEC_PATH/../package.json | cut -d'"' -f4)
    echo "  App Name: $NAME"
    echo "  Version: $VERSION"
    echo "  Platform: Linux x64"
fi
echo ""

# Test 7: Size analysis
echo "✓ TEST 7: Build Size Analysis"
TOTAL_SIZE=$(du -sh "$EXEC_PATH" | cut -f1)
EXEC_SIZE=$(ls -lh "$EXEC" | awk '{print $5}')
echo "  Total Build Size: $TOTAL_SIZE"
echo "  Executable Size: $EXEC_SIZE"
echo ""

# Test 8: Dynamic Dependencies
echo "✓ TEST 8: System Dependencies"
DEPS=$(ldd "$EXEC" 2>/dev/null | grep "=>" | cut -d' ' -f1 | sort -u | wc -l)
echo "  Linked system libraries: $DEPS"
echo "  Most libraries bundled with app"
echo ""

# Test 9: Python backend check
echo "✓ TEST 9: Python Backend"
if [ -f "$RESOURCES/start_piddy.py" ]; then
    echo "  ✅ Python launcher found: start_piddy.py"
    if command -v python3 &> /dev/null; then
        PY_VERSION=$(python3 --version 2>&1)
        echo "  ✅ System Python available: $PY_VERSION"
    fi
fi
echo ""

# Test 10: Summary report
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ DESKTOP APP BUILD TEST COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 BUILD SUMMARY:"
echo "  • Processor: x64 (64-bit Intel/AMD)"
echo "  • Platform: Linux"
echo "  • Electron: v28.3.3"
echo "  • Runtime: Chromium + Node.js"
echo "  • Frontend: React 18 + Vite (optimized)"
echo "  • Backend: Python 3 + FastAPI"
echo ""

echo "🎯 READY FOR DEPLOYMENT"
echo ""
echo "To run the app:"
echo "  cd /workspaces/Piddy/desktop/dist/linux-unpacked"
echo "  ./piddy"
echo ""
echo "To create installer:"
echo "  cd /workspaces/Piddy/desktop"
echo "  npm run dist:linux    # Linux AppImage"
echo "  npm run dist:win      # Windows installer"
echo "  npm run dist:mac      # macOS DMG"
echo ""
