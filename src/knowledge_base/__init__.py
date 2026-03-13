"""
Knowledge Base System for Piddy

Enables offline learning from coding books, standards, and best practices.
Integrates with Tier 1 healing to search knowledge base before using Claude/OpenAI.
"""

from src.knowledge_base.loader import DocumentLoader, Document
from src.knowledge_base.retriever import KnowledgeRetriever, SearchResult
from src.knowledge_base.indexer import KnowledgeIndexer, get_indexer, search_knowledge_base, find_answer
from src.knowledge_base.integrator import KnowledgeBaseHealer, get_kb_healer, heal_with_knowledge

__all__ = [
    # Loader
    'DocumentLoader',
    'Document',
    
    # Retriever
    'KnowledgeRetriever',
    'SearchResult',
    
    # Indexer
    'KnowledgeIndexer',
    'get_indexer',
    'search_knowledge_base',
    'find_answer',
    
    # Integrator (Tier 1 healing)
    'KnowledgeBaseHealer',
    'get_kb_healer',
    'heal_with_knowledge',
]
