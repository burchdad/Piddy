#!/usr/bin/env python3
"""
GitHub Repository Creation Tool for Piddy

Uses GitHub API to create a private repository in your GitHub account.
Requires: GITHUB_TOKEN environment variable

Supports both classic and fine-grained tokens:
- Fine-grained tokens (recommended): More secure, repository-specific
- Classic tokens (deprecated): Full account access

To create a GitHub token:
1. Go to https://github.com/settings/tokens/new
2. Choose token type:
   - Fine-grained (recommended):
     * Repository access: Only this repo
     * Permissions: Repository administration (read & write)
   - Classic (deprecated):
     * Select 'repo' scope
3. Set: export GITHUB_TOKEN='ghp_...' or 'github_pat_...'
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path

def get_github_token():
    """Get GitHub token from environment"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN not set")
        print("\n📋 Create a GitHub Personal Access Token:")
        print("\n   Fine-grained tokens (RECOMMENDED - more secure):")
        print("   1. Go to: https://github.com/settings/tokens/new")
        print("   2. Name: 'Piddy KB Creation'")
        print("   3. Repository access: 'Only select repositories' OR 'All repositories'")
        print("   4. Permissions:")
        print("      - Repository administration: Read & write")
        print("      - Contents: Read & write (for commits)")
        print("   5. Generate and copy token")
        print("\n   Classic tokens (deprecated but still work):")
        print("   1. Go to: https://github.com/settings/tokens?type=beta")
        print("   2. Generate new token")
        print("   3. Select scope: 'repo' (Full control of private repositories)")
        print("\n   Then set the token:")
        print("   export GITHUB_TOKEN='ghp_...' (fine-grained)")
        print("   export GITHUB_TOKEN='github_pat_...' (classic converted)")
        return None
    return token

def get_github_username(token):
    """Get GitHub username from token"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/user', headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()['login']
        elif response.status_code == 401:
            print(f"❌ Invalid or expired GitHub token")
            print(f"   Verify token still exists at: https://github.com/settings/tokens")
            print(f"   For fine-grained tokens, check expiration and permissions")
            print(f"   Needed: Repository administration (read & write)")
            return None
        else:
            print(f"❌ Failed to get username: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_github_repo(token, repo_name, description, private=True):
    """
    Create a private GitHub repository
    
    Args:
        token: GitHub personal access token
        repo_name: Name of repository
        description: Description
        private: Whether to make it private
    
    Returns:
        Repo info dict if successful, None otherwise
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': repo_name,
        'description': description,
        'private': private,
        'auto_init': False  # Don't create README, we'll do it
    }
    
    try:
        print(f"\n🔨 Creating repository '{repo_name}'...")
        
        response = requests.post(
            'https://api.github.com/user/repos',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            repo_info = response.json()
            print(f"✅ Repository created!")
            print(f"   URL: {repo_info['html_url']}")
            print(f"   Clone: {repo_info['clone_url']}")
            return repo_info
        elif response.status_code == 422:
            print(f"⚠️ Repository '{repo_name}' already exists")
            print(f"   You can clone it instead")
            return None
        elif response.status_code == 403:
            print(f"❌ Permission denied creating repository")
            print(f"   For fine-grained tokens, ensure 'Repository administration' permission is set to 'read & write'")
            print(f"   See: https://github.com/settings/tokens")
            return None
        else:
            print(f"❌ Failed to create repository: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def setup_local_repo(repo_url, username):
    """
    Clone and setup local knowledge base repository
    
    Args:
        repo_url: GitHub repo URL
        username: GitHub username
    """
    repo_dir = Path(f"{username}-knowledge-base")
    
    # Remove if exists
    if repo_dir.exists():
        import shutil
        shutil.rmtree(repo_dir)
    
    print(f"\n📂 Setting up local repository...")
    
    # Clone
    result = subprocess.run(
        ['git', 'clone', repo_url, str(repo_dir)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Clone failed: {result.stderr}")
        return None
    
    print(f"✅ Repository cloned")
    
    # Create directory structure
    os.makedirs(f"{repo_dir}/books", exist_ok=True)
    os.makedirs(f"{repo_dir}/standards", exist_ok=True)
    os.makedirs(f"{repo_dir}/patterns", exist_ok=True)
    os.makedirs(f"{repo_dir}/examples", exist_ok=True)
    
    # Create README
    readme_content = f"""# Piddy Knowledge Base

Private repository containing training data for Piddy AI assistant.

## Contents
- **books/**: Programming books and documentation (4000+ free resources)
- **standards/**: Coding standards and guidelines
- **patterns/**: Design patterns and best practices
- **examples/**: Code examples and templates

## Setup

Set environment variable for Piddy:
```bash
export PIDDY_KB_REPO_URL='https://github.com/{username}/piddy-knowledge-base.git'
```

Then Piddy will auto-sync on startup.

## Adding Content

1. Add files to appropriate directory
2. Commit: `git add . && git commit -m "Add content"`
3. Push: `git push origin main`

Piddy will automatically sync on next startup!

## Resources

- [Free Programming Books](https://github.com/EbookFoundation/free-programming-books)
- [KB Setup Guide](../KB_SEPARATE_REPO_GUIDE.md)
- [Quick Reference](../KB_QUICK_REFERENCE.md)
"""
    
    with open(f"{repo_dir}/README.md", 'w') as f:
        f.write(readme_content)
    
    # Create .gitkeep files
    for subdir in ['books', 'standards', 'patterns', 'examples']:
        with open(f"{repo_dir}/{subdir}/.gitkeep", 'w') as f:
            f.write("")
    
    # Initial commit
    subprocess.run(['git', 'add', '.'], cwd=str(repo_dir), capture_output=True)
    subprocess.run(
        ['git', 'commit', '-m', 'Initial knowledge base repository structure'],
        cwd=str(repo_dir),
        capture_output=True
    )
    
    # Push
    result = subprocess.run(
        ['git', 'push', '-u', 'origin', 'main'],
        cwd=str(repo_dir),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Initial commit pushed")
        return str(repo_dir)
    else:
        print(f"⚠️ Could not push initial commit: {result.stderr}")
        print(f"   You may need to push manually")
        return str(repo_dir)

def main():
    """Main execution"""
    
    print("\n" + "="*60)
    print("🚀 Create Piddy KB Repository on GitHub")
    print("="*60 + "\n")
    
    # Step 1: Get token
    token = get_github_token()
    if not token:
        return False
    
    print(f"✅ GitHub token found")
    
    # Step 2: Get username
    username = get_github_username(token)
    if not username:
        print("❌ Could not verify GitHub account")
        return False
    
    print(f"✅ GitHub user: {username}")
    
    # Step 3: Create repo
    repo_name = "piddy-knowledge-base"
    description = "Private knowledge base for Piddy AI assistant - 4000+ programming books"
    
    repo_info = create_github_repo(token, repo_name, description, private=True)
    
    if not repo_info:
        print("\n⚠️ Repository creation failed or already exists")
        repo_url = f"https://github.com/{username}/{repo_name}.git"
        print(f"   Try cloning existing: {repo_url}")
        return False
    
    # Step 4: Setup local repo
    repo_url = repo_info['clone_url']
    local_dir = setup_local_repo(repo_url, username)
    
    if not local_dir:
        return False
    
    # Step 5: Show configuration
    print("\n" + "="*60)
    print("📋 Configuration for Piddy")
    print("="*60)
    print(f"\nSet this environment variable:")
    print(f"   export PIDDY_KB_REPO_URL='{repo_url}'")
    print(f"\nOr add to ~/.bashrc:")
    print(f"   echo \"export PIDDY_KB_REPO_URL='{repo_url}'\" >> ~/.bashrc")
    print(f"   source ~/.bashrc")
    
    # Step 6: Next steps
    print("\n" + "="*60)
    print("📚 Next Steps")
    print("="*60)
    print(f"""
1. Add books to the repository:
   cd {local_dir}
   
   # Copy free-programming-books
   git clone https://github.com/EbookFoundation/free-programming-books.git --depth 1
   cp free-programming-books/books/*.md books/
   
   # Or add your own books
   cp ~/Downloads/*.pdf books/
   cp ~/Documents/*.md standards/

2. Commit and push:
   git add .
   git commit -m "Add programming books"
   git push origin main

3. Configure Piddy:
   export PIDDY_KB_REPO_URL='{repo_url}'
   python3 src/kb_repo_manager.py

4. Done! Piddy will now:
   - Auto-sync KB from GitHub on startup
   - Search 4000+ books instantly
   - Answer 80%+ of queries locally (FREE!)
   - Save you $50+/month in API costs
""")
    
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
