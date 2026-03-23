#!/bin/bash
# Create GitHub Knowledge Base Repository with API

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Create Piddy KB Repository on GitHub (Automated)               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN environment variable not set"
    echo ""
    echo "You need to create a GitHub Personal Access Token:"
    echo ""
    echo "Steps:"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Click: 'Generate new token (classic)'"
    echo "  3. Fill in:"
    echo "     - Note: 'Piddy KB Creation'"
    echo "     - Expiration: 90 days (or longer)"
    echo "     - Scopes: Check 'repo' (Full control of private repositories)"
    echo "  4. Click: 'Generate token'"
    echo "  5. COPY the token (you won't see it again!)"
    echo ""
    echo "Then run:"
    echo "  export GITHUB_TOKEN='ghp_xxxxx...'"
    echo "  bash create_kb_repo_auto.sh"
    echo ""
    exit 1
fi

echo "✅ GITHUB_TOKEN is set"
echo ""

# Step 2: Verify token works
echo "🔐 Verifying GitHub token..."

RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USERNAME=$(echo "$RESPONSE" | grep -o '"login":"[^"]*' | cut -d'"' -f4)

if [ -z "$USERNAME" ]; then
    echo "❌ Invalid GitHub token"
    echo ""
    echo "The token might be:"
    echo "  - Expired"
    echo "  - Revoked"
    echo "  - Incorrectly copied"
    echo ""
    echo "Create a new one at: https://github.com/settings/tokens"
    exit 1
fi

echo "✅ Authenticated as: $USERNAME"
echo ""

# Step 3: Run Python script
echo "🚀 Creating repository..."
echo ""

python3 /workspaces/Piddy/create_kb_repo.py

echo ""
echo "✅ Done!"
echo ""
