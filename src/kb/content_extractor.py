"""
Content extraction from various formats (PDF, Markdown, Text, etc.)
Handles downloading and parsing different document types.
"""

import os
import re
import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
import urllib.parse
import tempfile
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDocument:
    """Represents extracted content from a document."""
    title: str
    content: str
    source_url: str
    content_type: str  # "pdf", "markdown", "text", "html"
    file_path: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentExtractor:
    """Extract content from various document formats."""
    
    def __init__(self, cache_dir: str = "kb_content_cache", timeout: int = 30):
        """
        Initialize content extractor.
        
        Args:
            cache_dir: Directory to cache downloaded files
            timeout: HTTP request timeout in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
    
    def extract_from_url(self, url: str, title: Optional[str] = None) -> Optional[ExtractedDocument]:
        """
        Download and extract content from a URL.
        
        Args:
            url: URL to download from
            title: Optional title for the document
            
        Returns:
            ExtractedDocument if successful, None otherwise
        """
        try:
            logger.info(f"📥 Downloading from: {url}")
            
            # Add timeout and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Piddy KB Extractor)'
            }
            
            response = requests.get(url, timeout=self.timeout, headers=headers)
            response.raise_for_status()
            
            # Detect content type
            content_type = response.headers.get('content-type', '').lower()
            
            # Determine format
            if 'pdf' in content_type or url.lower().endswith('.pdf'):
                return self._extract_pdf_from_bytes(
                    response.content,
                    title or self._get_filename_from_url(url),
                    url
                )
            elif 'markdown' in content_type or url.lower().endswith('.md'):
                return ExtractedDocument(
                    title=title or self._get_filename_from_url(url),
                    content=response.text,
                    source_url=url,
                    content_type="markdown"
                )
            elif 'text' in content_type or url.lower().endswith('.txt'):
                return ExtractedDocument(
                    title=title or self._get_filename_from_url(url),
                    content=response.text,
                    source_url=url,
                    content_type="text"
                )
            elif 'html' in content_type:
                return self._extract_from_html(response.text, title or url, url)
            else:
                # Try as text by default
                return ExtractedDocument(
                    title=title or self._get_filename_from_url(url),
                    content=response.text,
                    source_url=url,
                    content_type="text"
                )
                
        except requests.Timeout:
            logger.warning(f"⏱️ Timeout downloading {url}")
            return None
        except requests.RequestException as e:
            logger.warning(f"❌ Failed to download {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error processing {url}: {e}")
            return None
    
    def extract_from_file(self, file_path: str, title: Optional[str] = None) -> Optional[ExtractedDocument]:
        """
        Extract content from a local file.
        
        Args:
            file_path: Path to the file
            title: Optional title for the document
            
        Returns:
            ExtractedDocument if successful, None otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                return None
            
            logger.info(f"📄 Extracting from: {file_path}")
            
            if file_path.suffix.lower() == '.pdf':
                with open(file_path, 'rb') as f:
                    return self._extract_pdf_from_bytes(
                        f.read(),
                        title or file_path.stem,
                        str(file_path)
                    )
            elif file_path.suffix.lower() in ['.md', '.markdown']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return ExtractedDocument(
                        title=title or file_path.stem,
                        content=f.read(),
                        source_url=str(file_path),
                        content_type="markdown",
                        file_path=str(file_path)
                    )
            elif file_path.suffix.lower() in ['.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return ExtractedDocument(
                        title=title or file_path.stem,
                        content=f.read(),
                        source_url=str(file_path),
                        content_type="text",
                        file_path=str(file_path)
                    )
            else:
                logger.warning(f"⚠️ Unsupported file type: {file_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting from {file_path}: {e}")
            return None
    
    def _extract_pdf_from_bytes(self, pdf_bytes: bytes, title: str, source_url: str) -> Optional[ExtractedDocument]:
        """Extract text from PDF bytes."""
        try:
            import pdfplumber
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
            
            try:
                text_content = []
                with pdfplumber.open(tmp_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            # Add page marker for better chunking
                            text_content.append(f"\n\n[Page {page_num}]\n{text}")
                
                if not text_content:
                    logger.warning(f"⚠️ No text extracted from PDF: {title}")
                    return None
                
                return ExtractedDocument(
                    title=title,
                    content="\n".join(text_content),
                    source_url=source_url,
                    content_type="pdf",
                    metadata={
                        "pages": len(pdf.pages) if 'pdf' in locals() else 0,
                        "extraction_method": "pdfplumber"
                    }
                )
            finally:
                os.unlink(tmp_path)
                
        except ImportError:
            logger.warning("⚠️ pdfplumber not installed, skipping PDF extraction")
            return None
        except Exception as e:
            logger.error(f"❌ PDF extraction failed for {title}: {e}")
            return None
    
    def _extract_from_html(self, html_content: str, title: str, source_url: str) -> Optional[ExtractedDocument]:
        """Extract text from HTML content."""
        try:
            from html.parser import HTMLParser
            
            class HTMLTextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.skip_content = False
                
                def handle_starttag(self, tag, attrs):
                    if tag in ['script', 'style', 'nav', 'footer']:
                        self.skip_content = True
                
                def handle_endtag(self, tag):
                    if tag in ['script', 'style', 'nav', 'footer']:
                        self.skip_content = False
                    elif tag in ['p', 'div', 'article', 'section']:
                        self.text.append('\n')
                
                def handle_data(self, data):
                    if not self.skip_content:
                        text = data.strip()
                        if text:
                            self.text.append(text + ' ')
            
            extractor = HTMLTextExtractor()
            extractor.feed(html_content)
            content = ''.join(extractor.text).strip()
            
            if not content or len(content) < 100:
                logger.warning(f"⚠️ Minimal content extracted from HTML: {title}")
                return None
            
            return ExtractedDocument(
                title=title,
                content=content,
                source_url=source_url,
                content_type="html"
            )
        except Exception as e:
            logger.error(f"❌ HTML extraction failed for {title}: {e}")
            return None
    
    @staticmethod
    def _get_filename_from_url(url: str) -> str:
        """Extract filename from URL."""
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path)
        return filename or "document"


class DownloadManager:
    """Manage downloading books from free-programming-books index."""
    
    def __init__(self, cache_dir: str = "kb_content_cache"):
        self.extractor = ContentExtractor(cache_dir)
        self.cache_dir = Path(cache_dir)
        self.downloaded = set()
        self.failed = set()
    
    def parse_index_file(self, index_path: str) -> List[Dict]:
        """
        Parse free-programming-books markdown index file.
        
        Returns list of books with title and URL.
        """
        books = []
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract markdown links: [Title](URL)
            pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            matches = re.findall(pattern, content)
            
            for title, url in matches:
                if url.startswith('http'):
                    books.append({
                        'title': title.strip(),
                        'url': url.strip()
                    })
            
            logger.info(f"📚 Found {len(books)} books in index")
            return books
        
        except Exception as e:
            logger.error(f"❌ Error parsing index: {e}")
            return []
    
    def download_books(self, books: List[Dict], max_books: Optional[int] = None,
                      max_size_mb: int = 50) -> List[ExtractedDocument]:
        """
        Download and extract multiple books.
        
        Args:
            books: List of dicts with 'title' and 'url'
            max_books: Maximum number of books to download
            max_size_mb: Skip files larger than this
            
        Returns:
            List of successfully extracted documents
        """
        extracted = []
        books_to_process = books[:max_books] if max_books else books
        
        for i, book in enumerate(books_to_process, 1):
            logger.info(f"📖 [{i}/{len(books_to_process)}] Processing: {book['title']}")
            
            try:
                doc = self.extractor.extract_from_url(book['url'], book['title'])
                if doc and len(doc.content) > 500:  # Minimum content length
                    extracted.append(doc)
                    self.downloaded.add(book['url'])
                    logger.info(f"✅ Extracted: {book['title']} ({len(doc.content)} chars)")
                else:
                    logger.warning(f"⚠️ Insufficient content: {book['title']}")
                    self.failed.add(book['url'])
            except Exception as e:
                logger.error(f"❌ Failed to process {book['title']}: {e}")
                self.failed.add(book['url'])
        
        logger.info(f"\n📊 Downloaded: {len(self.downloaded)}, Failed: {len(self.failed)}")
        return extracted
