---
name: git-workflow
description: Git commands, branching strategies, commit conventions, and collaboration workflows
---

# Git Workflow

## Commit Convention (Conventional Commits)
```
<type>(<scope>): <short description>

Types: feat, fix, docs, style, refactor, test, chore, perf, ci
```
- `feat(auth): add JWT refresh token rotation`
- `fix(chat): prevent duplicate messages on reconnect`
- `refactor(agent): extract LLM failover into separate module`

## Branching Strategy
```
main ─────────────────────── production (always deployable)
  └── dev ────────────────── integration branch
       ├── feat/chat-streaming
       ├── fix/session-timeout
       └── refactor/agent-core
```
- `main` — stable, tagged releases only
- `dev` — integration branch, CI must pass
- `feat/*` — new features, branch from dev
- `fix/*` — bug fixes, branch from dev (or main for hotfix)

## Common Operations
```bash
# Start new feature
git checkout dev && git pull
git checkout -b feat/my-feature

# Save work in progress
git add -A && git commit -m "wip: checkpoint"

# Squash before merge
git rebase -i dev  # squash fixup commits into one clean commit

# Update feature branch with latest dev
git fetch origin && git rebase origin/dev

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what changed
git diff --stat dev...HEAD
git log --oneline dev..HEAD
```

## Pull Request Checklist
- [ ] Clear title with conventional commit format
- [ ] Description explains WHAT and WHY
- [ ] Tests pass (CI green)
- [ ] No unrelated changes
- [ ] Self-reviewed diff before requesting review

## Conflict Resolution
1. Understand both sides of the conflict
2. Keep the intent of both changes if possible
3. Test after resolving
4. Never just accept "ours" or "theirs" blindly

## .gitignore Essentials
```
node_modules/
__pycache__/
*.pyc
.env
*.db
dist/
.DS_Store
```
