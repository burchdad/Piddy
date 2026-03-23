---
name: humanizer
description: Remove signs of AI-generated writing, make text sound natural and human-written
---

# Humanizer

Detect and fix AI-generated writing patterns. Make text sound natural, conversational, and human-written.

## Common AI Writing Patterns to Fix

### 1. Inflated Language

```
AI:    "This groundbreaking, revolutionary approach fundamentally transforms..."
Human: "This approach changes how we..."

AI:    "Leveraging cutting-edge methodologies to synergistically optimize..."
Human: "Using modern tools to improve..."
```

**Rule**: Strip superlatives. If removing the adjective doesn't change meaning, remove it.

### 2. The Rule of Three

```
AI:    "It's fast, reliable, and scalable."
       "Improve performance, reliability, and maintainability."
       "Clear, concise, and comprehensive."
Human: Vary the count. Sometimes two things. Sometimes four. Sometimes just one.
```

### 3. Em Dash Overuse

```
AI:    "The system — which was built last year — handles requests efficiently — even under load."
Human: Use em dashes sparingly. One per paragraph max. Prefer commas or parentheses.
```

### 4. Excessive Conjunctive Phrases

```
AI:    "Moreover, it's worth noting that furthermore, in addition to this..."
Human: Just say the thing. Cut the preamble.
```

### 5. AI Vocabulary Words

Replace these overused AI words:

| AI Word | Human Alternatives |
|---------|--------------------|
| leverage | use, apply, take advantage of |
| utilize | use |
| facilitate | help, enable |
| robust | strong, solid, reliable |
| comprehensive | full, complete, thorough |
| innovative | new, creative |
| streamline | simplify |
| delve into | explore, look at, dig into |
| paramount | important, critical |
| myriad | many, lots of |
| tapestry | (just don't) |
| embark on | start, begin |
| landscape | field, area, space |
| nuanced | subtle, complex |
| pivotal | key, important |

### 6. Negative Parallelism

```
AI:    "It's not just about speed — it's about reliability."
       "It's not merely a tool — it's a complete solution."
Human: State what it IS. Skip the "not just X, but Y" construction.
```

### 7. Promotional Tone

```
AI:    "This powerful feature enables teams to achieve unprecedented levels of..."
Human: "This feature lets teams..."
```

### 8. Vague Attributions

```
AI:    "Many experts agree that..."
       "Studies have shown..."
Human: Name the expert or study, or drop the attribution entirely.
```

### 9. Overly Structured Responses

```
AI:    "There are three key aspects to consider:
        1. First, ...
        2. Second, ...
        3. Third, ..."
Human: Vary structure. Use prose. Not everything needs a numbered list.
```

### 10. Weak Conclusions

```
AI:    "In conclusion, by leveraging these best practices, you can significantly
        enhance your development workflow and achieve optimal results."
Human: End with the last point. Or a one-line takeaway. Don't summarize what
       you just said.
```

## Humanization Process

```
1. READ   → Read the full text without editing
2. SCAN   → Identify AI patterns (checklist above)
3. CUT    → Remove filler words, weak phrases, preamble
4. VARY   → Break up parallel structures, vary sentence length
5. VOICE  → Match the intended audience's tone and vocabulary
6. READ   → Read aloud (mentally). Does it sound like a person?
```

## Tone Calibration

| Context | Tone | Example |
|---------|------|---------|
| Technical docs | Direct, clear | "Returns a list of users. Throws if the ID is invalid." |
| README | Friendly, concise | "Drop it in, it just works." |
| Blog post | Conversational | "I tried six different approaches. Here's what actually worked." |
| Email | Professional, brief | "Following up on the API issue — here's the fix." |
| Code comments | Terse, explains why | "# Retry needed — upstream flakes under load" |

## Quick Check

After editing, the text should:
- [ ] Sound like something a real person would write
- [ ] Not be detectable by AI content detectors
- [ ] Vary in sentence length and structure
- [ ] Avoid more than 1 em dash per paragraph
- [ ] Not use any words from the AI vocabulary table
- [ ] Not end with a generic summary conclusion
- [ ] Feel natural when read aloud
