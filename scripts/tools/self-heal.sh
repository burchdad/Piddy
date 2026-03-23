#!/bin/bash
# Piddy Self-Healing Master Script
# Run: ./self-heal.sh

set -e

ENDPOINT="${ENDPOINT:-http://localhost:8000}"
COLORS=true
VERBOSE=true

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    if [ "$COLORS" = true ]; then
        echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
    else
        echo "[$(date +'%H:%M:%S')] $1"
    fi
}

success() {
    if [ "$COLORS" = true ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo "✅ $1"
    fi
}

error() {
    if [ "$COLORS" = true ]; then
        echo -e "${RED}❌ $1${NC}"
    else
        echo "❌ $1"
    fi
}

warning() {
    if [ "$COLORS" = true ]; then
        echo -e "${YELLOW}⚠️  $1${NC}"
    else
        echo "⚠️  $1"
    fi
}

info() {
    if [ "$COLORS" = true ]; then
        echo -e "${CYAN}ℹ️  $1${NC}"
    else
        echo "ℹ️  $1"
    fi
}

# Check if server is running
check_server() {
    log "Checking if Piddy is running at $ENDPOINT..."
    
    if curl -s "$ENDPOINT/health" > /dev/null 2>&1; then
        success "Server is running ✓"
        return 0
    else
        error "Server is not running at $ENDPOINT"
        error "Start with: python -m uvicorn src.main:app --reload"
        exit 1
    fi
}

# Run audit
audit() {
    log "🔍 Running comprehensive system audit..."
    info "This will check: code quality, security, database, integrations"
    
    response=$(curl -s -X POST "$ENDPOINT/api/self/audit")
    
    total=$(echo "$response" | jq '.total_issues // 0')
    critical=$(echo "$response" | jq '.critical // 0')
    high=$(echo "$response" | jq '.high // 0')
    
    success "Audit complete!"
    info "Issues found: $total (Critical: $critical, High: $high)"
    
    if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.'
    fi
}

# Auto-fix everything
fix_all() {
    log "🤖 AUTONOMOUS SELF-FIX INITIATED..."
    warning "This will:"
    info "  • Remove ALL mock data"
    info "  • Fix code quality issues"
    info "  • Fix security vulnerabilities"
    info "  • Optimize database"
    info "  • Run full test suite"
    info "  • Create PR with all changes"
    
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Cancelled"
        return 1
    fi
    
    response=$(curl -s -X POST "$ENDPOINT/api/self/fix-all")
    
    status=$(echo "$response" | jq -r '.status // "unknown"')
    
    if [ "$status" = "self-fix_complete" ]; then
        success "All fixes applied!"
        info "Next: Review the auto-generated PR on GitHub"
        info "Then: Merge and deploy to production"
    else
        error "Fix process encountered an issue"
    fi
    
    if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.'
    fi
}

# Go live
go_live() {
    log "🚀 GO-LIVE SEQUENCE INITIATED..."
    warning "This will perform COMPLETE system deployment"
    info "Steps:"
    info "  1. Full system audit"
    info "  2. Auto-fix all issues"
    info "  3. Create comprehensive PR"
    info "  4. Mark as production-ready"
    
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Cancelled"
        return 1
    fi
    
    response=$(curl -s -X POST "$ENDPOINT/api/self/go-live")
    
    status=$(echo "$response" | jq -r '.status // "unknown"')
    message=$(echo "$response" | jq -r '.message // ""')
    
    if [ "$status" = "go_live_complete" ]; then
        success "$message"
        success "System is fully operational and live!"
    else
        error "Go-live process encountered an issue"
    fi
    
    if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.'
    fi
}

# Status
status() {
    log "📊 Getting system status..."
    
    response=$(curl -s "$ENDPOINT/api/self/status")
    
    monitoring=$(echo "$response" | jq -r '.monitoring_enabled // false')
    issues=$(echo "$response" | jq '.issues_detected // 0')
    fixed=$(echo "$response" | jq '.issues_fixed // 0')
    
    info "Monitoring: $([ "$monitoring" = "true" ] && echo "🟢 ENABLED" || echo "🔴 DISABLED")"
    info "Issues detected: $issues"
    info "Issues fixed: $fixed"
    
    if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.'
    fi
}

# Main menu
show_menu() {
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  Piddy Autonomous Self-Healing System${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
    echo ""
    echo "1) 🔍 Audit - Scan entire system"
    echo "2) 🔧 Fix-All - Remove mock data and fix everything"
    echo "3) 🚀 Go-Live - Complete go-live deployment"
    echo "4) 📊 Status - Check current system state"
    echo "5) ⚙️  Advanced Options"
    echo "6) ❌ Exit"
    echo ""
    read -p "Choose option (1-6): " choice
}

# Advanced options
advanced_menu() {
    echo ""
    echo "Advanced Options:"
    echo "1) Start monitoring"
    echo "2) Analyze now"
    echo "3) View autonomous status"
    echo "4) Back"
    echo ""
    read -p "Choose option: " choice
}

# Main loop
main() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║ Piddy - Autonomous Self-Healing System    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_server
    
    echo ""
    success "Ready to heal!"
    info "What would you like to do?"
    echo ""
    
    while true; do
        show_menu
        
        case $choice in
            1)
                audit
                ;;
            2)
                fix_all
                ;;
            3)
                go_live
                ;;
            4)
                status
                ;;
            5)
                advanced_menu
                ;;
            6)
                log "Goodbye! 👋"
                exit 0
                ;;
            *)
                error "Invalid option"
                ;;
        esac
    done
}

# Handle command line arguments
case "${1:-}" in
    audit)
        check_server && audit
        ;;
    fix-all)
        check_server && fix_all
        ;;
    go-live)
        check_server && go_live
        ;;
    status)
        check_server && status
        ;;
    *)
        main
        ;;
esac
