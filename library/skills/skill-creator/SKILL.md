---
name: skill-creator
description: Guide for creating new Piddy skills — format, structure, best practices, and testing
---

# Skill Creator

Create new skills that extend Piddy's capabilities. Skills are knowledge files that get injected into LLM prompts when relevant to a user's query.

## Skill File Format

Each skill lives in `library/skills/<skill-name>/SKILL.md`:

```markdown
---
name: my-skill-name
description: One-line description of what this skill does
version: 1.0
tags: [tag1, tag2, tag3]
---

# Skill Title

Detailed instructions, patterns, and examples...
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| name | yes | Display name — shown in Skills page |
| description | yes | One-line summary of the skill's purpose |
| version | yes | Semantic version (e.g., 1.0) — no quotes |
| tags | yes | Inline array of keywords for query matching |

### Tags are critical

Tags determine when the skill gets activated. Choose tags that match what users actually type:

```yaml
# Good tags — match natural queries
tags: [python, api, fastapi, backend, pydantic]

# Bad tags — too generic or won't match queries
tags: [code, programming, stuff]
```

## Content Structure

### Recommended layout

```markdown
# Title

Brief intro — when to use this skill.

## Core Concepts
Key principles and rules.

## Patterns / Templates
Code examples showing the RIGHT way.

## Common Mistakes / Anti-Patterns
What to avoid and why.

## Quick Reference
Tables, checklists, or cheat sheets.
```

### Quality checklist

- [ ] Every section has actionable content (not just descriptions)
- [ ] Code examples are complete and runnable
- [ ] Anti-patterns shown with corrections
- [ ] Tags match realistic user queries
- [ ] Description is specific (not "helps with code")

## How Skills Get Loaded

```
library/skills/
├── my-skill/
│   └── SKILL.md          ← discovered automatically
├── another-skill/
│   └── SKILL.md
└── legacy.skill.md        ← also discovered (alternative format)

Discovery → Parse frontmatter → Register in SkillRegistry
```

The `SkillRegistry` (in `src/skills/loader.py`):
1. Scans `library/skills/` recursively for `SKILL.md` and `*.skill.md`
2. Parses YAML frontmatter with simple regex (inline tags only)
3. Registers each skill with name, description, version, tags
4. `matches_query()` — checks if skill is relevant to user input
5. `get_context_for_query()` — returns matching skill instructions

### Parser limitations

- Tags MUST be inline: `tags: [a, b, c]` — NOT multi-line YAML lists
- Version MUST be unquoted: `version: 1.0` — NOT `version: "1.0"`
- Use simple colon-separated key-value pairs in frontmatter

## Testing a New Skill

1. Create the file: `library/skills/<name>/SKILL.md`
2. Call the reload endpoint: `POST /api/skills/reload`
3. Verify it appears: `GET /api/skills`
4. Test matching: ask Piddy a question using one of the skill's tags
5. Verify the skill's instructions appear in the LLM context

## Skill Writing Best Practices

1. **Be opinionated** — Don't list 5 options. Recommend the best one.
2. **Show, don't tell** — Code examples > prose descriptions
3. **Keep it scannable** — Tables, bullet points, short paragraphs
4. **Include the WHY** — "Use X because Y" not just "Use X"
5. **Stay current** — Update skills when tools/patterns evolve
6. **One skill, one domain** — Don't create a skill that covers everything
7. **Test with real queries** — Make sure tags actually trigger the skill

## Example: Creating a "React Hooks" Skill

```markdown
---
name: React Hooks
description: Modern React hooks patterns, custom hooks, and state management
version: 1.0
tags: [react, hooks, useState, useEffect, custom-hooks, state]
---

# React Hooks

## Core Rules
1. Only call hooks at the top level (never in loops/conditions)
2. Only call hooks from React functions

## useState Patterns
[examples...]

## useEffect Cleanup
[examples...]

## Custom Hook Template
[examples...]
```
