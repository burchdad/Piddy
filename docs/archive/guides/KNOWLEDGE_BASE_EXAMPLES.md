# Knowledge Base - Quick Examples

## Example 1: Setup and First Search

```python
#!/usr/bin/env python3
"""Setup knowledge base and perform first search"""

from src.knowledge_base import get_indexer

# Initialize indexer (loads or builds index)
indexer = get_indexer()

# Show what's indexed
indexer.print_stats()

# Search for something
results = indexer.search("naming conventions Python", top_k=5)

if results:
    print(f"\n✅ Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.filename}")
        print(f"   Relevance: {result.relevance_score:.1%}")
        print(f"   Section: {result.section}")
        print(f"   Preview: {result.content[:200]}...\n")
else:
    print("❌ No results found")
```

## Example 2: Add Your Own Books

```python
#!/usr/bin/env python3
"""Add documentation to knowledge base"""

from src.knowledge_base import get_indexer
from pathlib import Path

indexer = get_indexer()

# Add individual books
books_to_add = [
    "~/Downloads/Clean_Code.pdf",
    "~/Downloads/Python_Best_Practices.txt",
    "~/Documents/team_standards.md"
]

for book_path in books_to_add:
    book = Path(book_path).expanduser()
    if book.exists():
        print(f"📚 Adding: {book.name}")
        success = indexer.add_document(str(book))
        if success:
            print(f"   ✅ Added successfully")
        else:
            print(f"   ❌ Failed to add")
    else:
        print(f"⚠️ File not found: {book_path}")

# Show updated statistics
print("\n" + "="*60)
indexer.print_stats()
```

## Example 3: Research a Topic

```python
#!/usr/bin/env python3
"""Research a topic in your knowledge base"""

from src.knowledge_base import search_knowledge_base

# Research different topics
topics = [
    "error handling best practices",
    "async/await patterns",
    "API design",
    "unit testing",
]

for topic in topics:
    print(f"\n{'='*60}")
    print(f"🔍 Researching: {topic}")
    print('='*60)
    
    results = search_knowledge_base(topic, top_k=3)
    
    if not results:
        print("❌ No results found")
        continue
    
    for i, result in enumerate(results, 1):
        print(f"\n#{i} {result.filename}")
        print(f"   Type: {result.source_type}")
        print(f"   Section: {result.section or 'N/A'}")
        print(f"   Relevance: {result.relevance_score:.1%}")
        print(f"\n   Content:\n   {result.content[:400]}")
        if len(result.content) > 400:
            print("   ...")
```

## Example 4: Solve a Problem Using KB

```python
#!/usr/bin/env python3
"""Use knowledge base to solve a coding problem"""

from src.knowledge_base import find_answer

# Ask different questions
questions = [
    "How should we structure a REST API endpoint?",
    "What are the best practices for error handling in Python?",
    "How do we implement dependency injection?",
]

for question in questions:
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    
    answer = find_answer(question)
    
    if answer:
        print(answer)
    else:
        print("❌ No relevant information found in knowledge base")
    
    print()
```

## Example 5: Integration with Agent

```python
#!/usr/bin/env python3
"""Use knowledge base within an agent's problem-solving"""

from src.knowledge_base import heal_with_knowledge

async def solve_with_knowledge(error: str, context: str = ""):
    """Try to solve error using knowledge base first"""
    
    print(f"\n🔧 Attempting to solve error...")
    print(f"   Error: {error[:100]}...")
    
    # Try knowledge base first (free)
    result = heal_with_knowledge(error, context)
    
    if result:
        print(f"\n✅ Found solution in knowledge base!")
        print(f"   Source: {result['file']}")
        print(f"   Type: {result['type']}")
        print(f"   Relevance: {result['relevance']:.1%}")
        print(f"\n   Solution:\n{result['solution']}")
        return result
    
    print(f"❌ No solution in knowledge base")
    print(f"   Would fall back to Claude API...")
    return None

# Example errors
errors = [
    "TypeError: cannot concatenate 'str' and 'int'",
    "ValueError: invalid literal for int() with base 10",
    "KeyError: 'username' not found",
]

for error in errors:
    await solve_with_knowledge(error)
```

## Example 6: Monitor KB Usage Impact

```python
#!/usr/bin/env python3
"""Monitor how knowledge base is reducing API costs"""

from src.knowledge_base import get_indexer
from src.tiered_healing_engine import token_tracker

def show_kb_impact():
    """Display knowledge base impact on API costs"""
    
    indexer = get_indexer()
    stats = indexer.get_stats()
    
    print("\n" + "="*60)
    print("📊 KNOWLEDGE BASE IMPACT ANALYSIS")
    print("="*60)
    
    # Show what's indexed
    if stats['status'] == 'indexed':
        doc_count = stats['total_documents']
        print(f"\n📚 Active Knowledge Base")
        print(f"   Documents: {doc_count:,} chunks")
        print(f"   Types: {', '.join([f\"{k}({v})\" for k,v in stats['by_type'].items()])}")
    else:
        print(f"\n⚠️ Knowledge Base Status: {stats['status']}")
        return
    
    # Show cost impact
    print(f"\n💰 Estimated Cost Impact (Monthly)")
    print(f"   Without KB:")
    print(f"   - 100 queries → ~500 API calls (avg)")
    print(f"   - Claude: 500 × $0.003 = $1.50")
    print(f"")
    print(f"   With KB (80% KB hit rate):")
    print(f"   - 100 queries → 20 API calls")
    print(f"   - Claude: 20 × $0.003 = $0.06")
    print(f"   - SAVINGS: $1.44/month")
    print(f"")
    print(f"   Scale to 1000 queries: SAVINGS $14.40/month")
    
    print("\n" + "="*60)

show_kb_impact()
```

## Example 7: Setup Automated Indexing

```python
#!/usr/bin/env python3
"""Automatically index knowledge base on startup"""

import logging
from src.knowledge_base import get_indexer

logging.basicConfig(level=logging.INFO)

def setup_knowledge_base():
    """Initialize knowledge base when system starts"""
    
    print("🚀 Piddy Startup - Knowledge Base Setup")
    print("="*60)
    
    # Get or create indexer
    indexer = get_indexer()
    
    # Check if index exists and is fresh
    stats = indexer.get_stats()
    
    if stats['status'] == 'empty':
        print("\n⚠️ Knowledge base is empty")
        print("   Add books to: /knowledge_base/books/")
        print("   Add standards to: /knowledge_base/standards/")
        print("   Add patterns to: /knowledge_base/patterns/")
    else:
        print(f"\n✅ Knowledge base ready")
        print(f"   Documents: {stats['total_documents']:,}")
        print(f"   Indexed at: {stats['last_indexed']}")
    
    print("\n" + "="*60)
    return indexer

# Run on system startup
kb = setup_knowledge_base()

# Proceed with normal operations...
print("\n✅ System ready with knowledge base integration")
```

## Example 8: Search and Format Results

```python
#!/usr/bin/env python3
"""Advanced search with formatted results"""

from src.knowledge_base import search_knowledge_base
from tabulate import tabulate

def search_and_display(query: str):
    """Search and display results in table format"""
    
    results = search_knowledge_base(query, top_k=10)
    
    if not results:
        print(f"❌ No results for: {query}")
        return
    
    # Format for table
    table_data = []
    for i, result in enumerate(results, 1):
        table_data.append([
            i,
            result.filename,
            f"{result.relevance_score:.1%}",
            result.source_type,
            result.section or "N/A",
            result.content[:50] + "..."
        ])
    
    headers = ["#", "File", "Relevance", "Type", "Section", "Preview"]
    
    print(f"\n🔍 Results for: '{query}'")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Show top result details
    top = results[0]
    print(f"\n📌 Top Result Details:")
    print(f"   File: {top.filename}")
    print(f"   Relevance: {top.relevance_score:.1%}")
    print(f"   Content Length: {len(top.content)} characters")
    print(f"\n   Full Content:\n{top.content}")

# Example
search_and_display("REST API patterns Python")
```

## Example 9: Batch Processing

```python
#!/usr/bin/env python3
"""Process multiple questions and save results"""

from src.knowledge_base import search_knowledge_base
import json
from datetime import datetime

def batch_research(questions: list, output_file: str = "research_results.json"):
    """Research multiple questions and save results"""
    
    results = {}
    
    for question in questions:
        print(f"🔍 Researching: {question}")
        
        kb_results = search_knowledge_base(question, top_k=3)
        
        results[question] = {
            'query_time': datetime.now().isoformat(),
            'found': len(kb_results) > 0,
            'results': [
                {
                    'file': r.filename,
                    'relevance': r.relevance_score,
                    'section': r.section,
                    'content': r.content[:500]
                }
                for r in kb_results
            ]
        }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Research complete - saved to {output_file}")
    return results

# Example batch research
questions = [
    "API error handling best practices",
    "Database connection pooling",
    "Caching strategies for performance",
    "Security considerations for REST APIs",
]

batch_research(questions)
```

## Example 10: Check KB Health

```python
#!/usr/bin/env python3
"""Monitor knowledge base health and performance"""

from src.knowledge_base import get_indexer
import time

def check_kb_health():
    """Perform health checks on knowledge base"""
    
    indexer = get_indexer()
    
    print("\n" + "="*60)
    print("🏥 KNOWLEDGE BASE HEALTH CHECK")
    print("="*60)
    
    # 1. Statistics
    stats = indexer.get_stats()
    print(f"\n📊 Statistics")
    print(f"   Status: {stats['status']}")
    if stats['status'] == 'indexed':
        print(f"   Total Documents: {stats['total_documents']:,}")
        print(f"   Document Types: {len(stats['by_type'])}")
    
    # 2. Performance Test
    print(f"\n⚡ Performance Test")
    
    test_queries = [
        "error handling",
        "API design",
        "testing strategies"
    ]
    
    times = []
    for query in test_queries:
        start = time.time()
        results = indexer.search(query, top_k=5)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"   '{query}': {elapsed*1000:.1f}ms ({len(results)} results)")
    
    avg_time = sum(times) / len(times)
    print(f"   Average: {avg_time*1000:.1f}ms")
    
    # 3. Recommendations
    print(f"\n💡 Recommendations")
    if stats['status'] == 'empty':
        print(f"   ⚠️ Add documentation to knowledge base")
    elif stats['total_documents'] < 100:
        print(f"   💼 Consider adding more documentation")
    else:
        print(f"   ✅ Good coverage")
    
    if avg_time > 0.5:
        print(f"   ⚠️ Search performance could be improved")
    else:
        print(f"   ✅ Search performance is good")
    
    print("\n" + "="*60)

check_kb_health()
```

---

## Running These Examples

```bash
# Go to Piddy root
cd /workspaces/Piddy

# Run any example
python3 -m examples.kb_setup_and_search
python3 -m examples.kb_add_books
python3 -m examples.kb_research_topic

# Or run directly with Python
python3 << 'EOF'
from src.knowledge_base import get_indexer
indexer = get_indexer()
indexer.print_stats()
EOF
```

---

**Note**: All examples assume Piddy is properly installed. See `KNOWLEDGE_BASE_SETUP.md` for initial setup instructions.
