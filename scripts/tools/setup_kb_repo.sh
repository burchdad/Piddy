#!/bin/bash
# Quick setup for Piddy Knowledge Base as separate GitHub repo

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    Piddy Knowledge Base - Separate Repository Setup             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if user provided username
if [ -z "$1" ]; then
    echo "Usage: ./setup_kb_repo.sh <github-username>"
    echo ""
    echo "This will create and configure a separate KB repository."
    echo "Example:"
    echo "  ./setup_kb_repo.sh yourusername"
    exit 1
fi

USERNAME="$1"
REPO_NAME="piddy-knowledge-base"
REPO_URL="https://github.com/$USERNAME/$REPO_NAME.git"

echo "📋 Setup Configuration:"
echo "   GitHub User: $USERNAME"
echo "   Repository: $REPO_NAME"
echo "   URL: $REPO_URL"
echo ""

# Step 1: Verify git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git first."
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Step 2: Check if repo exists
echo "🔍 Checking if repository exists on GitHub..."
if git ls-remote "$REPO_URL" &> /dev/null; then
    echo "✅ Repository found on GitHub"
    REPO_EXISTS=true
else
    echo "⚠️ Repository not found on GitHub"
    REPO_EXISTS=false
fi

echo ""

# Step 3: Setup local KB repo
echo "📂 Setting up local knowledge base repository..."

KB_DIR="${PWD}/piddy-knowledge-base"

if [ "$REPO_EXISTS" = true ]; then
    echo "   Cloning existing repository..."
    if [ -d "$KB_DIR" ]; then
        echo "   (Directory already exists, skipping clone)"
    else
        git clone "$REPO_URL" "$KB_DIR"
    fi
else
    echo "   Creating new local repository..."
    mkdir -p "$KB_DIR"
    cd "$KB_DIR"
    git init
    
    # Create structure
    mkdir -p {books,standards,patterns,examples}
    
    # Create README
    cat > README.md << 'EOF'
# Piddy Knowledge Base

Private repository containing training data and knowledge for Piddy AI assistant.

## Structure
- **books/**: Programming books and documentation
- **standards/**: Coding standards and guidelines  
- **patterns/**: Design patterns and best practices
- **examples/**: Code examples and templates

## Usage
See: [KB_SEPARATE_REPO_GUIDE.md](../KB_SEPARATE_REPO_GUIDE.md)

## Adding Content
1. Add files to appropriate directory
2. Commit: `git add . && git commit -m "Add content description"`
3. Push: `git push origin main`

Piddy will automatically sync on startup!
EOF

    # Create initial commit
    git add .
    git commit -m "Initial Knowledge Base repository structure"
    
    cd - > /dev/null
    echo "   ✅ Local repository created"
fi

echo "✅ Local KB repository ready at: $KB_DIR"
echo ""

# Step 4: Configuration
echo "⚙️ Configuration Options:"
echo ""
echo "Option 1: Environment Variable (Recommended)"
echo "   Add to ~/.bashrc or ~/.zshrc:"
echo "   export PIDDY_KB_REPO_URL='$REPO_URL'"
echo ""
echo "Option 2: Set for current session:"
echo "   export PIDDY_KB_REPO_URL='$REPO_URL'"
echo ""

# Step 5: Next steps
echo "📋 Next Steps:"
echo ""
echo "If repository doesn't exist on GitHub yet:"
echo "   1. Go to: https://github.com/new"
echo "   2. Create repository '$REPO_NAME' (PRIVATE)"
echo "   3. Run these commands:"
echo "      cd $KB_DIR"
echo "      git remote add origin $REPO_URL"
echo "      git branch -M main"
echo "      git push -u origin main"
echo ""
echo "Add your knowledge to the repository:"
echo "   1. Copy books to: $KB_DIR/books/"
echo "   2. Copy standards to: $KB_DIR/standards/"
echo "   3. Copy patterns to: $KB_DIR/patterns/"
echo "   4. Copy examples to: $KB_DIR/examples/"
echo ""
echo "Commit and push:"
echo "   cd $KB_DIR"
echo "   git add ."
echo "   git commit -m 'Add knowledge base content'"
echo "   git push origin main"
echo ""
echo "Setup Piddy to use the KB:"
echo "   export PIDDY_KB_REPO_URL='$REPO_URL'"
echo "   python3 src/kb_repo_manager.py"
echo ""

echo "✅ Setup complete!"
echo ""
echo "For detailed guide, see: KB_SEPARATE_REPO_GUIDE.md"
echo ""
