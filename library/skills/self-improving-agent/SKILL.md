---
name: self-improving-agent
description: Learn from errors, capture corrections, and continuously improve responses and code quality over time
---

# Self-Improving Agent

Capture learnings, errors, and corrections to enable continuous improvement. Apply when a command fails, when the user corrects output, or when reflecting on completed work.

## Error Learning Loop

When something goes wrong, follow this cycle:

```
1. DETECT  → Recognize the error or correction
2. ANALYZE → Why did it fail? Root cause, not symptoms
3. RECORD  → Store the lesson (what failed, why, what works)
4. APPLY   → Use the lesson in future similar situations
5. VERIFY  → Confirm the fix actually resolves the issue
```

## Capturing Corrections

When the user corrects your output:

```markdown
## Correction Log Entry

**Task**: [What was requested]
**My Output**: [What I produced]
**Correction**: [What the user said was wrong]
**Root Cause**: [Why I got it wrong]
**Lesson**: [One-sentence rule to prevent this]
**Category**: [code-style | logic-error | misunderstanding | missing-context | wrong-tool]
```

### Common correction categories

| Category | Example | Prevention |
|----------|---------|------------|
| code-style | "We use single quotes" | Check project conventions first |
| logic-error | "That loop is off by one" | Trace edge cases before outputting |
| misunderstanding | "I meant the OTHER file" | Clarify ambiguous requests |
| missing-context | "We already have a util for that" | Search codebase before creating new code |
| wrong-tool | "Use pytest, not unittest" | Check project setup first |

## Error Pattern Recognition

### Build/Runtime Errors

```
Error observed → Check memory for similar errors
  ├── Found match → Apply known fix
  └── No match → Debug, fix, then record:
        - Error message pattern
        - Root cause
        - Working solution
        - Environment context (OS, versions)
```

### Repeated Mistakes

If the same type of error occurs 2+ times:
1. Escalate to a **rule** (not just a note)
2. Add it to pre-task checklist
3. Example: "Always check if port is in use before starting server"

## Self-Reflection Protocol

After completing a multi-step task, reflect:

```markdown
## Post-Task Reflection

**What went well**: [Steps that worked first try]
**What struggled**: [Steps that needed retries or corrections]
**Time sinks**: [Where did I spend the most effort?]
**Key learning**: [One new insight to carry forward]
**Would I approach it differently?**: [Yes/No — if yes, how?]
```

## Knowledge Categories

Organize learnings into buckets:

1. **Project-specific** — This repo's conventions, patterns, tools
2. **Language-specific** — Python gotchas, JS quirks, etc.
3. **Tool-specific** — CLI flags, API behaviors, version differences
4. **User-specific** — Preferences, communication style, priorities
5. **Environment-specific** — OS differences, path formats, encoding issues

## Improvement Strategies

### Before Starting a Task
- Check memory for relevant past lessons
- Review project conventions and existing patterns
- Identify potential failure points from past experience

### During Execution
- Validate each step before proceeding
- If something fails, check if you've seen this before
- Don't repeat the same approach if it failed — try alternatives

### After Completion
- Record any new learnings
- Update outdated notes if something changed
- Flag patterns that keep recurring

## Anti-Patterns to Avoid

1. **Ignoring corrections** — Every user correction is a learning opportunity
2. **Repeating mistakes** — If it failed before, don't try the same thing again
3. **Over-generalizing** — A fix for one project may not apply to another
4. **Forgetting context** — Always note WHEN and WHERE a lesson applies
5. **Not verifying** — Always confirm your fix actually works before moving on
