---
name: technical-writing
description: Write clear technical content — blog posts, tutorials, changelogs, error messages, and user-facing copy
---

# Technical Writing

Write technical content that people actually want to read.

## Blog Posts / Tutorials

### Structure

```
1. Hook — What problem does this solve? (1-2 sentences)
2. Context — Why does this matter? When would you need this?
3. Solution — Step-by-step walkthrough with code
4. Gotchas — What tripped you up? What's non-obvious?
5. Takeaway — One key insight (not a long summary)
```

### Example Opening

```markdown
Bad:  "In this comprehensive guide, we will explore the intricacies of..."
Good: "Our deploy script kept timing out. Here's the one-line fix."

Bad:  "Docker is a powerful containerization platform that..."
Good: "I wasted 3 hours on a Docker build cache issue. Don't be me."
```

### Code in Tutorials

- Show the **final working code** first, then explain
- Include the **exact commands** to run, not paraphrased
- Show expected output so readers can verify they're on track
- Mark optional steps clearly ("You can skip this if...")

## Error Messages

### Format

```
What happened → Why it happened → How to fix it

Bad:  "Error: Invalid input"
Good: "Invalid email format. Expected: user@domain.com. Got: 'not-an-email'"

Bad:  "Connection failed"
Good: "Can't reach database at localhost:5432. Is PostgreSQL running? Try: sudo systemctl start postgresql"
```

### Rules for error messages

1. Say what went wrong (specific, not generic)
2. Say why (if you know)
3. Say how to fix it (actionable step)
4. Include the actual values that caused the error
5. Never expose internal details to end users (stack traces, SQL, etc.)

## Commit Messages (Conventional Commits)

```
<type>(<scope>): <description>

feat(auth): add JWT refresh token rotation
fix(api): handle null user in /profile endpoint
docs(readme): add quickstart section
refactor(db): extract query builder into util
chore(deps): bump fastapi to 0.104.0
test(auth): add edge case for expired tokens
```

## README Sections

Must-have sections in order of importance:

1. **Title + one-liner** — What is this?
2. **Quick Start** — Get running in <60 seconds
3. **Features** — Bullet list, not paragraphs
4. **Configuration** — Table of env vars
5. **Development** — How to contribute/test
6. **License** — MIT, Apache, etc.

Optional but nice:
- Screenshots/demo GIF
- Architecture diagram
- FAQ
- Troubleshooting

## API Documentation

```markdown
### POST /api/users

Create a new user account.

**Headers**: Authorization: Bearer <token>

**Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | yes | Valid email address |
| name | string | yes | Display name (1-100 chars) |
| role | string | no | "user" or "admin" (default: "user") |

**Response 201**:
{ "id": "usr_abc", "email": "a@b.com", "name": "Alice" }

**Errors**:
- 400 — Missing required field
- 409 — Email already registered
- 422 — Invalid email format
```

## Editing Principles

1. **Cut first, then add** — Delete everything unnecessary, then see what's missing
2. **One idea per paragraph** — If you need "also" or "additionally", start a new paragraph
3. **Active voice** — "The function returns X" not "X is returned by the function"
4. **Concrete > abstract** — Show a specific example rather than describing in general terms
5. **Front-load the answer** — Put the key information in the first sentence, context after
