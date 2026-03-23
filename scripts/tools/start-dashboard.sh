#!/bin/bash

# Piddy Dashboard Full Stack Startup Script
# This script starts all necessary services for the Piddy Dashboard

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PIDDY_PORT=8000
FRONTEND_PORT=3000
DASHBOARD_API_PORT=8000

echo -e "${BLUE}🎯 Piddy Dashboard Startup Script${NC}"
echo -e "${BLUE}===================================${NC}\n"

# Function to check if port is in use
check_port() {
    if nc -zv localhost "$1" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for $service to be ready on port $port...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if check_port "$port"; then
            echo -e "${GREEN}✓ $service is running on port $port${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}✗ $service failed to start on port $port${NC}"
    return 1
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}⏹ Shutting down services...${NC}"
    
    if [ ! -z "$PIDDY_PID" ]; then
        echo "Stopping Piddy Core (PID: $PIDDY_PID)"
        kill $PIDDY_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$DASHBOARD_API_PID" ]; then
        echo "Stopping Dashboard API (PID: $DASHBOARD_API_PID)"
        kill $DASHBOARD_API_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ All services stopped${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Check Python availability
if ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Python is not installed${NC}"
    exit 1
fi

# Check Node availability
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi

# Check npm availability
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites installed${NC}\n"

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================
# Check if services are already running
# ============================================
echo -e "${BLUE}📋 Checking for running services...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠ Port 8000 is already in use${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠ Port 3000 is already in use${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# ============================================
# Step 1: Start Piddy Core (Optional)
# ============================================
echo -e "\n${BLUE}📦 Step 1: Starting Piddy Core${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠ Piddy Core appears to be running already${NC}"
else
    echo "Starting Piddy Core..."
    python src/main.py > /tmp/piddy-core.log 2>&1 &
    PIDDY_PID=$!
    echo -e "${GREEN}✓ Piddy Core started (PID: $PIDDY_PID)${NC}"
    
    if ! wait_for_service 8000 "Piddy Core"; then
        echo -e "${RED}✗ Failed to start Piddy Core${NC}"
        echo "Check /tmp/piddy-core.log for details"
        exit 1
    fi
fi

# Brief pause to ensure Piddy is fully ready
sleep 2

# ============================================
# Step 2: Start Dashboard API
# ============================================
echo -e "\n${BLUE}📊 Step 2: Starting Dashboard API${NC}"

# Check if dashboar_api.py exists
if [ ! -f "src/dashboard_api.py" ]; then
    echo -e "${RED}✗ Dashboard API not found at src/dashboard_api.py${NC}"
    echo "Please ensure src/dashboard_api.py exists"
    exit 1
fi

echo "Starting Dashboard API..."
python src/dashboard_api.py > /tmp/dashboard-api.log 2>&1 &
DASHBOARD_API_PID=$!
echo -e "${GREEN}✓ Dashboard API started (PID: $DASHBOARD_API_PID)${NC}"

# Wait a moment for the API to start
sleep 2

# Verify API health
if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dashboard API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Dashboard API health check inconclusive (may still be starting)${NC}"
fi

# ============================================
# Step 3: Start Frontend
# ============================================
echo -e "\n${BLUE}🎨 Step 3: Starting Dashboard Frontend${NC}"

# Check if frontend exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Frontend directory not found${NC}"
    echo "Please ensure frontend/ directory exists"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend
echo "Starting Frontend..."
cd frontend

# Use npm run dev which will open in browser
npm run dev > /tmp/dashboard-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

cd ..

# ============================================
# Display Status
# ============================================
echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All Services Started Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}\n"

echo -e "${BLUE}📍 Service URLs:${NC}"
echo -e "   Frontend:      ${GREEN}http://localhost:3000${NC}"
echo -e "   Dashboard API: ${GREEN}http://localhost:8000${NC}"
echo -e "   Piddy Core:    ${GREEN}http://localhost:8000${NC}\n"

echo -e "${BLUE}📋 Service Info:${NC}"
echo -e "   Frontend PID:       ${FRONTEND_PID}"
echo -e "   Dashboard API PID:  ${DASHBOARD_API_PID}"
echo -e "   Piddy Core PID:     ${PIDDY_PID}\n"

echo -e "${BLUE}📝 Log Files:${NC}"
echo -e "   Frontend:      /tmp/dashboard-frontend.log"
echo -e "   Dashboard API: /tmp/dashboard-api.log"
echo -e "   Piddy Core:    /tmp/piddy-core.log\n"

echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   - Frontend should open automatically in your browser"
echo -e "   - Press Ctrl+C to stop all services"
echo -e "   - Check log files for any errors"
echo -e "   - Visit frontend URL in browser if not opened automatically\n"

echo -e "${BLUE}🚀 Dashboard is ready! Monitor your Piddy system in real-time.${NC}\n"

# ============================================
# Keep script running and monitor services
# ============================================
echo -e "${BLUE}🔄 Monitoring services (Press Ctrl+C to stop)...${NC}"

while true; do
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}✗ Frontend has stopped${NC}"
        echo "Restarting frontend..."
        cd frontend
        npm run dev > /tmp/dashboard-frontend.log 2>&1 &
        FRONTEND_PID=$!
        cd ..
    fi
    
    # Check if dashboard API is still running
    if ! kill -0 $DASHBOARD_API_PID 2>/dev/null; then
        echo -e "${RED}✗ Dashboard API has stopped${NC}"
        echo "Restarting dashboard API..."
        python src/dashboard_api.py > /tmp/dashboard-api.log 2>&1 &
        DASHBOARD_API_PID=$!
    fi
    
    sleep 5
done
