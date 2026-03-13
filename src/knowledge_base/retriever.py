"""
Knowledge Retriever - Search offline knowledge base

Uses semantic similarity to find relevant documents without external APIs.
Integrates with Tier 1 healing to answer questions from learned knowledge.
"""

import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from knowledge base search"""
    document_id: str
    filename: str
    content: str
    relevance_score: float  # 0.0 to 1.0
    section: Optional[str] = None
    source_type: str = "unknown"


class KnowledgeRetriever:
    """Search and retrieve relevant knowledge from indexed documents"""
    
    def __init__(self, documents: List = None):
        self.documents = documents or []
        self.embeddings = {}
        self.embedder = None
        
        # Try to init embedder
        self._init_embedder()
    
    def _init_embedder(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use lightweight model that works offline
            logger.info("🤖 Loading embedding model (one-time download)...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model ready")
        
        except ImportError:
            logger.warning("⚠️ sentence-transformers not installed")
            logger.warning("   Install with: pip install sentence-transformers")
            self.embedder = None
        except Exception as e:
            logger.error(f"❌ Failed to load embedder: {e}")
            self.embedder = None
    
    def index_documents(self, documents: List) -> None:
        """Create embeddings for all documents"""
        self.documents = documents
        
        if not self.embedder:
            logger.warning("⚠️ Embedder not available, using fallback search")
            return
        
        logger.info(f"🔍 Indexing {len(documents)} document chunks...")
        
        try:
            # Get all document contents
            contents = [doc.content for doc in documents]
            
            # Create embeddings
            self.embeddings = {}
            for i, doc in enumerate(documents):
                embedding = self.embedder.encode(doc.content, convert_to_numpy=True)
                self.embeddings[doc.id] = embedding
            
            logger.info(f"✅ Indexed {len(self.embeddings)} document embeddings")
        
        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.3) -> List[SearchResult]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Return top K results
            threshold: Minimum relevance score (0-1)
        
        Returns:
            List of SearchResult objects sorted by relevance
        """
        if not self.documents:
            logger.warning("⚠️ No documents indexed")
            return []
        
        # Use embeddings if available, else fallback
        if self.embedder and self.embeddings:
            return self._semantic_search(query, top_k, threshold)
        else:
            return self._keyword_search(query, top_k, threshold)
    
    def _semantic_search(self, query: str, top_k: int, threshold: float) -> List[SearchResult]:
        """Search using semantic similarity"""
        try:
            # Encode query
            query_embedding = self.embedder.encode(query, convert_to_numpy=True)
            
            # Calculate similarities
            results = []
            for doc in self.documents:
                if doc.id not in self.embeddings:
                    continue
                
                doc_embedding = self.embeddings[doc.id]
                
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= threshold:
                    results.append(SearchResult(
                        document_id=doc.id,
                        filename=doc.filename,
                        content=doc.content,
                        relevance_score=float(similarity),
                        section=doc.section,
                        source_type=doc.source_type
                    ))
            
            # Sort by relevance and return top K
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int, threshold: float) -> List[SearchResult]:
        """Fallback: keyword-based search"""
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            doc_words = set(doc.content.lower().split())
            
            # Jaccard similarity
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            similarity = intersection / union if union > 0 else 0
            
            if similarity >= threshold:
                results.append(SearchResult(
                    document_id=doc.id,
                    filename=doc.filename,
                    content=doc.content,
                    relevance_score=float(similarity),
                    section=doc.section,
                    source_type=doc.source_type
                ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def search_by_section(self, section: str, query: str = None) -> List[SearchResult]:
        """Search within specific section"""
        section_docs = [doc for doc in self.documents if doc.section == section]
        
        if not section_docs:
            return []
        
        if query:
            # Search within section
            results = []
            for doc in section_docs:
                # Simple relevance based on keyword match
                score = sum(1 for word in query.lower().split() if word in doc.content.lower())
                if score > 0:
                    results.append(SearchResult(
                        document_id=doc.id,
                        filename=doc.filename,
                        content=doc.content,
                        relevance_score=min(1.0, score / len(query.split())),
                        section=doc.section,
                        source_type=doc.source_type
                    ))
            return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        else:
            # Return all from section
            return [SearchResult(
                document_id=doc.id,
                filename=doc.filename,
                content=doc.content,
                relevance_score=1.0,
                section=doc.section,
                source_type=doc.source_type
            ) for doc in section_docs]
    
    def get_summary(self) -> Dict:
        """Get summary of indexed knowledge"""
        by_type = {}
        by_file = {}
        by_section = {}
        
        for doc in self.documents:
            # By type
            by_type[doc.source_type] = by_type.get(doc.source_type, 0) + 1
            
            # By file
            by_file[doc.filename] = by_file.get(doc.filename, 0) + 1
            
            # By section
            if doc.section:
                by_section[doc.section] = by_section.get(doc.section, 0) + 1
        
        return {
            'total_documents': len(self.documents),
            'by_type': by_type,
            'by_file': by_file,
            'by_section': by_section,
            'has_embeddings': len(self.embeddings) > 0
        }


def get_retriever(documents: List = None) -> KnowledgeRetriever:
    """Get or create retriever instance"""
    return KnowledgeRetriever(documents)
