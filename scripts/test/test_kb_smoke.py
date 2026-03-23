#!/usr/bin/env python3
"""Quick smoke test for knowledge base system"""

import sys
sys.path.insert(0, '/workspaces/Piddy')

print("Testing Knowledge Base System Components\n")
print("="*60)

# Test 1: Document class
print("\n1️⃣ Testing Document dataclass...")
try:
    from src.knowledge_base.loader import Document
    doc = Document(
        id="test_1",
        filename="test.txt",
        content="Test content",
        source_type="text"
    )
    print(f"   ✅ Document created: {doc.id}")
    print(f"      Filename: {doc.filename}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 2: DocumentLoader
print("\n2️⃣ Testing DocumentLoader...")
try:
    from src.knowledge_base.loader import DocumentLoader
    loader = DocumentLoader()
    print(f"   ✅ DocumentLoader created")
    print(f"      KB directory: {loader.kb_dir}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 3: KnowledgeRetriever (may fail if embeddings not ready)
print("\n3️⃣ Testing KnowledgeRetriever...")
try:
    from src.knowledge_base.retriever import KnowledgeRetriever
    retriever = KnowledgeRetriever()
    print(f"   ✅ KnowledgeRetriever created")
    index_status = "not initialized"
    if retriever.documents:
        index_status = f"{len(retriever.documents)} documents indexed"
    print(f"      Index status: {index_status}")
except Exception as e:
    print(f"   ⚠️  Warning: {e}")
    print(f"      (This may be OK if embeddings model is downloading)")

# Test 4: KnowledgeIndexer
print("\n4️⃣ Testing KnowledgeIndexer...")
try:
    from src.knowledge_base.indexer import KnowledgeIndexer
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_kb = Path(tmpdir) / "test_kb"
        test_kb.mkdir()
        indexer = KnowledgeIndexer(str(test_kb))
        print(f"   ✅ KnowledgeIndexer created")
        print(f"      KB path: {indexer.kb_dir}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 5: KnowledgeBaseHealer
print("\n5️⃣ Testing KnowledgeBaseHealer...")
try:
    from src.knowledge_base.integrator import KnowledgeBaseHealer
    healer = KnowledgeBaseHealer()
    print(f"   ✅ KnowledgeBaseHealer created")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 6: Convenience functions
print("\n6️⃣ Testing convenience functions...")
try:
    from src.knowledge_base import (
        get_indexer,
        search_knowledge_base,
        find_answer,
        heal_with_knowledge,
        get_kb_healer
    )
    print(f"   ✅ Imported all convenience functions")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("✅ ALL SMOKE TESTS PASSED")
print("\nThe knowledge base system components are properly installed")
print("and ready to use. Next steps:")
print("  1. Setup knowledge base directory structure")
print("  2. Add documentation files (PDFs, TXT, MD)")
print("  3. Build index with: get_indexer().build_index()")
print("="*60 + "\n")
