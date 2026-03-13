"""
Automated content ingestion pipeline.
Orchestrates downloading, extracting, chunking, and indexing books.
"""

import json
import logging
import asyncio
import time
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import os

from src.kb.content_extractor import ContentExtractor, DownloadManager, ExtractedDocument
from src.kb.intelligent_chunker import IntelligentChunker, Chunk

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates the full ingestion pipeline:
    1. Download books from index
    2. Extract content
    3. Intelligently chunk
    4. Index into KB
    """
    
    def __init__(self, kb_dir: str = "burchdad-knowledge-base",
                 cache_dir: str = "kb_content_cache",
                 index_file: Optional[str] = None):
        """
        Initialize the ingestion pipeline.
        
        Args:
            kb_dir: Knowledge base repository directory
            cache_dir: Cache directory for downloaded content
            index_file: Path to free-programming-books index file
        """
        self.kb_dir = Path(kb_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.extractor = ContentExtractor(str(cache_dir))
        self.chunker = IntelligentChunker()
        self.download_manager = DownloadManager(str(cache_dir))
        
        # Find index file
        if index_file:
            self.index_file = Path(index_file)
        else:
            # Look for index in KB repo
            self.index_file = self.kb_dir / "books" / "free-programming-books-subjects.md"
            if not self.index_file.exists():
                self.index_file = self.kb_dir / "books" / "free-programming-books-langs.md"
        
        # Progress tracking
        self.progress_file = self.cache_dir / "ingestion_progress.json"
        self.progress = self._load_progress()
        self.stats = {
            'downloaded': 0,
            'extracted': 0,
            'chunked': 0,
            'failed': 0,
            'total_chunks': 0,
            'total_chars': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _load_progress(self) -> Dict:
        """Load progress from previous runs."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'processed': [], 'failed': []}
    
    def _save_progress(self):
        """Save progress for resumability."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def ingest(self, max_books: Optional[int] = 10,
              categories: Optional[List[str]] = None,
              skip_existing: bool = True) -> Dict:
        """
        Run the full ingestion pipeline.
        
        Args:
            max_books: Maximum number of books to process
            categories: Specific categories to ingest (if None, use all)
            skip_existing: Skip already processed books
            
        Returns:
            Statistics about ingestion
        """
        self.stats['start_time'] = datetime.now().isoformat()
        
        try:
            logger.info("🚀 Starting content ingestion pipeline...")
            
            # Step 1: Parse index
            logger.info(f"📖 Reading index: {self.index_file}")
            books = self._parse_index(skip_existing, categories)
            
            if not books:
                logger.warning("⚠️ No books found in index")
                return self.stats
            
            # Limit to max_books
            if max_books:
                books = books[:max_books]
            
            logger.info(f"📚 Found {len(books)} books to process")
            
            # Step 2: Download and extract
            logger.info("📥 Downloading and extracting books...")
            extracted_docs = self._download_and_extract(books)
            
            # Step 3: Chunk
            logger.info("🔪 Chunking documents...")
            all_chunks = self._chunk_documents(extracted_docs)
            
            # Step 4: Save chunks
            logger.info("💾 Saving chunks...")
            self._save_chunks(all_chunks)
            
            # Step 5: Index into KB
            logger.info("📇 Indexing chunks into KB...")
            self._index_chunks(all_chunks)
            
            self.stats['end_time'] = datetime.now().isoformat()
            self._save_progress()
            
            logger.info("\n" + "="*60)
            logger.info("✅ INGESTION COMPLETE")
            logger.info("="*60)
            self._print_stats()
            
            return self.stats
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise
    
    def _parse_index(self, skip_existing: bool = True,
                    categories: Optional[List[str]] = None) -> List[Dict]:
        """Parse the index file and extract book links."""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            books = self.download_manager.parse_index_file(str(self.index_file))
            
            # Filter by categories if specified
            if categories:
                books = [b for b in books if any(cat in b['title'] for cat in categories)]
            
            # Skip already processed
            if skip_existing:
                processed_urls = set(self.progress.get('processed', []))
                books = [b for b in books if b['url'] not in processed_urls]
            
            # Filter out certain domains (too risky or slow)
            skip_domains = ['github.com/downloads', 'archive.org', 'books.google.com']
            books = [b for b in books if not any(d in b['url'] for d in skip_domains)]
            
            return books
        
        except Exception as e:
            logger.error(f"❌ Error parsing index: {e}")
            return []
    
    def _download_and_extract(self, books: List[Dict]) -> List[ExtractedDocument]:
        """Download and extract books."""
        extracted = []
        
        for i, book in enumerate(books, 1):
            logger.info(f"\n[{i}/{len(books)}] 📖 {book['title']}")
            
            try:
                doc = self.extractor.extract_from_url(book['url'], book['title'])
                
                if doc:
                    # Validate content
                    if len(doc.content) > 500:
                        extracted.append(doc)
                        self.progress['processed'].append(book['url'])
                        self.stats['extracted'] += 1
                        logger.info(f"   ✅ Extracted: {len(doc.content):,} chars")
                    else:
                        logger.warning(f"   ⚠️ Content too small: {len(doc.content)} chars")
                        self.progress['failed'].append(book['url'])
                        self.stats['failed'] += 1
                else:
                    logger.warning(f"   ❌ Extraction failed")
                    self.progress['failed'].append(book['url'])
                    self.stats['failed'] += 1
                
                self.stats['downloaded'] += 1
            
            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                self.progress['failed'].append(book['url'])
                self.stats['failed'] += 1
        
        logger.info(f"\n📊 Extracted: {self.stats['extracted']}/{self.stats['downloaded']}")
        return extracted
    
    def _chunk_documents(self, documents: List[ExtractedDocument]) -> List[Chunk]:
        """Chunk all documents using intelligent chunking."""
        all_chunks = []
        
        for doc in documents:
            logger.info(f"🔪 Chunking: {doc.title}")
            
            chunks = self.chunker.chunk(doc.content, doc.title, doc.source_url)
            all_chunks.extend(chunks)
            
            self.stats['chunked'] += 1
            self.stats['total_chunks'] += len(chunks)
            self.stats['total_chars'] += len(doc.content)
            
            logger.info(f"   → {len(chunks)} chunks from {len(doc.content):,} chars")
        
        return all_chunks
    
    def _save_chunks(self, chunks: List[Chunk]):
        """Save chunks to files for inspection and backup."""
        chunks_dir = self.cache_dir / "extracted_chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        # Save as JSONL for easy processing
        chunks_file = chunks_dir / f"chunks_{int(time.time())}.jsonl"
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                json_obj = {
                    'chunk_id': chunk.chunk_id,
                    'title': chunk.source_title,
                    'section': chunk.section,
                    'content': chunk.text[:500],  # Preview
                    'chars': len(chunk.text),
                    'type': chunk.content_type,
                    'full_path': str(chunks_dir / f"{chunk.chunk_id}.txt")
                }
                f.write(json.dumps(json_obj) + '\n')
                
                # Save full chunk to file
                chunk_file = chunks_dir / f"{chunk.chunk_id}.txt"
                with open(chunk_file, 'w', encoding='utf-8') as cf:
                    cf.write(chunk.text)
        
        logger.info(f"💾 Saved {len(chunks)} chunks to {chunks_file}")
    
    def _index_chunks(self, chunks: List[Chunk]):
        """
        Index chunks into the knowledge base system.
        This integrates with Piddy's existing KB indexing.
        """
        try:
            from src.knowledge_base.indexer import get_kb_indexer
            from src.knowledge_base.loader import Document
            
            indexer = get_kb_indexer()
            
            # Convert chunks to Document objects
            indexed_count = 0
            for chunk in chunks:
                # Create Document from Chunk
                doc = Document(
                    id=chunk.chunk_id,
                    filename=chunk.source_title,
                    content=chunk.text,
                    source_type=chunk.content_type,
                    section=chunk.section,
                    metadata={
                        'source': chunk.source_title,
                        'subsection': chunk.subsection,
                        'start_line': chunk.start_line,
                        'end_line': chunk.end_line,
                        **chunk.metadata
                    }
                )
                
                # Add document to indexer
                if indexer.add_document(doc=doc):
                    indexed_count += 1
            
            logger.info(f"📇 Indexed {indexed_count}/{len(chunks)} chunks into KB")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not index chunks: {e}")
    
    def _print_stats(self):
        """Print ingestion statistics."""
        duration = "unknown"
        if self.stats['start_time'] and self.stats['end_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            end = datetime.fromisoformat(self.stats['end_time'])
            duration = str(end - start)
        
        print(f"""
📊 INGESTION STATISTICS
{'='*50}
Duration:        {duration}
Downloaded:      {self.stats['downloaded']} URLs
Extracted:       {self.stats['extracted']} documents
Failed:          {self.stats['failed']} documents
Chunked:         {self.stats['chunked']} documents
Total Chunks:    {self.stats['total_chunks']:,} chunks
Total Content:   {self.stats['total_chars']:,} characters
Avg Chunk Size:  {self.stats['total_chars'] // max(self.stats['total_chunks'], 1):,} chars
{'='*50}
""")


class SelectiveIngestion:
    """
    Selective ingestion for testing and category-based loading.
    """
    
    # Recommended training categories (50-100 books each)
    PRIORITY_CATEGORIES = {
        'web_development': [
            'React', 'Vue', 'Angular', 'Frontend', 'JavaScript',
            'HTML', 'CSS', 'Web Development'
        ],
        'backend': [
            'Python', 'Node.js', 'FastAPI', 'Django', 'Flask',
            'Java', 'Go', 'Rust', 'APIs'
        ],
        'databases': [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Database',
            'SQL', 'Queries'
        ],
        'devops': [
            'Docker', 'Kubernetes', 'CI/CD', 'DevOps', 'AWS',
            'Cloud', 'Infrastructure'
        ],
        'architecture': [
            'Design Patterns', 'Architecture', 'Microservices',
            'System Design', 'Enterprise'
        ],
    }
    
    @staticmethod
    def ingest_category(category: str, max_books: int = 20) -> Dict:
        """
        Ingest a specific category of books.
        
        Args:
            category: Category name (from PRIORITY_CATEGORIES)
            max_books: Maximum books to download
            
        Returns:
            Statistics
        """
        if category not in SelectiveIngestion.PRIORITY_CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        
        keywords = SelectiveIngestion.PRIORITY_CATEGORIES[category]
        pipeline = IngestionPipeline()
        
        logger.info(f"📚 Ingesting {category} ({len(keywords)} keywords)")
        logger.info(f"   Keywords: {', '.join(keywords)}")
        
        return pipeline.ingest(max_books=max_books, categories=keywords)
    
    @staticmethod
    def quick_test(num_books: int = 5) -> Dict:
        """Quick test ingestion with just a few books."""
        logger.info(f"🧪 Quick test: ingesting {num_books} books")
        pipeline = IngestionPipeline()
        return pipeline.ingest(max_books=num_books)
