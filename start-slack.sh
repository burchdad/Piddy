#!/bin/bash

# Piddy Slack Quick Start
# This script helps you get Piddy running with Slack integration

set -e

echo "🚀 Piddy Slack Integration Setup"
echo "================================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "✅ Virtual environment ready"
echo ""

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}

echo "✅ Virtual environment activated"
echo ""

# Check dependencies
if ! pip list | grep -q "fastapi"; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt -q
fi

echo "✅ Dependencies installed"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found!"
    echo ""
    echo "Please create .env with:"
    echo ""
    echo "# Required for Slack"
    echo "SLACK_BOT_TOKEN=xoxb-your-token"
    echo "SLACK_APP_TOKEN=xapp-1-your-token"
    echo "SLACK_SIGNING_SECRET=your-secret"
    echo ""
    echo "# Required for Claude"
    echo "ANTHROPIC_API_KEY=sk-ant-your-key"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Configuration loaded"
echo ""

# Verify required environment variables
required_vars=("SLACK_BOT_TOKEN" "SLACK_APP_TOKEN" "ANTHROPIC_API_KEY")

for var in "${required_vars[@]}"; do
    value=$(grep "^${var}=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ -z "$value" ] || [ "$value" = "your-token" ] || [ "$value" = "your-key" ] || [ "$value" = "your-secret" ]; then
        echo "❌ Missing or invalid ${var} in .env"
        exit 1
    fi
    echo "✅ ${var} configured"
done

echo ""
echo "🎉 All checks passed!"
echo ""
echo "Starting Piddy with Slack integration..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Piddy
python -m src.main
