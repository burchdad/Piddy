---
name: skill-vetter
description: Evaluate third-party skills, plugins, and code for security risks, red flags, and suspicious patterns before installation
---

# Skill Vetter

Security-first evaluation for skills, plugins, extensions, and third-party code before installation. Checks for red flags, permission scope, and suspicious patterns.

## Vetting Checklist

Before installing any skill or plugin:

```
1. SOURCE VERIFICATION
   □ Who is the author? Known/trusted?
   □ Is the source repo public and auditable?
   □ Does it have meaningful stars/reviews?
   □ When was it last updated?

2. PERMISSION AUDIT
   □ What file system access does it need?
   □ Does it require network/internet access?
   □ Does it need environment variables or secrets?
   □ Does it request shell/command execution?
   □ Are permissions proportional to functionality?

3. CODE INSPECTION
   □ Is the code readable and well-structured?
   □ Any obfuscated or minified code?
   □ Any encoded strings (base64, hex)?
   □ Any dynamic code execution (eval, exec, Function())?
   □ Any outbound network calls to unknown hosts?

4. DEPENDENCY CHECK
   □ What dependencies does it pull in?
   □ Are they from trusted sources?
   □ Any known vulnerabilities (npm audit, pip audit)?
   □ Minimal dependency footprint?
```

## Red Flags

### Critical (Do NOT install)

| Flag | Example | Risk |
|------|---------|------|
| Obfuscated code | `eval(atob("aGVsbG8="))` | Hidden malicious payload |
| Hardcoded URLs to unknown domains | `fetch("http://sketchy.xyz/data")` | Data exfiltration |
| Requests ALL permissions | "needs full file system + network + shell" | Over-privileged |
| Reads SSH keys / credentials | `~/.ssh/id_rsa`, `~/.aws/credentials` | Credential theft |
| Executes shell commands from user input | `os.system(user_input)` | Command injection |
| Recently created account with popular skill | 2-day-old account, 10k downloads | Typosquatting / impersonation |

### Warning (Investigate further)

| Flag | Example | Concern |
|------|---------|---------|
| No source code link | "Binary only" or "closed source" | Can't audit |
| Excessive permissions | CLI tool that needs network access | May phone home |
| No license | Missing LICENSE file | Legal risk |
| Single contributor, no community | 1 commit, 0 issues, 0 PRs | Abandoned risk |
| Telemetry/analytics built in | Sends usage data to third party | Privacy concern |

## Scoring System

Rate each skill 1-10:

```
Security:     [1-10]  Permission scope, code safety
Trustworthiness: [1-10]  Author reputation, community
Functionality: [1-10]  Does it do what it claims?
Maintenance:  [1-10]  Update frequency, issue response
Overall:      [1-10]  Weighted average

Recommendation: INSTALL / CAUTION / REJECT
```

## Safe Installation Practices

1. **Sandbox first** — test in an isolated environment
2. **Pin versions** — don't auto-update untrusted code
3. **Review changelogs** — check what changed between versions
4. **Monitor behavior** — watch network/file activity after install
5. **Limit scope** — grant minimum permissions needed

## Supply Chain Security

```
Your code
  └── depends on: libraries
        └── depend on: transitive deps
              └── any of these can be compromised

Mitigation:
- Use lockfiles (package-lock.json, poetry.lock)
- Audit dependencies regularly
- Use tools: npm audit, pip audit, safety, snyk
- Prefer well-known, actively maintained packages
- Verify package integrity with checksums
```

## Evaluation Template

```markdown
## Skill Evaluation: [skill-name]

**Author**: [@handle] — [trusted/unknown/suspicious]
**Source**: [URL]
**Last Updated**: [date]
**Downloads/Stars**: [count]

### Permissions Required
- [list each permission and whether it's justified]

### Code Review Findings
- [list any concerns or notable patterns]

### Dependencies
- [list external dependencies and their trust level]

### Verdict: [INSTALL / CAUTION / REJECT]
**Reason**: [one-line summary]
```
