---
name: github-workflows
description: GitHub-specific workflows — PRs, issues, Actions, code review, release management, and repository best practices
---

# GitHub Workflows

Master GitHub beyond basic git — PRs, issues, Actions, releases, and collaboration patterns.

## Pull Request Workflow

### Creating a Good PR

```markdown
## Title: feat(auth): add JWT refresh token rotation

### What
- Added refresh token rotation on each use
- Old refresh tokens are invalidated after use

### Why
Prevents token replay attacks. Addresses security audit item #47.

### Testing
- [x] Unit tests for token rotation logic
- [x] Integration test for full auth flow
- [x] Manual test with Postman

### Screenshots
(if UI changes — before/after)
```

### PR Size Guidelines

| Size | Lines Changed | Review Time | Quality |
|------|---------------|-------------|---------|
| XS | <50 | 5 min | Excellent |
| S | 50-200 | 15 min | Good |
| M | 200-500 | 30 min | OK |
| L | 500-1000 | 1 hour | Risky |
| XL | 1000+ | 2+ hours | Split it |

**Rule**: If a PR is >500 lines, split it into smaller PRs.

### Code Review Comments

```
# Good review comments
"This will throw if `user` is null — add a guard: `if (!user) return null;`"
"Nice pattern! Consider extracting this into a shared util."
"Nit: consistent naming — `getUserById` vs `fetchUser` (this file uses `get*`)"

# Bad review comments
"This is wrong" (no explanation)
"I would have done it differently" (no actionable suggestion)
"LGTM" (no substance if there are issues)
```

## GitHub Issues

### Issue Template

```markdown
## Bug Report

**Describe the bug**: Brief description
**Steps to reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**: What should happen
**Actual behavior**: What actually happens
**Environment**: OS, browser, version
**Screenshots**: If applicable
```

### Issue Labels

| Label | Meaning |
|-------|---------|
| bug | Something broken |
| feature | New functionality |
| docs | Documentation only |
| good-first-issue | Beginner-friendly |
| priority:high | Needs attention ASAP |
| wontfix | Intentionally not fixing |

## GitHub Actions

### Basic CI Workflow

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -e ".[dev]"
      - run: pytest --tb=short
      - run: ruff check src/
```

### Useful Action Patterns

```yaml
# Cache dependencies
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# Run on specific file changes
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'

# Matrix testing
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest]
```

## Release Management

### Semantic Versioning

```
MAJOR.MINOR.PATCH
  │      │     └── Bug fixes (backwards compatible)
  │      └──────── New features (backwards compatible)
  └─────────────── Breaking changes
```

### Release Checklist

```
□ All tests passing on main
□ CHANGELOG.md updated
□ Version bumped in pyproject.toml / package.json
□ Tag created: git tag -a v1.2.0 -m "Release 1.2.0"
□ GitHub Release created with notes
□ Deployment triggered and verified
```

### Changelog from Commits

```bash
# Generate changelog from conventional commits
git log v1.1.0..HEAD --pretty=format:"- %s" --no-merges

# Or use a tool like git-cliff or standard-version
```

## Repository Structure Best Practices

```
.github/
├── workflows/          # CI/CD pipelines
│   ├── ci.yml
│   └── release.yml
├── ISSUE_TEMPLATE/     # Standardized issue forms
│   ├── bug_report.md
│   └── feature_request.md
├── PULL_REQUEST_TEMPLATE.md
├── CODEOWNERS          # Auto-assign reviewers
└── dependabot.yml      # Automated dependency updates
```

### CODEOWNERS

```
# Auto-assign reviewers by path
src/auth/     @auth-team
src/api/      @backend-team
frontend/     @frontend-team
*.sql         @dba-team
```

## Branch Protection Rules

For production repos, enable:
- [x] Require PR reviews (1+ approval)
- [x] Require status checks (CI must pass)
- [x] Require branches to be up to date
- [x] No force pushes to main
- [x] No deletions of main
