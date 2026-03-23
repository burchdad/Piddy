---
name: security-hardening
description: Security best practices for APIs, authentication, data protection, and OWASP compliance
---

# Security Hardening

## Authentication

### Password Hashing

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Rules:**
- bcrypt with cost factor 12+ (or argon2id for new projects)
- Never store plaintext passwords or API keys in code
- Never log passwords, tokens, or secrets

### JWT Tokens

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.environ["JWT_SECRET"]  # 256-bit random key

def create_access_token(user_id: str) -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

**Token guidelines:**
- Access tokens: 15-30 min expiry
- Refresh tokens: 7-30 days, stored in httpOnly cookies
- Always validate `exp` and `iat` claims
- Rotate refresh tokens on use (one-time use)

## API Security

### Input Validation

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w.-]+@[\w.-]+\.\w+$")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v):
        # Strip control characters
        return re.sub(r"[\x00-\x1f\x7f]", "", v).strip()
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str):
    ...
```

Recommended limits:
- Authentication endpoints: 5-10/minute
- Public API: 30-60/minute
- Internal API: 200-500/minute

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Never use ["*"] in production
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
    max_age=3600,
)
```

### Security Headers

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"  # Deprecated; use CSP instead
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

## Data Protection

### Encryption at Rest

```python
from cryptography.fernet import Fernet

# Generate key once, store securely
key = Fernet.generate_key()  # Store in env var or key vault
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(b"sensitive data")

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

### SQL Injection Prevention

```python
# ALWAYS use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# NEVER do this
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # VULNERABLE
```

### XSS Prevention

- Sanitize user-generated content before rendering
- Use Content-Security-Policy headers
- In React: JSX auto-escapes by default — never use `dangerouslySetInnerHTML`
- Escape HTML entities in server-rendered content

## Secret Management

```python
# Use environment variables
import os
API_KEY = os.environ["API_KEY"]

# Or encrypted config files (Piddy pattern)
from cryptography.fernet import Fernet
# Keys stored in config/keys.enc, decrypted at runtime

# NEVER commit secrets to git
# .gitignore:
# .env
# *.enc
# *secret*
```

## OWASP Top 10 Checklist

| # | Vulnerability | Mitigation |
|---|--------------|------------|
| 1 | Broken Access Control | Verify permissions on every request; deny by default |
| 2 | Cryptographic Failures | Use Fernet/AES-256; TLS everywhere; hash passwords with bcrypt |
| 3 | Injection | Parameterized queries; input validation; no eval/exec on user input |
| 4 | Insecure Design | Threat model before building; principle of least privilege |
| 5 | Security Misconfiguration | Disable debug in prod; remove default credentials; minimal permissions |
| 6 | Vulnerable Components | Keep dependencies updated; use `pip audit` / `npm audit` |
| 7 | Auth Failures | Strong passwords; MFA; account lockout after failed attempts |
| 8 | Data Integrity | Verify signatures; use Subresource Integrity (SRI) for CDN scripts |
| 9 | Logging Failures | Log security events (login, auth failures, permission denials) |
| 10 | SSRF | Validate and restrict outbound URLs; block internal network ranges |

## Security Audit Checklist

Before deploying, verify:
- [ ] No secrets in source code or git history
- [ ] All user input validated and sanitized
- [ ] Authentication on all protected endpoints
- [ ] Rate limiting on public endpoints
- [ ] CORS restricted to specific origins
- [ ] Security headers present
- [ ] Dependencies scanned for vulnerabilities
- [ ] Error messages don't leak internal details
- [ ] Logging captures security events (without sensitive data)
- [ ] Database queries use parameterized statements
