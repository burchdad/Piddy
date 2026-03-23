#!/bin/bash
# Piddy Service Management Script
# Manages Piddy background service with easy commands

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"
SERVICE_NAME="piddy"
LOG_FILE="${PROJECT_DIR}/.piddy_service.log"
STATUS_FILE="${PROJECT_DIR}/.piddy_service_status.json"

# Ensure virtual environment is active
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_DIR${NC}"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Load environment
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env from .env.example with your credentials"
    exit 1
fi

# Function to print status
print_status() {
    if [ -f "$STATUS_FILE" ]; then
        echo -e "${BLUE}📊 Service Status:${NC}"
        cat "$STATUS_FILE" | grep -E "status|uptime|messages" | head -5
    fi
}

# Command handling
case "${1:-help}" in
    start)
        echo -e "${BLUE}🚀 Starting Piddy background service...${NC}"
        source "${VENV_DIR}/bin/activate"
        cd "$PROJECT_DIR"
        python -m src.service.background_runner start > "$LOG_FILE" 2>&1 &
        PID=$!
        echo -e "${GREEN}✅ Piddy started (PID: $PID)${NC}"
        echo "📝 View logs: tail -f $LOG_FILE"
        ;;
    
    stop)
        echo -e "${BLUE}🛑 Stopping Piddy service...${NC}"
        if pgrep -f "src.service.background_runner" > /dev/null; then
            pkill -f "src.service.background_runner" || true
            sleep 2
            echo -e "${GREEN}✅ Piddy stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  Piddy is not running${NC}"
        fi
        ;;
    
    restart)
        echo -e "${BLUE}🔄 Restarting Piddy service...${NC}"
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo -e "${BLUE}📊 Checking Piddy service status...${NC}"
        if pgrep -f "src.service.background_runner" > /dev/null; then
            echo -e "${GREEN}✅ Piddy is running${NC}"
            print_status
        else
            echo -e "${RED}❌ Piddy is not running${NC}"
        fi
        ;;
    
    logs)
        echo -e "${BLUE}📝 Piddy service logs:${NC}"
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo -e "${YELLOW}⚠️  No logs found yet${NC}"
        fi
        ;;
    
    check)
        echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
        source "${VENV_DIR}/bin/activate"
        cd "$PROJECT_DIR"
        python -m src.service.background_runner check
        ;;
    
    install-service)
        echo -e "${BLUE}📦 Installing systemd service...${NC}"
        if [ ! -f "/etc/systemd/system/piddy.service" ]; then
            sudo cp "${PROJECT_DIR}/piddy.service" /etc/systemd/system/
            sudo systemctl daemon-reload
            echo -e "${GREEN}✅ Service installed${NC}"
            echo "Enable with: sudo systemctl enable piddy@\$USER"
            echo "Start with: sudo systemctl start piddy@\$USER"
        else
            echo -e "${YELLOW}⚠️  Service already installed${NC}"
        fi
        ;;
    
    uninstall-service)
        echo -e "${BLUE}📦 Uninstalling systemd service...${NC}"
        sudo systemctl stop "piddy@$USER" 2>/dev/null || true
        sudo systemctl disable "piddy@$USER" 2>/dev/null || true
        sudo rm -f /etc/systemd/system/piddy.service
        sudo systemctl daemon-reload
        echo -e "${GREEN}✅ Service uninstalled${NC}"
        ;;
    
    *)
        echo -e "${BLUE}Piddy Service Management${NC}"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo -e "  ${GREEN}start${NC}            - Start Piddy background service"
        echo -e "  ${GREEN}stop${NC}             - Stop Piddy service"
        echo -e "  ${GREEN}restart${NC}          - Restart Piddy service"
        echo -e "  ${GREEN}status${NC}           - Check service status"
        echo -e "  ${GREEN}logs${NC}             - View live service logs"
        echo -e "  ${GREEN}check${NC}            - Verify prerequisites"
        echo -e "  ${GREEN}install-service${NC}  - Install systemd service (Linux)"
        echo -e "  ${GREEN}uninstall-service${NC} - Remove systemd service (Linux)"
        echo ""
        echo "Examples:"
        echo "  # Start Piddy in background"
        echo "  $0 start"
        echo ""
        echo "  # Check if running"
        echo "  $0 status"
        echo ""
        echo "  # View live logs"
        echo "  $0 logs"
        echo ""
        echo "  # Install as systemd service (auto-start on boot)"
        echo "  $0 install-service"
        echo ""
        exit 1
        ;;
esac
