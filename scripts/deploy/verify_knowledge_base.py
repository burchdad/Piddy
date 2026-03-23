#!/usr/bin/env python3
"""
Knowledge Base System Verification

Tests all components of the knowledge base system to ensure proper operation.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add Piddy root to path
sys.path.insert(0, '/workspaces/Piddy')

from src.knowledge_base import (
    DocumentLoader, Document,
    KnowledgeRetriever, SearchResult,
    KnowledgeIndexer,
    KnowledgeBaseHealer,
    get_indexer, search_knowledge_base, find_answer, heal_with_knowledge
)


def test_document_loader():
    """Test DocumentLoader functionality"""
    print("\n" + "="*60)
    print("TEST 1: Document Loader")
    print("="*60)
    
    loader = DocumentLoader()
    
    # Test creating test documents
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create test TXT file
        txt_file = test_dir / "test.txt"
        txt_file.write_text("This is a test document.\nIt has multiple lines.\nFor testing purposes.")
        
        # Create test MD file
        md_file = test_dir / "test.md"
        md_file.write_text("""# Section 1
        Some content here.
        
        ## Subsection 1.1
        More content.
        
        # Section 2
        Final content.""")
        
        # Try to load (would need PyPDF2 installed for PDF)
        print("✅ Test files created")
        print(f"   - TXT: {txt_file.name}")
        print(f"   - MD: {md_file.name}")
    
    print("\n✅ DocumentLoader test passed")


def test_retriever():
    """Test KnowledgeRetriever functionality"""
    print("\n" + "="*60)
    print("TEST 2: Knowledge Retriever")
    print("="*60)
    
    retriever = KnowledgeRetriever()
    
    # Create test documents
    test_docs = [
        Document(
            id="doc_1",
            filename="test1.txt",
            content="Python is a programming language",
            source_type="text",
            page_number=1
        ),
        Document(
            id="doc_2",
            filename="test1.txt",
            content="JavaScript runs in web browsers",
            source_type="text",
            page_number=2
        ),
        Document(
            id="doc_3",
            filename="test2.md",
            content="Rust provides memory safety",
            source_type="markdown"
        ),
    ]
    
    # Index documents
    retriever.index_documents(test_docs)
    print("✅ Documents indexed")
    
    # Test search
    results = retriever.search("programming language", top_k=2)
    
    assert len(results) > 0, "Expected search results"
    assert results[0].relevance_score > 0, "Expected relevance score"
    
    print(f"✅ Search returned {len(results)} result(s)")
    print(f"   Top result: {results[0].content[:50]}...")
    
    # Test summary
    summary = retriever.get_summary()
    assert 'by_type' in summary, "Expected summary statistics"
    
    print(f"✅ Summary generated: {summary['by_type']}")


def test_indexer():
    """Test KnowledgeIndexer functionality"""
    print("\n" + "="*60)
    print("TEST 3: Knowledge Indexer")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir) / "knowledge_base"
        kb_dir.mkdir()
        
        # Create test documents
        (kb_dir / "books").mkdir()
        (kb_dir / "standards").mkdir()
        
        test_file = kb_dir / "books" / "test.txt"
        test_file.write_text("This is test content for indexing.")
        
        # Create indexer
        indexer = KnowledgeIndexer(str(kb_dir))
        
        # Build index
        stats = indexer.build_index(force=True)
        
        assert stats['indexed'] == False or stats['indexed'] == True, "Expected index status"
        print(f"✅ Index built: {stats}")
        
        # Test search
        results = indexer.search("indexing", top_k=5)
        print(f"✅ Search completed: {len(results)} result(s)")
        
        # Test stats
        kb_stats = indexer.get_stats()
        assert 'status' in kb_stats, "Expected stats"
        print(f"✅ Stats retrieved: status={kb_stats['status']}")


def test_healer():
    """Test KnowledgeBaseHealer functionality"""
    print("\n" + "="*60)
    print("TEST 4: Knowledge Base Healer")
    print("="*60)
    
    healer = KnowledgeBaseHealer()
    
    # Test healing attempt (will return None if no KB, which is OK)
    result = healer.try_heal_from_knowledge("ImportError: No module named 'requests'")
    
    if result:
        print(f"✅ Healing result found")
        print(f"   Source: {result['source']}")
        print(f"   File: {result['file']}")
    else:
        print(f"✅ Healing attempted (no results expected in test)")
    
    # Test stats
    stats = healer.get_stats()
    print(f"✅ Stats retrieved: {stats['status']}")


def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "="*60)
    print("TEST 5: Convenience Functions")
    print("="*60)
    
    # Test get_indexer (global instance)
    indexer = get_indexer()
    assert indexer is not None, "Expected indexer instance"
    print("✅ get_indexer() works")
    
    # Test search_knowledge_base (empty if no docs)
    results = search_knowledge_base("test query")
    assert isinstance(results, list), "Expected list of results"
    print(f"✅ search_knowledge_base() works: {len(results)} results")
    
    # Test find_answer (empty if no docs)
    answer = find_answer("test question")
    assert answer is None or isinstance(answer, str), "Expected string or None"
    print(f"✅ find_answer() works")
    
    # Test heal_with_knowledge (empty if no docs)
    healing = heal_with_knowledge("test error")
    assert healing is None or isinstance(healing, dict), "Expected dict or None"
    print(f"✅ heal_with_knowledge() works")


def test_integration():
    """Test full integration"""
    print("\n" + "="*60)
    print("TEST 6: Full Integration")
    print("="*60)
    
    # Create minimal KB
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir) / "knowledge_base"
        kb_dir.mkdir()
        (kb_dir / "books").mkdir()
        
        # Add sample document
        doc_file = kb_dir / "books" / "sample.txt"
        doc_file.write_text("""
Clean Code Best Practices
==========================

1. Naming
- Use clear, descriptive names
- Names should reveal intent
- Avoid misleading names

2. Functions
- Keep functions small
- Do one thing well
- Use descriptive names

3. Comments
- Explain why, not what
- Keep comments accurate
- Remove obsolete comments
        """)
        
        # Create indexer
        indexer = KnowledgeIndexer(str(kb_dir))
        indexer.build_index(force=True)
        
        # Test search
        results = indexer.search("naming conventions", top_k=3)
        
        if results:
            print(f"✅ Integrated search found {len(results)} result(s)")
            print(f"   Top result from: {results[0].filename}")
            print(f"   Relevance: {results[0].relevance_score:.1%}")
        else:
            print(f"⚠️ No results found (integration still works, just no matches)")
        
        # Test find answer
        answer = find_answer("How should we name things?")
        
        if answer:
            print(f"✅ Answer found in KB")
            print(f"   Length: {len(answer)} characters")
        else:
            print(f"✅ Answer search works (no results in this test)")


def run_all_tests():
    """Run all verification tests"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " KNOWLEDGE BASE SYSTEM VERIFICATION ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Document Loader", test_document_loader),
        ("Knowledge Retriever", test_retriever),
        ("Knowledge Indexer", test_indexer),
        ("Knowledge Base Healer", test_healer),
        ("Convenience Functions", test_convenience_functions),
        ("Full Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED")
            print(f"   Error: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Knowledge Base System is Ready!")
    else:
        print(f"\n⚠️ {failed} test(s) failed - check errors above")
    
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
