---
name: ci-cd-pipelines
description: Build CI/CD pipelines for automated testing, building, and deployment
---

# CI/CD Pipelines

## GitHub Actions (Most Common)
```yaml
name: CI
on:
  push:
    branches: [main, dev]
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
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff
      - run: ruff check .

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:${{ github.sha }} .
```

## Pipeline Stages
```
[Commit] → [Lint] → [Test] → [Build] → [Deploy Staging] → [Deploy Prod]
                                              ↓
                                    [Integration Tests]
```

## Best Practices
- **Fast feedback** — Lint first (fastest), then unit tests, then integration
- **Parallel jobs** — Run independent stages concurrently
- **Cache dependencies** — Don't download packages every run
- **Fail fast** — Stop pipeline on first failure
- **Artifact management** — Store build outputs, test reports
- **Environment secrets** — NEVER hardcode, use CI secrets manager
- **Branch protection** — Require CI pass before merge to main

## Caching Example
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('requirements.txt') }}
    restore-keys: pip-
```

## Deployment Strategy
- **Rolling** — Replace instances one at a time (zero downtime)
- **Blue/Green** — Run two environments, swap traffic
- **Canary** — Route small % of traffic to new version first
- **Feature flags** — Deploy code dark, enable gradually

## Notifications
- Notify on failure (Slack, email, webhook)
- Don't notify on success (noise) unless it's a deployment
- Include: commit, author, failure stage, and link to logs
