"""
Knowledge Indexer - Manage knowledge base lifecycle

Handles:
- Loading documents from disk
- Building indexes
- Updating indexes when files change
- Providing search interface
- Managing cache
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from src.knowledge_base.loader import DocumentLoader, Document
from src.knowledge_base.retriever import KnowledgeRetriever, SearchResult

logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """Manage knowledge base indexing and retrieval"""
    
    def __init__(self, knowledge_base_dir: str = "./knowledge_base"):
        self.kb_dir = Path(knowledge_base_dir)
        self.loader = DocumentLoader(knowledge_base_dir)
        self.retriever = KnowledgeRetriever()
        self.file_hashes = {}
        self.last_indexed = None
        
        # Load existing index if available
        self._load_cache()
    
    def build_index(self, force: bool = False) -> Dict:
        """
        Build knowledge base index
        
        Args:
            force: Force rebuild even if cache is valid
        
        Returns:
            Index metadata
        """
        logger.info("🔨 Building knowledge base index...")
        
        # Load documents
        documents = self.loader.load_all_documents()
        
        if not documents:
            logger.warning("⚠️ No documents found in knowledge base")
            return {'total_documents': 0, 'indexed': False}
        
        # Index documents with retriever
        self.retriever.index_documents(documents)
        
        # Save cache
        self._save_cache(documents)
        self.last_indexed = datetime.now()
        
        # Return metadata
        summary = self.retriever.get_summary()
        summary['indexed_at'] = self.last_indexed.isoformat()
        
        logger.info(f"✅ Index complete: {len(documents)} documents")
        logger.info(f"   Types: {summary['by_type']}")
        
        return summary
    
    def search(self, query: str, top_k: int = 5, min_relevance: float = 0.3) -> List[SearchResult]:
        """
        Search knowledge base for relevant information
        
        Args:
            query: Search query
            top_k: Return top K results
            min_relevance: Minimum relevance threshold (0-1)
        
        Returns:
            List of SearchResult sorted by relevance
        """
        if not self.retriever.documents:
            logger.info("📚 Knowledge base not indexed yet, building index...")
            self.build_index()
        
        results = self.retriever.search(query, top_k=top_k, threshold=min_relevance)
        
        if results:
            logger.info(f"🔍 Found {len(results)} relevant documents for: '{query}'")
        else:
            logger.info(f"❌ No relevant documents found for: '{query}'")
        
        return results
    
    def search_for_answer(self, question: str, context: str = "") -> Optional[str]:
        """
        Search for answer to a question in knowledge base
        
        Args:
            question: The question to answer
            context: Optional context about the issue
        
        Returns:
            Best answer from knowledge base or None
        """
        # Combine question and context for better search
        search_query = f"{question} {context}".strip()
        
        results = self.search(search_query, top_k=3, min_relevance=0.25)
        
        if not results:
            return None
        
        # Return content from most relevant result
        best_result = results[0]
        
        answer = f"""
📚 Found in: {best_result.filename} ({best_result.source_type})
Relevance: {best_result.relevance_score:.1%}

{best_result.content[:1000]}
{'...' if len(best_result.content) > 1000 else ''}
""".strip()
        
        return answer
    
    def add_document(self, file_path: str = None, doc: Document = None) -> bool:
        """Add a new document to knowledge base
        
        Args:
            file_path: Path to file to add (legacy)
            doc: Document object to add (new)
        """
        try:
            if doc is not None:
                # Add Document object directly
                self.retriever.documents.append(doc)
                logger.debug(f"✅ Added document chunk: {doc.filename}")
                return True
            
            elif file_path is not None:
                # Legacy: Add from file path
                file_path = Path(file_path)
                
                if not file_path.exists():
                    logger.error(f"❌ File not found: {file_path}")
                    return False
                
                # Copy to knowledge base
                dest = self.kb_dir / file_path.name
                
                with open(file_path, 'rb') as src:
                    with open(dest, 'wb') as dst:
                        dst.write(src.read())
                
                logger.info(f"✅ Added document: {file_path.name}")
                
                # Rebuild index
                self.build_index(force=True)
                return True
            else:
                logger.error("❌ Must provide either file_path or doc")
                return False
        
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if not self.retriever.documents:
            return {'status': 'empty', 'documents': 0}
        
        summary = self.retriever.get_summary()
        summary['status'] = 'indexed'
        summary['last_indexed'] = self.last_indexed.isoformat() if self.last_indexed else None
        
        return summary
    
    def _save_cache(self, documents: List[Document]) -> None:
        """Save document cache to disk"""
        cache_path = self.kb_dir / ".cache.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'document_count': len(documents),
            'documents': [doc.to_dict() for doc in documents]
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, default=str)
            logger.debug(f"💾 Saved cache to {cache_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save cache: {e}")
    
    def _load_cache(self) -> bool:
        """Load document cache from disk if available"""
        cache_path = self.kb_dir / ".cache.json"
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            logger.info(f"📖 Using cached knowledge base ({cache_data['document_count']} documents)")
            return True
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cache: {e}")
            return False
    
    def print_stats(self) -> None:
        """Print knowledge base statistics nicely"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📚 KNOWLEDGE BASE STATISTICS")
        print("="*60)
        
        if stats['status'] == 'empty':
            print("Status: EMPTY (no documents)")
        else:
            print(f"Status: {stats['status'].upper()}")
            print(f"Total Documents: {stats['total_documents']}")
            
            if 'by_type' in stats and stats['by_type']:
                print(f"\nBy Type:")
                for type_, count in stats['by_type'].items():
                    print(f"  - {type_}: {count}")
            
            if 'by_file' in stats and stats['by_file']:
                print(f"\nBy File:")
                for file_, count in list(stats['by_file'].items())[:10]:
                    print(f"  - {file_}: {count} chunks")
            
            if 'by_section' in stats and stats['by_section']:
                print(f"\nBy Section:")
                for section, count in list(stats['by_section'].items())[:5]:
                    print(f"  - {section}: {count}")
            
            if 'last_indexed' in stats:
                print(f"\nLast Indexed: {stats['last_indexed']}")
        
        print("="*60 + "\n")


# Global indexer instance
_indexer: Optional[KnowledgeIndexer] = None


def get_indexer(kb_dir: str = "./knowledge_base") -> KnowledgeIndexer:
    """Get or create global indexer instance"""
    global _indexer
    
    if _indexer is None:
        _indexer = KnowledgeIndexer(kb_dir)
        _indexer.build_index()
    
    return _indexer


def search_knowledge_base(query: str, top_k: int = 5) -> List[SearchResult]:
    """Convenience function to search knowledge base"""
    indexer = get_indexer()
    return indexer.search(query, top_k=top_k)


def get_kb_indexer(kb_dir: str = "./knowledge_base") -> KnowledgeIndexer:
    """Get or create KB indexer instance (alias for get_indexer)"""
    return get_indexer(kb_dir)


def find_answer(question: str, context: str = "") -> Optional[str]:
    """Convenience function to find answer in knowledge base"""
    indexer = get_indexer()
    return indexer.search_for_answer(question, context)
