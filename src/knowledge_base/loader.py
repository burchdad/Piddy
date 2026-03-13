"""
Document Loader for Knowledge Base

Loads and parses:
- PDF files (.pdf)
- Plain text files (.txt)
- Markdown files (.md)
- Python files (.py)
- JSON files (.json)

Stores extracted text with metadata (filename, page, section, etc.)
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a loaded document chunk"""
    id: str
    filename: str
    content: str
    source_type: str  # "pdf", "text", "markdown", "code", etc.
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    loaded_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'filename': self.filename,
            'content': self.content,
            'source_type': self.source_type,
            'page_number': self.page_number,
            'section': self.section,
            'metadata': self.metadata,
            'loaded_at': self.loaded_at.isoformat()
        }


class DocumentLoader:
    """Load and parse documents from knowledge base directory"""
    
    def __init__(self, knowledge_base_dir: str = "./knowledge_base"):
        self.kb_dir = Path(knowledge_base_dir)
        self.documents: List[Document] = []
        
        # Ensure directory structure
        self.kb_dir.mkdir(exist_ok=True)
        (self.kb_dir / "books").mkdir(exist_ok=True)
        (self.kb_dir / "standards").mkdir(exist_ok=True)
        (self.kb_dir / "patterns").mkdir(exist_ok=True)
        (self.kb_dir / "examples").mkdir(exist_ok=True)
        
        logger.info(f"📚 Knowledge Base initialized at: {self.kb_dir}")
    
    def load_all_documents(self) -> List[Document]:
        """Load all documents from knowledge base"""
        self.documents = []
        
        for root, dirs, files in os.walk(self.kb_dir):
            for file in files:
                file_path = Path(root) / file
                
                # Skip index files and hidden files
                if file.startswith('.') or file == 'index.json':
                    continue
                
                try:
                    if file.endswith('.pdf'):
                        self._load_pdf(file_path)
                    elif file.endswith('.txt'):
                        self._load_text(file_path)
                    elif file.endswith('.md'):
                        self._load_markdown(file_path)
                    elif file.endswith('.py'):
                        self._load_python(file_path)
                    elif file.endswith('.json'):
                        self._load_json(file_path)
                except Exception as e:
                    logger.error(f"❌ Failed to load {file_path}: {e}")
        
        logger.info(f"✅ Loaded {len(self.documents)} document chunks")
        return self.documents
    
    def _load_pdf(self, file_path: Path) -> None:
        """Load PDF file"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    
                    if text.strip():
                        doc = Document(
                            id=f"{file_path.name}_{page_num}",
                            filename=file_path.name,
                            content=text,
                            source_type="pdf",
                            page_number=page_num,
                            metadata={'total_pages': len(reader.pages)}
                        )
                        self.documents.append(doc)
            
            logger.info(f"📄 Loaded PDF: {file_path.name} ({len(reader.pages)} pages)")
        
        except ImportError:
            logger.warning(f"⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
        except Exception as e:
            logger.error(f"❌ PDF loading failed: {e}")
    
    def _load_text(self, file_path: Path) -> None:
        """Load plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split long text into chunks
            chunks = self._chunk_text(content, chunk_size=2000)
            
            for chunk_num, chunk in enumerate(chunks, 1):
                doc = Document(
                    id=f"{file_path.name}_chunk_{chunk_num}",
                    filename=file_path.name,
                    content=chunk,
                    source_type="text",
                    metadata={'chunk': chunk_num, 'total_chunks': len(chunks)}
                )
                self.documents.append(doc)
            
            logger.info(f"📝 Loaded text: {file_path.name} ({len(chunks)} chunks)")
        
        except Exception as e:
            logger.error(f"❌ Text loading failed: {e}")
    
    def _load_markdown(self, file_path: Path) -> None:
        """Load Markdown file with section awareness"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_section = "Introduction"
            current_content = []
            
            for line in lines:
                # Detect markdown headers
                if line.startswith('#'):
                    # Save previous section
                    if current_content:
                        content = ''.join(current_content).strip()
                        if content:
                            doc = Document(
                                id=f"{file_path.name}_{current_section.replace(' ', '_')}",
                                filename=file_path.name,
                                content=content,
                                source_type="markdown",
                                section=current_section
                            )
                            self.documents.append(doc)
                    
                    # Start new section
                    current_section = line.strip().lstrip('#').strip()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Save final section
            if current_content:
                content = ''.join(current_content).strip()
                if content:
                    doc = Document(
                        id=f"{file_path.name}_{current_section.replace(' ', '_')}",
                        filename=file_path.name,
                        content=content,
                        source_type="markdown",
                        section=current_section
                    )
                    self.documents.append(doc)
            
            logger.info(f"📘 Loaded markdown: {file_path.name}")
        
        except Exception as e:
            logger.error(f"❌ Markdown loading failed: {e}")
    
    def _load_python(self, file_path: Path) -> None:
        """Load Python code files as documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstrings and comments
            sections = self._extract_python_docs(content)
            
            for section_name, section_content in sections.items():
                doc = Document(
                    id=f"{file_path.name}_{section_name}",
                    filename=file_path.name,
                    content=section_content,
                    source_type="code",
                    section=section_name,
                    metadata={'language': 'python'}
                )
                self.documents.append(doc)
            
            logger.info(f"🐍 Loaded Python: {file_path.name}")
        
        except Exception as e:
            logger.error(f"❌ Python loading failed: {e}")
    
    def _load_json(self, file_path: Path) -> None:
        """Load JSON configuration or data files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to readable format
            content = json.dumps(data, indent=2)
            
            doc = Document(
                id=file_path.name,
                filename=file_path.name,
                content=content,
                source_type="json",
                metadata={'lines': len(content.split('\n'))}
            )
            self.documents.append(doc)
            
            logger.info(f"📦 Loaded JSON: {file_path.name}")
        
        except Exception as e:
            logger.error(f"❌ JSON loading failed: {e}")
    
    def _chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _extract_python_docs(self, content: str) -> Dict[str, str]:
        """Extract docstrings and comments from Python code"""
        sections = {}
        lines = content.split('\n')
        
        current_section = "Functions and Classes"
        section_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Collect docstrings and function definitions
            if stripped.startswith('def ') or stripped.startswith('class ') or '"""' in line or "'''" in line:
                section_lines.append(line)
        
        if section_lines:
            sections[current_section] = '\n'.join(section_lines)
        
        return sections
    
    def get_documents_by_type(self, source_type: str) -> List[Document]:
        """Get all documents of a specific type"""
        return [doc for doc in self.documents if doc.source_type == source_type]
    
    def get_documents_by_filename(self, filename: str) -> List[Document]:
        """Get all document chunks from a specific file"""
        return [doc for doc in self.documents if doc.filename == filename]
    
    def save_index(self) -> None:
        """Save document index to JSON for fast loading"""
        index_path = self.kb_dir / "index.json"
        
        index_data = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': len(self.documents),
            'documents': [doc.to_dict() for doc in self.documents]
        }
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"💾 Saved knowledge base index to {index_path}")


def get_document_loader(kb_dir: str = "./knowledge_base") -> DocumentLoader:
    """Get or create document loader instance"""
    return DocumentLoader(kb_dir)
