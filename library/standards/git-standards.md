# Git Conventions & Standards

## Scope: Commit messages, branching, PR workflow
**Authority:** Conventional Commits, Git Flow, GitHub Flow  
**Tools:** commitlint, husky, lint-staged  

## Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no logic change) |
| `refactor` | Code restructure (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding/fixing tests |
| `chore` | Build, CI, dependencies |
| `ci` | CI/CD configuration |

**Examples:**
```
feat(auth): add JWT refresh token support
fix(api): handle null response from user endpoint
docs(readme): add deployment instructions
refactor(db): extract connection pooling to module
feat!: drop support for Node 16  (BREAKING CHANGE)
```

## Branching Strategy (GitHub Flow)

```
main (always deployable)
 └── feature/add-user-auth
 └── fix/null-pointer-dashboard
 └── chore/upgrade-dependencies
```

**Rules:**
- `main` is always deployable
- Branch from `main`, PR back to `main`
- Branch names: `type/short-description` (kebab-case)
- Delete branch after merge
- Use squash merge for clean history

## Commit Best Practices

| Rule | Example |
|------|---------|
| Imperative mood | "Add feature" not "Added feature" |
| Subject ≤ 72 chars | Keep it scannable |
| No period at end | `feat: add login` not `feat: add login.` |
| Body: explain WHY | What changed is in the diff; commit says why |
| One logical change | Don't mix refactor + feature |
| Never commit secrets | Use `.env` + `.gitignore` |

## Pull Request Guidelines

- **Title:** follows conventional commit format
- **Description:** What, Why, How, Testing
- **Size:** < 400 lines changed (split larger PRs)
- **Self-review:** before requesting review
- **CI green** before requesting review
- **One approval minimum** before merge
- **Link issues:** `Closes #123` in description
