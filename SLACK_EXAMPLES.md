# Piddy Slack - Command Examples by Scenario

Real-world examples of how to ask Piddy for backend development tasks in Slack.

## 📝 Code Generation Examples

### Example 1: FastAPI Endpoint with Auth

**Scenario**: You need a user registration endpoint for your new FastAPI app

**Basic command**:
```
@Piddy Generate FastAPI endpoint for user registration
```

**Better command** (more context):
```
@Piddy I'm building a user management service with FastAPI and PostgreSQL.
Generate a registration endpoint that:
- Accepts email, password, name, phone
- Validates email format and password strength
- Returns JWT token on success
- Uses SQLAlchemy models
- Includes error handling for duplicate emails
```

**Response**:
Piddy generates complete, production-ready code with:
- Request/response models
- Password hashing
- Database operations
- Error handling
- Input validation

---

### Example 2: Express.js REST API

**Scenario**: Building Node.js backend, need CRUD endpoints

**Command**:
```
@Piddy Create Express.js REST API for a blog

Endpoints needed:
- GET /posts (list all)
- GET /posts/:id (get one)
- POST /posts (create)
- PUT /posts/:id (update)
- DELETE /posts/:id (delete)

Use MongoDB with Mongoose for models
Include JWT authentication on write operations
Add input validation
```

**Response**: Full Express.js router with all endpoints

---

### Example 3: Python Function

**Scenario**: Need a utility function

**Command**:
```
@Piddy Write a Python async function that:
- Fetches user data from PostgreSQL
- Caches result in Redis for 1 hour
- Returns None if user not found
- Raises exception if database error

Use SQLAlchemy and aioredis
Include proper error logging
```

**Response**: Production-ready async function

---

## 🔍 Code Review Examples

### Example 1: Security Audit

**Scenario**: Code written by another team member, need security review

**In Slack thread** (so code is visible):
```
@Piddy Review this for security vulnerabilities:

```python
@app.post("/login")
def login(username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:
        return {"token": generate_jwt(user.id)}
    return {"error": "Invalid"}
```

Please check for:
- Authentication issues
- Data exposure
- Best practices
```

**Response**: Lists vulnerabilities with fixes:
- ❌ Passwords stored plain text → Should use bcrypt
- ❌ No rate limiting → Add limit on attempts
- ❌ SQL injection risk (if not using ORM) → Use parameterized queries
- ✅ Suggestions for implementation

---

### Example 2: Performance Review

**Command**:
```
@Piddy Analyze this code for performance issues

```python
def get_user_posts(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    posts = []
    for post_id in user.post_ids:
        post = db.query(Post).filter(Post.id == post_id).first()
        posts.append(post)
    return posts
```

Framework: FastAPI + SQLAlchemy
Database: PostgreSQL
```

**Response**: Identifies N+1 query problem, suggests eager loading

---

### Example 3: Code Quality

**Command**:
```
@Piddy Check this for:
- Code quality
- Maintainability
- Test coverage
- Best practices

```python
def validate_email(e):
    import re
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e)

def process_user(u):
    if validate_email(u['email']):
        db.add(u)
        db.commit()
        return True
    return False
```
```

**Response**: Suggestions for:
- Error handling
- Type hints
- Documentation
- Testability

---

## 🗄️ Database Examples

### Example 1: Schema Design

**Command**:
```
@Piddy Design a database schema for an e-commerce platform

Entities:
- Users (customers)
- Products (with categories)
- Orders (with items)
- Inventory
- Reviews

Requirements:
- Support multiple currencies
- Track inventory changes
- Support soft deletes
- Audit trail for orders
- Performance optimized

Use PostgreSQL with SQLAlchemy models
```

**Response**: Complete schema with:
- Tables and relationships
- Indexes for performance
- Constraints for data integrity

---

### Example 2: Migration

**Command**:
```
@Piddy Generate a database migration

Current schema: User has id, email, name, created_at
Need to add: phone, address, country, verified, verified_at

Use Alembic for Python/SQLAlchemy
Include both up() and down()
Add data migration for existing users
```

**Response**: Complete Alembic migration file

---

### Example 3: Complex Relationships

**Command**:
```
@Piddy Design MongoDB schema for a SaaS platform

Entities:
- Organizations (have many users)
- Users (belong to organizations)
- Projects (belong to organizations)
- Tasks (belong to projects)
- Users can be org admin, project lead, or contributor

Relationships:
- M2M: Users ↔ Organizations
- M2M: Users ↔ Projects  
- 1:M: Organizations → Projects
- 1:M: Projects → Tasks

Generate Mongoose schemas with proper indexing
```

**Response**: Optimized schema with relationship queries

---

## 🏗️ Architecture Examples

### Example 1: API Design

**Command**:
```
@Piddy Design a GraphQL API for a social media platform

Entities:
- User (followers, following, posts)
- Post (comments, likes)
- Comment (likes, replies)

Mutations needed:
- Create post
- Like/unlike post
- Follow/unfollow user
- Comment on post

Subscriptions:
- New post from followed users
- New comments on my posts

Use Apollo Server (Node.js)
```

**Response**: Complete schema definition

---

### Example 2: Microservices

**Command**:
```
@Piddy Design microservices architecture for an app with:

Services:
1. User Service (auth, profiles)
2. Product Service (catalog, search)
3. Order Service (orders, payment)
4. Inventory Service (stock)
5. Notification Service (email, SMS)

Requirements:
- Async communication where possible
- Shared PostgreSQL database? Or separate?
- How to handle distributed transactions?
- API Gateway needed?

Stack: Python/FastAPI, PostgreSQL, RabbitMQ
```

**Response**: Architecture diagram suggestions, service boundaries, communication patterns

---

### Example 3: System Design

**Command**:
```
@Piddy Design a system for real-time notifications

Expected load:
- 100K concurrent users
- 10M notifications per day
- Read-heavy (95% reads)

Questions:
- In-memory cache needed?
- Message queue for reliability?
- Websockets or polling?
- Database schema?

Stack recommendation please
```

**Response**: Scalable architecture with tech stack options

---

## 🚀 Infrastructure Examples

### Example 1: Docker

**Command**:
```
@Piddy Generate Dockerfile for FastAPI app

Requirements:
- Python 3.11
- Production ASGI server (uvicorn)
- Multi-stage build
- Minimize image size
- Use official Python image

The app uses:
- FastAPI
- SQLAlchemy
- Pydantic
- Redis client
```

**Response**: Optimized Dockerfile with best practices

---

### Example 2: Kubernetes

**Command**:
```
@Piddy Create Kubernetes deployment manifests for:

Services:
1. FastAPI backend
2. PostgreSQL database
3. Redis cache

Requirements:
- 3 instances of backend
- Auto-scaling 2-10 pods
- Database with persistent volume
- Resource limits
- Health checks
- ConfigMap for settings
- Secret for DB password

Namespace: production
```

**Response**: Complete YAML manifests ready to deploy

---

### Example 3: Docker Compose

**Command**:
```
@Piddy Generate docker-compose.yml for development with:

Services:
- FastAPI app (code volume)
- PostgreSQL 15
- Redis latest
- pgAdmin (admin)

Volume mounts:
- App code at /app
- DB data persisted

Environment:
- Dev database
- Dev Redis
- Debug mode on

Port mappings:
- API: 8000
- pgAdmin: 5050
- App reloads on code changes
```

**Response**: Complete docker-compose file with commentary

---

## 🔐 Security Examples

### Example 1: Vulnerability Analysis

**Command** (in reply thread):
```
@Piddy Perform a security audit on this code:

```python
@app.post("/api/users")
def create_user(name: str, email: str, password: str):
    user = User(name=name, email=email, password=password)
    db.add(user)
    db.commit()
    return user.dict()
```

Check for:
- Authentication/authorization
- Data validation
- Injection attacks
- Data exposure
- Best practices
```

**Response**: Detailed security findings with CVSS scores

---

### Example 2: Authentication Design

**Command**:
```
@Piddy Design a secure authentication system for:

Requirements:
- Mobile app + web app
- Should support: email/password, OAuth2 (Google/GitHub), SSO
- Need refresh tokens
- Session management
- Account recovery
- 2FA support

Stack: FastAPI + PostgreSQL
```

**Response**: Complete auth architecture and implementation

---

### Example 3: Data Protection

**Command**:
```
@Piddy Recommend data protection strategy for:

Sensitive data:
- User passwords
- Credit card info
- Medical records
- User locations

Compliance: GDPR, PCI-DSS

Technologies: FastAPI, PostgreSQL, S3
```

**Response**: Encryption strategy, compliance recommendations

---

## 🐛 Debugging Examples

### Example 1: Root Cause

**Command**:
```
@Piddy Help debug this issue:

Problem: "Users report slow page load when fetching profile"

Error log: 
```
GET /users/123/profile - 8.5s
```

Code (simplified):
```python
@app.get("/users/{user_id}/profile")
def get_profile(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    comments = db.query(Comment).filter(Comment.user_id == user_id).all()
    followers = db.query(User).filter(User.id.in_(user.follower_ids)).all()
    return {
        "user": user,
        "posts": posts,
        "comments": comments,  
        "followers": followers
    }
```

Database: PostgreSQL, SQLAlchemy
Schema: User has 100K posts, 50K comments, 10K followers
```

**Response**: Identifies N+1 problem, suggests caching/eager loading

---

### Example 2: Test Failures

**Command**:
```
@Piddy Why are these tests failing?

Test code:
```python
def test_user_creation():
    user = create_user("john@example.com", "password123")
    assert user.id is not None
    assert user.email == "john@example.com"
```

Error:
```
AssertionError: assert None == 'john@example.com'
```

The create_user function works in the app, but fails in tests
```

**Response**: Suggests database setup issues, fixtures needed, etc.

---

## 📚 Documentation Examples

### Example 1: API Documentation

**Command**:
```
@Piddy Generate OpenAPI documentation for these endpoints:

GET /users - list all users
GET /users/{id} - get user by id
POST /users - create user
PUT /users/{id} - update user
DELETE /users/{id} - delete user

Include example responses, authentication requirements
Format: OpenAPI 3.0 (for FastAPI)
```

**Response**: Complete OpenAPI spec

---

## 💡 Tips for Better Results

### 1. Provide Context
**Poor**: `@Piddy Generate an endpoint`
**Better**: `@Piddy I'm using FastAPI with PostgreSQL and SQLAlchemy. Generate a user endpoint that...`

### 2. Specify Requirements
**Poor**: `@Piddy Create a login endpoint`
**Better**: `@Piddy Create a login endpoint with JWT, rate limiting, email validation, and bcrypt password hashing`

### 3. Use Threads for Long Requests
- Write code in thread reply (easier for Piddy to analyze)
- Keep conversation organized
- Get follow-ups in same thread

### 4. Ask Follow-ups
```
Thread: Original request
Reply 1: Can you also add X?
Reply 2: Can you make it async?
Reply 3: Add tests?
```

### 5. Share the Language/Framework
```
@Piddy Generate endpoint for [language/framework]
```

### 6. Include Error Details
If something's wrong:
```
@Piddy This code throws [error]:
[code]

How can I fix it?
```

---

## 🎯 Command Types Reference

| Type | When to Use | Example |
|------|------------|---------|
| Generate | Need new code | `@Piddy Generate FastAPI endpoint...` |
| Review | Analyze existing code | `@Piddy Review this for security` |
| Design | Architecture/schema | `@Piddy Design database schema for...` |
| Debug | Fix broken code | `@Piddy Why is this failing?` |
| Refactor | Improve code | `@Piddy Refactor this for performance` |
| Document | Write docs/comments | `@Piddy Document this function` |
| Explain | Understand code | `@Piddy Explain how this works` |

---

See [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) for more commands and [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md) for help!
