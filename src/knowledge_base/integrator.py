"""
Knowledge Base Integration - Extend Tier 1 Healing

Integrates knowledge base search into the local healing pipeline.
Knowledge base is checked FIRST before pattern matching to reduce API calls.
"""

import logging
from typing import Optional, Dict, List
from src.knowledge_base.indexer import KnowledgeIndexer, get_indexer, search_knowledge_base, find_answer

logger = logging.getLogger(__name__)


class KnowledgeBaseHealer:
    """Integrate knowledge base into Tier 1 healing"""
    
    def __init__(self, kb_dir: str = "./knowledge_base"):
        self.indexer = None
        self.kb_dir = kb_dir
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize knowledge base"""
        try:
            logger.info("🔧 Initializing knowledge base integration...")
            self.indexer = get_indexer(self.kb_dir)
            logger.info("✅ Knowledge base ready for queries")
        except Exception as e:
            logger.warning(f"⚠️ Knowledge base initialization failed: {e}")
    
    def try_heal_from_knowledge(self, error_message: str, context: str = "") -> Optional[Dict]:
        """
        Try to heal an error using knowledge base
        
        This is called BEFORE pattern matching or LLM APIs to reduce cost.
        
        Args:
            error_message: The error or issue to solve
            context: Additional context about the problem
        
        Returns:
            Healing dict with solution or None if not found
        """
        if not self.indexer:
            return None
        
        try:
            logger.info(f"🔍 Searching knowledge base for: {error_message[:50]}...")
            
            # Search knowledge base
            results = self.indexer.search(error_message, top_k=3, min_relevance=0.25)
            
            if not results:
                logger.debug("❌ No knowledge base results")
                return None
            
            best_result = results[0]
            
            # Check if relevance is high enough
            if best_result.relevance_score < 0.35:
                logger.debug(f"⚠️ Low relevance score: {best_result.relevance_score:.1%}")
                return None
            
            logger.info(f"✅ Found knowledge base answer (relevance: {best_result.relevance_score:.1%})")
            
            return {
                'source': 'knowledge_base',
                'file': best_result.filename,
                'section': best_result.section,
                'relevance': best_result.relevance_score,
                'solution': best_result.content[:2000],  # First 2000 chars
                'full_content_length': len(best_result.content),
                'type': best_result.source_type
            }
        
        except Exception as e:
            logger.warning(f"⚠️ Knowledge base search failed: {e}")
            return None
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search knowledge base and return results as dicts"""
        if not self.indexer:
            return []
        
        try:
            results = self.indexer.search(query, top_k=top_k)
            return [
                {
                    'file': r.filename,
                    'source_type': r.source_type,
                    'section': r.section,
                    'relevance': r.relevance_score,
                    'content': r.content[:1000]  # Summarize for display
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if not self.indexer:
            return {'status': 'uninitialized'}
        
        return self.indexer.get_stats()
    
    def add_document(self, file_path: str) -> bool:
        """Add document to knowledge base"""
        if not self.indexer:
            return False
        
        return self.indexer.add_document(file_path)


# Global instance
_kb_healer: Optional[KnowledgeBaseHealer] = None


def get_kb_healer() -> KnowledgeBaseHealer:
    """Get or create KB healer instance"""
    global _kb_healer
    
    if _kb_healer is None:
        _kb_healer = KnowledgeBaseHealer()
    
    return _kb_healer


def heal_with_knowledge(error: str, context: str = "") -> Optional[Dict]:
    """Convenience function to try healing with knowledge base"""
    healer = get_kb_healer()
    return healer.try_heal_from_knowledge(error, context)
