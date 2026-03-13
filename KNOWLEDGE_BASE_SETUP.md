# Knowledge Base Setup & Usage Guide

## Overview

The Knowledge Base system enables Piddy to run **completely offline** while learning from your custom documentation, coding standards, and best practices. This eliminates external API costs while maintaining intelligent assistance.

### Architecture

```
┌─────────────────────────────────────────┐
│        Learning & Queries               │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼────────┐    ┌──────▼────────┐
    │ Search KB  │    │ Pattern Match  │
    │ (Tier 1)   │    │ (Tier 1)       │
    └────┬───────┘    └────────┬───────┘
         │                     │
    ┌────▼─────────────────────▼────┐
    │    All Results Cached          │
    │    NO API COSTS               │
    └───────────────────────────────┘
         If needed: Claude (Tier 2)
         Fallback: OpenAI (Tier 3)
```

## Quick Start

### 1. Directory Structure

Create the knowledge base directory structure:

```bash
mkdir -p /workspaces/Piddy/knowledge_base/{books,standards,patterns,examples}
```

The system automatically creates:
- `books/` - Your coding books and documentation
- `standards/` - Team coding standards documents
- `patterns/` - Design patterns and architectural guides
- `examples/` - Code examples and templates

### 2. Add Your Documentation

**Option A: Copy Books to Directory**

```bash
# Copy a PDF
cp ~/Downloads/Clean_Code.pdf /workspaces/Piddy/knowledge_base/books/

# Copy standards document
cp ~/Documents/python_standards.md /workspaces/Piddy/knowledge_base/standards/

# Copy design patterns
cp ~/Documents/design_patterns.txt /workspaces/Piddy/knowledge_base/patterns/
```

**Option B: Use Python API**

```python
from src.knowledge_base import get_indexer

indexer = get_indexer()
indexer.add_document("~/Downloads/System_Design.pdf")  # Auto-copies to KB
```

### 3. Build the Index

The knowledge base automatically indexes on first use. To force rebuild:

```python
from src.knowledge_base import get_indexer

indexer = get_indexer()
indexer.build_index(force=True)
indexer.print_stats()
```

### 4. Search Knowledge Base

**Direct Search:**

```python
from src.knowledge_base import search_knowledge_base

# Search for information
results = search_knowledge_base("how to name variables", top_k=5)

for result in results:
    print(f"📖 {result.filename} (relevance: {result.relevance_score:.1%})")
    print(f"   {result.content[:500]}...\n")
```

**Find Answers:**

```python
from src.knowledge_base import find_answer

answer = find_answer("what's the best way to structure a REST API?")
print(answer)
```

## Supported File Formats

| Format | How It's Processed |
|--------|-------------------|
| **PDF** | Extracted page-by-page (preserves structure) |
| **TXT** | Split into 2000-char chunks with 200-char overlap |
| **MD** | Parsed section-aware by headers |
| **Python** | Docstrings and function definitions extracted |
| **JSON** | Converted to readable text format |

### Example Files

**books/Clean_Code.pdf** (345 pages)
- ✅ PDF auto-extracted into 700+ searchable chunks

**standards/python_guidelines.md**
- ✅ Markdown sections preserved
- ✅ Searchable by section ("Naming Conventions", "Error Handling", etc.)

**patterns/design_patterns.txt**
- ✅ Text chunked intelligently with context overlap
- ✅ Words split across chunks are still searchable

**examples/rest_api.py**
- ✅ Function docstrings extracted
- ✅ Type hints and signatures included

## Integration with Tier 1 Healing

The knowledge base is automatically integrated into Piddy's Tier 1 local healing:

```
Error Occurs
    ↓
KB Healing (FREE - runs locally)
  - Search knowledge base
  - Found answer? → Use it ✅
    ↓
Pattern Matching (FREE - runs locally)
  - Check common patterns
  - Found pattern? → Use it ✅
    ↓
Claude Opus 4.1 (PAID - Tier 2)
  - Only if KB + patterns insufficient
    ↓
OpenAI GPT-4o (PAID - Tier 3)
  - Final fallback only
```

### Cost Impact

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Standard query | Claude API | KB search | 100% |
| Coding question | Claude API | KB + patterns | 95%+ |
| Complex debugging | 1-3 API calls | KB first, then 1 API call | 80%+ |

## API Reference

### Search Knowledge Base

```python
from src.knowledge_base import search_knowledge_base, SearchResult

# Basic search
results = search_knowledge_base("naming conventions")

# Advanced search
results = search_knowledge_base(
    query="REST API best practices",
    top_k=10,              # Return top 10 results
    min_relevance=0.25     # Minimum relevance threshold
)

# Access results
for result in results:
    print(f"File: {result.filename}")              # "Clean_Code.pdf"
    print(f"Type: {result.source_type}")          # "pdf", "markdown", etc.
    print(f"Section: {result.section}")            # "Chapter 3: Functions"
    print(f"Relevance: {result.relevance_score}") # 0.0-1.0 score
    print(f"Content: {result.content}")            # Actual text
```

### Find Answers

```python
from src.knowledge_base import find_answer

# Simple question
answer = find_answer("how should errors be handled?")

# With context
answer = find_answer(
    question="what's the best way to structure this?",
    context="We're using async/await in Python"
)

print(answer)  # Formatted answer with source attribution
```

### Full Index Management

```python
from src.knowledge_base import get_indexer

indexer = get_indexer()

# Build index
stats = indexer.build_index(force=True)
print(stats)  # {'total_documents': 1205, 'indexed_at': '2024-01-15T...'}

# Search
results = indexer.search("pattern matching", top_k=5)

# Add new document
indexer.add_document("~/Downloads/new_book.pdf")

# Get statistics
print(indexer.get_stats())
# {
#     'status': 'indexed',
#     'total_documents': 1205,
#     'by_type': {'pdf': 850, 'markdown': 200, 'text': 155},
#     'by_file': {'Clean_Code.pdf': 352, ...},
#     'by_section': {'Chapter 1': 45, ...}
# }

# Print formatted stats
indexer.print_stats()
```

### Healing Integration

```python
from src.knowledge_base import heal_with_knowledge

# Try to heal an error using knowledge base
healing_result = heal_with_knowledge(
    error="ImportError: No module named 'requests'",
    context="Python REST client"
)

if healing_result:
    print(f"✅ Found solution in: {healing_result['file']}")
    print(f"   Section: {healing_result['section']}")
    print(f"   Relevance: {healing_result['relevance']:.1%}")
    print(f"   Solution: {healing_result['solution']}")
else:
    print("❌ No knowledge base solution found")
```

## Performance Characteristics

### First Run
- **Action**: Initial index build
- **Time**: 2-5 seconds per 100MB of documentation
- **IO**: One disk write of index cache

### Subsequent Runs
- **Action**: Load from cache
- **Time**: <100ms startup
- **Memory**: ~50MB for 1000+ documents

### Search Performance
- **Semantic search**: 50-200ms (with embeddings)
- **Keyword fallback**: 10-50ms (no embeddings needed)
- **Results**: Instant display (already cached)

## Example Workflow

### Step 1: Download and Organize Books

```bash
# Create structure
cd /workspaces/Piddy/knowledge_base

# Download books (your choice)
# Place them in appropriate folders:
# - Clean Code PDF → books/
# - Python PEP 8 → standards/
# - Design Patterns → patterns/

ls -la books/
# Clean_Code.pdf (1.2MB)
# Python_Best_Practices.pdf (2.3MB)
```

### Step 2: Initialize Piddy with Knowledge Base

```python
# Piddy starts up
from src.knowledge_base import get_indexer

indexer = get_indexer()  # Automatically indexes all documents
indexer.print_stats()

# Output:
# ============================================================
# 📚 KNOWLEDGE BASE STATISTICS
# ============================================================
# Status: INDEXED
# Total Documents: 1,205 chunks
#
# By Type:
#   - pdf: 852
#   - markdown: 200
#   - text: 153
#
# By File:
#   - Clean_Code.pdf: 352 chunks
#   - Python_PEP8.pdf: 284 chunks
#   - design_patterns.txt: 189 chunks
#
# Last Indexed: 2024-01-15T10:30:45.123456
# ============================================================
```

### Step 3: Use Piddy Normally

```python
# Any query automatically checks KB first
await agent.process_command("How should I name variables?")

# Behind the scenes:
# 1. Search KB (instant)
# 2. Found: Chapter 2 "Meaningful Names" from Clean Code
# 3. Return answer (NO API COST)
```

### Step 4: Monitor API Usage

```python
from src.tiered_healing_engine import token_tracker

# Check how many tokens were saved
print(f"Queries handled by KB: {token_tracker.kb_queries}")
print(f"Claude API calls avoided: {token_tracker.kb_hits}")
print(f"Estimated savings: ${token_tracker.kb_hits * 0.003:.2f}")
```

## Troubleshooting

### No Documents Found

```python
from src.knowledge_base import get_indexer

indexer = get_indexer()
indexer.build_index(force=True)
indexer.print_stats()  # Check if documents loaded
```

**If still empty:**
- Verify files are in: `/workspaces/Piddy/knowledge_base/books/` and subdirs
- Check file permissions: `ls -la /workspaces/Piddy/knowledge_base/`
- Try manually: `python3 -c "from src.knowledge_base.loader import DocumentLoader; DocumentLoader().load_all_documents()"`

### Low Relevance Scores

- Add more relevant documentation
- Different KB documents match different questions
- Threshold can be lowered if needed: `search(query, min_relevance=0.15)`

### Slow Search Performance

- KB is run locally, speed depends on hardware
- First search loads embeddings (~500ms)
- Subsequent searches faster (<100ms)
- Can use keyword-only mode (no embeddings) for speed

### Out of Memory

- If KB has 10,000+ documents:
  - Consider archiving older docs
  - Split into multiple KB instances
  - Use keyword search (lower memory)

## Next Steps

1. **Download Documentation**
   - Get coding books (PDFs, MD files)
   - Collect team standards
   - Save design patterns

2. **Configure Knowledge Base**
   - Place files in `/knowledge_base/{category}/`
   - Run `indexer.build_index()`
   - Verify with `indexer.print_stats()`

3. **Test Offline Operation**
   - Run Piddy normally
   - Check token usage remains zero
   - Verify KB results are being used

4. **Monitor Cost Savings**
   - Track KB vs API queries
   - Measure token cost reduction
   - Adjust documentation as needed

5. **Optional: Local LLM**
   - For zero API costs even on complex queries
   - Integrate Ollama or LLaMA
   - See: `/docs/LOCAL_LLM_INTEGRATION.md` (coming soon)

## FAQ

**Q: What if I don't have any books yet?**
A: Piddy still works - the KB just stays empty and falls back to normal Claude/OpenAI. Add books anytime.

**Q: Can I use web content?**
A: Yes! Copy web pages as TXT/MD and place in knowledge base. They'll be indexed like any other document.

**Q: How do I know if KB is being used?**
A: Check logs: "✅ Found knowledge base answer" means KB was used successfully.

**Q: Can I remove documents from the KB?**
A: Yes - delete from `/knowledge_base/` and rebuild index with `build_index(force=True)`.

**Q: Will adding more books slow things down?**
A: No - search performance stays constant (~100ms) regardless of KB size due to embeddings indexing.

---

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready
