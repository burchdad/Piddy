# Code Review Standards

## Scope: Review process, checklist, feedback etiquette
**Authority:** Google Engineering Practices, Thoughtbot Code Review Guide  
**Applies To:** All pull requests and merge requests  

## Author Checklist (Before Requesting Review)

- [ ] Self-reviewed the entire diff
- [ ] PR is small (< 400 lines, single purpose)
- [ ] Descriptive title (conventional commit format)
- [ ] Description: What, Why, How, Testing approach
- [ ] All CI checks pass (lint, test, build)
- [ ] No commented-out code or debug statements
- [ ] No merge conflicts
- [ ] Screenshots/recordings for UI changes

## Reviewer Checklist

**Correctness:**
- Does the code do what the PR description claims?
- Are edge cases handled?
- Are errors handled properly (not swallowed)?

**Design:**
- Right level of abstraction?
- Single Responsibility — does each function/class do one thing?
- Would a simpler approach work?

**Security:**
- Input validated at boundaries?
- No secrets in code?
- SQL injection / XSS risks?

**Performance:**
- N+1 queries?
- Unnecessary allocations in hot paths?
- Missing indexes for new queries?

**Maintainability:**
- Clear naming?
- Would a new team member understand this?
- Tests cover the change?

## Feedback Etiquette

| Do | Don't |
|----|-------|
| "Consider using X because..." | "This is wrong" |
| "Nit: rename to Y for clarity" | "Bad variable name" |
| Ask questions: "What happens if...?" | Make assumptions |
| Prefix: `nit:`, `suggestion:`, `blocking:` | Leave ambiguous severity |
| Approve with minor nits | Block on style preferences |
| Praise good patterns | Only point out negatives |

**Turnaround:** Review within 1 business day.
**Resolve promptly:** Author responds to all comments before re-requesting.
