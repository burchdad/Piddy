---
name: knowledge-graph
description: Structured knowledge storage, entity relationships, and agent memory patterns for persistent context
---

# Knowledge Graph & Memory

Design structured memory systems for agents and applications. Store entities, relationships, and context that persists across sessions.

## Entity Model

Core entity types for a knowledge graph:

```
Person     — name, role, contact, skills
Project    — name, status, tech stack, repo
Task       — title, status, assignee, priority, due date
Document   — title, path, type, last modified
Event      — title, date, participants, outcome
Decision   — what, why, date, alternatives considered
Concept    — name, definition, related concepts
```

### Entity Schema

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Entity:
    id: str
    type: str           # person, project, task, etc.
    name: str
    properties: dict    # flexible key-value attributes
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Relationship:
    source_id: str
    target_id: str
    type: str           # owns, works-on, depends-on, etc.
    properties: dict = field(default_factory=dict)
```

## Relationship Types

| Relationship | Example |
|-------------|---------|
| owns | Person → Project |
| works-on | Person → Task |
| depends-on | Task → Task |
| documents | Document → Project |
| decided-in | Decision → Event |
| part-of | Task → Project |
| related-to | Concept → Concept |
| blocks | Task → Task |

## Storage Patterns

### SQLite Graph Store

```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    properties TEXT DEFAULT '{}',  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL REFERENCES entities(id),
    target_id TEXT NOT NULL REFERENCES entities(id),
    type TEXT NOT NULL,
    properties TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rel_source ON relationships(source_id);
CREATE INDEX idx_rel_target ON relationships(target_id);
CREATE INDEX idx_rel_type ON relationships(type);
CREATE INDEX idx_entity_type ON entities(type);
```

### Querying Relationships

```sql
-- Find all tasks for a person
SELECT e.* FROM entities e
JOIN relationships r ON r.target_id = e.id
WHERE r.source_id = 'person_alice'
  AND r.type = 'works-on'
  AND e.type = 'task';

-- Find all dependencies of a task
SELECT e.* FROM entities e
JOIN relationships r ON r.target_id = e.id
WHERE r.source_id = 'task_123'
  AND r.type = 'depends-on';

-- Find connected entities (2 hops)
WITH direct AS (
    SELECT target_id FROM relationships WHERE source_id = ?
)
SELECT DISTINCT e.* FROM entities e
JOIN relationships r ON r.source_id IN (SELECT target_id FROM direct)
WHERE e.id = r.target_id;
```

## Agent Memory Layers

```
┌─────────────────────────────────┐
│  Working Memory (Current Task)  │  ← Context window, immediate state
├─────────────────────────────────┤
│  Session Memory (Conversation)  │  ← This chat's history, decisions
├─────────────────────────────────┤
│  Project Memory (Repository)    │  ← Codebase conventions, patterns
├─────────────────────────────────┤
│  Long-term Memory (Persistent)  │  ← User preferences, learned lessons
└─────────────────────────────────┘
```

### What to store at each layer

| Layer | Store | Expire |
|-------|-------|--------|
| Working | Current file, current function, intent | End of task |
| Session | Decisions made, files changed, errors hit | End of conversation |
| Project | Code conventions, architecture, tooling | When project changes |
| Long-term | User preferences, common mistakes, patterns | Never (update in place) |

## Memory Operations

```python
class MemoryStore:
    def remember(self, key: str, value: str, category: str):
        """Store a fact with category for retrieval."""
        ...

    def recall(self, query: str, limit: int = 5) -> list:
        """Find relevant memories matching a query."""
        ...

    def forget(self, key: str):
        """Remove a specific memory."""
        ...

    def consolidate(self):
        """Merge similar memories, remove duplicates."""
        ...
```

## Context Injection Pattern

When answering a question, build context from memory:

```
1. Parse user query → extract entities and intent
2. Search knowledge graph for matching entities
3. Traverse relationships for related context
4. Rank results by relevance and recency
5. Inject top results into LLM prompt as context
6. After response, store any new facts learned
```

## Anti-Patterns

1. **Storing everything** — Be selective; not every message is worth remembering
2. **Never pruning** — Old, incorrect memories pollute context
3. **Flat key-value** — Use relationships, not just isolated facts
4. **No timestamps** — Can't distinguish current from outdated info
5. **Ignoring contradictions** — When new info conflicts with old, update or flag it
