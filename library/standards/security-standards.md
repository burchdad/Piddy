# Security Coding Standards

## Scope: OWASP Top 10, secrets, input validation, authentication
**Authority:** OWASP Top 10 (2021), CWE/SANS Top 25, NIST  
**Tools:** Snyk, Dependabot, SonarQube, Trivy, gitleaks  

## Input Validation

```
RULE: Never trust user input. Validate at system boundaries.

1. Validate type, length, format, and range
2. Use allowlists over denylists
3. Sanitize output (context-dependent encoding)
4. Use parameterized queries (NEVER string concatenation for SQL)
```

```python
# SQL Injection prevention
# BAD:  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# GOOD:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```javascript
// XSS prevention — React auto-escapes by default
// NEVER use dangerouslySetInnerHTML with user data
// ALWAYS sanitize if rendering raw HTML (use DOMPurify)
```

## Secrets Management

| Rule | Implementation |
|------|---------------|
| Never commit secrets | Use `.env` + `.gitignore`, run `gitleaks` in CI |
| Environment variables | `process.env.DB_PASSWORD`, `os.environ["API_KEY"]` |
| Rotate regularly | Automate via vault/secrets manager |
| Least privilege | Each service gets only the keys it needs |
| No secrets in logs | Redact sensitive fields before logging |
| No secrets in URLs | Use headers (Authorization: Bearer) |

## Authentication & Authorization

```
- Use bcrypt/argon2 for password hashing (NEVER MD5/SHA1)
- JWT: short expiry (15min), refresh token rotation
- ALWAYS validate JWT signature server-side
- Enforce HTTPS everywhere
- Implement rate limiting on auth endpoints
- Use RBAC or ABAC for authorization
- Check permissions on every request (not just UI-side)
```

## Dependency Security

```bash
# Audit dependencies regularly
npm audit                    # Node.js
pip-audit                    # Python
cargo audit                  # Rust
dotnet list package --vulnerable  # .NET

# Pin dependency versions in production
# Review new dependencies before adding
# Use lockfiles (package-lock.json, Pipfile.lock)
# Run Dependabot / Renovate for automated updates
```

## OWASP Top 10 Quick Reference

| # | Risk | Key Mitigation |
|---|------|----------------|
| 1 | Broken Access Control | Check auth on every request, deny by default |
| 2 | Cryptographic Failures | Use TLS, bcrypt, avoid rolling own crypto |
| 3 | Injection | Parameterized queries, input validation |
| 4 | Insecure Design | Threat modeling, secure defaults |
| 5 | Security Misconfiguration | Harden defaults, disable debug in prod |
| 6 | Vulnerable Components | Audit deps, automated updates |
| 7 | Auth Failures | MFA, rate limiting, secure session mgmt |
| 8 | Data Integrity Failures | Verify signatures, CI/CD security |
| 9 | Logging Failures | Log security events, centralize, alert |
| 10 | SSRF | Allowlist URLs, don't fetch user-supplied URLs |
