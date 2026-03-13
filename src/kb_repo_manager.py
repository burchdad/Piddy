#!/usr/bin/env python3
"""
Knowledge Base Repository Manager

Manages cloning, syncing, and loading knowledge base from a private GitHub repo.
This keeps Piddy lean while maintaining access to 4000+ programming books.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeBaseRepo:
    """Manage knowledge base from separate GitHub repository"""
    
    def __init__(self, kb_repo_url: str = None, local_cache_dir: str = "./knowledge_base_cache"):
        """
        Initialize KB repo manager
        
        Args:
            kb_repo_url: GitHub repo URL (e.g., https://github.com/yourusername/piddy-knowledge-base.git)
            local_cache_dir: Local directory to cache KB repo
        """
        self.kb_repo_url = kb_repo_url or os.getenv('PIDDY_KB_REPO_URL')
        self.local_cache = Path(local_cache_dir)
        self.metadata_file = self.local_cache / ".sync_metadata.json"
        
        if not self.kb_repo_url:
            logger.warning("⚠️ PIDDY_KB_REPO_URL not set - KB repo sync disabled")
            logger.info("   Set with: export PIDDY_KB_REPO_URL='https://github.com/youruser/piddy-knowledge-base.git'")
    
    def clone_or_sync(self, force: bool = False) -> bool:
        """
        Clone KB repo if not present, otherwise sync latest changes
        
        Args:
            force: Force re-download even if cached
        
        Returns:
            True if successful
        """
        if not self.kb_repo_url:
            logger.info("ℹ️ KB repo URL not configured, skipping sync")
            return False
        
        # Check if already cloned
        repo_dir = self.local_cache / "repo"
        
        if repo_dir.exists() and not force:
            logger.info(f"📦 KB cache exists, syncing updates...")
            return self._sync_existing()
        
        if force or not repo_dir.exists():
            logger.info(f"📥 Cloning KB repo...")
            return self._clone_fresh()
        
        return True
    
    def _clone_fresh(self) -> bool:
        """Clone the knowledge base repo from GitHub"""
        try:
            repo_dir = self.local_cache / "repo"
            
            # Remove if exists (force re-clone)
            if repo_dir.exists():
                import shutil
                shutil.rmtree(repo_dir)
            
            self.local_cache.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"   Cloning from: {self.kb_repo_url}")
            
            result = subprocess.run(
                ['git', 'clone', self.kb_repo_url, str(repo_dir)],
                capture_output=True,
                timeout=300,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Clone failed: {result.stderr}")
                return False
            
            logger.info(f"✅ KB repo cloned successfully")
            self._save_metadata()
            return True
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Clone timeout (too large)")
            return False
        except Exception as e:
            logger.error(f"❌ Clone failed: {e}")
            return False
    
    def _sync_existing(self) -> bool:
        """Sync existing KB repo with latest from GitHub"""
        try:
            repo_dir = self.local_cache / "repo"
            
            logger.info(f"   Syncing from: {self.kb_repo_url}")
            
            # Change to repo and pull
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=str(repo_dir),
                capture_output=True,
                timeout=60,
                text=True
            )
            
            if "Already up to date" in result.stdout:
                logger.info("✅ KB already up to date")
            elif result.returncode == 0:
                logger.info("✅ KB synced with latest")
            else:
                logger.warning(f"⚠️ Sync warning: {result.stderr}")
            
            self._save_metadata()
            return True
        
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            return False
    
    def get_kb_documents(self) -> Path:
        """
        Get the KB documents directory
        
        Returns:
            Path to KB docs (repo/books, repo/standards, etc.)
        """
        repo_dir = self.local_cache / "repo"
        
        if not repo_dir.exists():
            logger.warning(f"⚠️ KB repo not found at {repo_dir}")
            logger.info("   Run: kb_repo.clone_or_sync() first")
            return None
        
        return repo_dir
    
    def load_into_knowledge_base(self) -> bool:
        """
        Load KB repo documents into Piddy's knowledge base
        
        Returns:
            True if successful
        """
        kb_docs = self.get_kb_documents()
        if not kb_docs:
            return False
        
        logger.info(f"📚 Loading KB documents into Piddy...")
        
        try:
            from src.knowledge_base import DocumentLoader, get_indexer
            
            # Load documents from repo
            loader = DocumentLoader(str(kb_docs))
            docs = loader.load_all_documents()
            
            if not docs:
                logger.warning("⚠️ No documents found in KB repo")
                return False
            
            logger.info(f"✅ Loaded {len(docs)} document chunks from KB repo")
            
            # Index documents
            logger.info("🔨 Indexing documents...")
            indexer = get_indexer()
            indexer.retriever.index_documents(docs)
            
            logger.info(f"✅ Indexed successfully")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to load KB: {e}")
            return False
    
    def get_cache_size(self) -> str:
        """Get total cache size in human-readable format"""
        total = 0
        
        if self.local_cache.exists():
            for path in self.local_cache.rglob('*'):
                if path.is_file():
                    total += path.stat().st_size
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024:
                return f"{total:.1f} {unit}"
            total /= 1024
        
        return f"{total:.1f} TB"
    
    def get_status(self) -> dict:
        """Get KB sync status"""
        repo_dir = self.local_cache / "repo"
        
        status = {
            'configured': bool(self.kb_repo_url),
            'cloned': repo_dir.exists(),
            'cache_size': self.get_cache_size(),
            'url': self.kb_repo_url,
            'cache_dir': str(self.local_cache)
        }
        
        # Read metadata if available
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    status['metadata'] = json.load(f)
            except:
                pass
        
        return status
    
    def _save_metadata(self) -> None:
        """Save sync metadata"""
        metadata = {
            'synced_at': datetime.now().isoformat(),
            'url': self.kb_repo_url,
            'cache_size': self.get_cache_size()
        }
        
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except:
            pass
    
    def print_status(self) -> None:
        """Print KB status nicely"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("📚 KNOWLEDGE BASE REPOSITORY STATUS")
        print("="*60)
        
        if not status['configured']:
            print("⚠️ KB repository not configured")
            print("\nSetup Instructions:")
            print("1. Create private repo: https://github.com/new")
            print("   Name: piddy-knowledge-base")
            print("2. Push your books/standards to it")
            print("3. Set environment variable:")
            print("   export PIDDY_KB_REPO_URL='https://github.com/youruser/piddy-knowledge-base.git'")
            print("4. Run: piddy_kb_repo.clone_or_sync()")
        else:
            print(f"URL: {status['url']}")
            print(f"Cloned: {'✅ Yes' if status['cloned'] else '❌ No'}")
            print(f"Cache Size: {status['cache_size']}")
            print(f"Cache Dir: {status['cache_dir']}")
            
            if 'metadata' in status and 'synced_at' in status['metadata']:
                print(f"Last Synced: {status['metadata']['synced_at']}")
        
        print("="*60 + "\n")


# Global instance
_kb_repo_manager = None


def get_kb_repo_manager(kb_url: str = None) -> KnowledgeBaseRepo:
    """Get or create KB repo manager"""
    global _kb_repo_manager
    
    if _kb_repo_manager is None:
        _kb_repo_manager = KnowledgeBaseRepo(kb_url)
    
    return _kb_repo_manager


def setup_kb_repo(kb_url: str) -> bool:
    """
    Setup and sync knowledge base repository
    
    Args:
        kb_url: GitHub repo URL
    
    Returns:
        True if successful
    """
    logger.info("🔧 Setting up Knowledge Base Repository...")
    
    # Create manager
    manager = get_kb_repo_manager(kb_url)
    
    # Clone/sync
    if not manager.clone_or_sync():
        logger.error("❌ Failed to setup KB repository")
        return False
    
    # Load into KB
    if not manager.load_into_knowledge_base():
        logger.error("❌ Failed to load KB into system")
        return False
    
    # Show status
    manager.print_status()
    
    return True


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        kb_url = sys.argv[1]
        setup_kb_repo(kb_url)
    else:
        # Check if env var is set
        kb_url = os.getenv('PIDDY_KB_REPO_URL')
        if kb_url:
            setup_kb_repo(kb_url)
        else:
            print("Usage: python3 kb_repo_manager.py <github-repo-url>")
            print("or set PIDDY_KB_REPO_URL environment variable")
