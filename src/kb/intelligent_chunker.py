"""
Intelligent chunking strategy for technical documents.
Preserves code blocks, sections, and context.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    text: str
    chunk_id: str
    source_title: str
    section: Optional[str] = None
    subsection: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    content_type: str = "text"  # "text", "code", "table", "list"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IntelligentChunker:
    """
    Smart chunking for technical documents.
    
    Strategy:
    - Detect and preserve code blocks
    - Chunk by sections/headers when available
    - Use semantic boundaries (not just character count)
    - Maintain context with smart overlap
    - Different chunk sizes for different content types
    """
    
    # Configuration
    DEFAULT_CHUNK_SIZE = 1000  # tokens, roughly 4k chars
    CODE_CHUNK_SIZE = 500  # Smaller for code blocks
    OVERLAP_RATIO = 0.15  # 15% overlap between chunks
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, 
                 overlap_size: Optional[int] = None):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size or int(chunk_size * self.OVERLAP_RATIO)
    
    def chunk(self, text: str, source_title: str, 
              source_url: Optional[str] = None) -> List[Chunk]:
        """
        Intelligently chunk a document.
        
        Args:
            text: Document text to chunk
            source_title: Title of the document
            source_url: Optional source URL
            
        Returns:
            List of chunks
        """
        chunks = []
        
        try:
            # First, detect and parse document structure
            sections = self._parse_structure(text)
            
            # Process each section
            chunk_id = 0
            for section in sections:
                section_chunks = self._chunk_section(section, source_title)
                for chunk_text, metadata in section_chunks:
                    chunk = Chunk(
                        text=chunk_text,
                        chunk_id=f"{source_title}_{chunk_id}",
                        source_title=source_title,
                        section=metadata.get('section'),
                        subsection=metadata.get('subsection'),
                        content_type=metadata.get('content_type', 'text'),
                        metadata={
                            'source_url': source_url,
                            'line_range': metadata.get('line_range'),
                            **metadata.get('extra', {})
                        }
                    )
                    chunks.append(chunk)
                    chunk_id += 1
            
            logger.info(f"✅ Chunked {source_title}: {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"❌ Chunking failed for {source_title}: {e}")
            # Fallback: simple chunking
            return self._simple_chunk(text, source_title, source_url)
    
    def _parse_structure(self, text: str) -> List[Dict]:
        """
        Parse document structure (headers, sections, code blocks).
        
        Returns list of sections with their content.
        """
        sections = []
        current_section = None
        current_content = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect headers (Markdown-style)
            header_match = re.match(r'^#+\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'header': current_section,
                        'content': '\n'.join(current_content),
                        'lines': (current_section['start'], i - 1)
                    })
                
                level = len(re.match(r'^#+', line).group())
                current_section = {
                    'title': header_match.group(1),
                    'level': level,
                    'start': i
                }
                current_content = [line]
                i += 1
                continue
            
            # Detect code blocks
            if line.strip().startswith('```'):
                # Code block detected
                code_block = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_block.append(lines[i])
                    i += 1
                if i < len(lines):
                    code_block.append(lines[i])  # Closing ```
                    i += 1
                
                current_content.append('\n'.join(code_block))
                continue
            
            current_content.append(line)
            i += 1
        
        # Save last section
        if current_section and current_content:
            sections.append({
                'header': current_section,
                'content': '\n'.join(current_content),
                'lines': (current_section['start'], len(lines) - 1)
            })
        
        return sections if sections else [{'content': text, 'lines': (0, len(lines) - 1)}]
    
    def _chunk_section(self, section: Dict, source_title: str) -> List[Tuple[str, Dict]]:
        """
        Chunk a section intelligently based on its content type.
        
        Returns list of (chunk_text, metadata) tuples.
        """
        content = section.get('content', '')
        
        if not content.strip():
            return []
        
        chunks = []
        
        # Check content type
        if self._is_code_heavy(content):
            # Code-heavy section: smaller chunks, preserve structure
            return self._chunk_code_section(content, section)
        else:
            # Text section: normal chunking
            return self._chunk_text_section(content, section)
    
    def _is_code_heavy(self, content: str) -> bool:
        """Detect if content is mostly code."""
        code_pattern = r'```[\s\S]*?```'
        code_blocks = re.findall(code_pattern, content)
        code_chars = sum(len(block) for block in code_blocks)
        return code_chars / max(len(content), 1) > 0.3
    
    def _chunk_code_section(self, content: str, section: Dict) -> List[Tuple[str, Dict]]:
        """Chunk code-heavy sections preserving code blocks."""
        chunks = []
        code_size = int(self.chunk_size * 0.5)  # Smaller chunks for code
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            chunk_lines = []
            chunk_start = i
            chunk_chars = 0
            
            while i < len(lines) and chunk_chars < code_size:
                line = lines[i]
                chunk_lines.append(line)
                chunk_chars += len(line)
                
                # If we hit a code block boundary, include the whole block
                if line.strip().startswith('```'):
                    chunk_lines.append(lines[i])
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        chunk_lines.append(lines[i])
                        chunk_chars += len(lines[i])
                        i += 1
                    if i < len(lines):
                        chunk_lines.append(lines[i])
                        i += 1
                else:
                    i += 1
            
            if chunk_lines:
                chunk_text = '\n'.join(chunk_lines)
                chunks.append((chunk_text, {
                    'content_type': 'code',
                    'section': section.get('header', {}).get('title'),
                    'line_range': (chunk_start, i - 1),
                    'extra': {'has_code': True}
                }))
        
        return chunks
    
    def _chunk_text_section(self, content: str, section: Dict) -> List[Tuple[str, Dict]]:
        """Chunk regular text sections."""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\n+', content)
        
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_size + para_size > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append((chunk_text, {
                    'content_type': 'text',
                    'section': section.get('header', {}).get('title'),
                    'line_range': None,
                }))
                
                # Add overlap
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1]]
                    current_size = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
        
        # Save final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append((chunk_text, {
                'content_type': 'text',
                'section': section.get('header', {}).get('title'),
                'line_range': None,
            }))
        
        return chunks
    
    def _simple_chunk(self, text: str, source_title: str, 
                     source_url: Optional[str] = None) -> List[Chunk]:
        """Fallback: simple character-based chunking."""
        chunks = []
        lines = text.split('\n')
        
        i = 0
        chunk_id = 0
        
        while i < len(lines):
            chunk_lines = []
            chunk_start = i
            chunk_chars = 0
            
            while i < len(lines) and chunk_chars < self.chunk_size * 4:
                chunk_lines.append(lines[i])
                chunk_chars += len(lines[i])
                i += 1
            
            if chunk_lines:
                chunk_text = '\n'.join(chunk_lines)
                chunk = Chunk(
                    text=chunk_text,
                    chunk_id=f"{source_title}_{chunk_id}",
                    source_title=source_title,
                    start_line=chunk_start,
                    end_line=i - 1,
                    metadata={'source_url': source_url, 'fallback': True}
                )
                chunks.append(chunk)
                chunk_id += 1
        
        logger.info(f"⚠️ Fallback chunking for {source_title}: {len(chunks)} chunks")
        return chunks
