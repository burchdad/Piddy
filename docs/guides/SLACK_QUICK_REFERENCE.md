# Piddy on Slack - Quick Reference

## Getting Started (5 minutes)

### 1. Setup Tokens
```bash
cp .env.example .env
# Add these tokens:
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_APP_TOKEN=xapp-1-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Start Piddy
```bash
# Linux/Mac
bash start-slack.sh

# Windows
start-slack.bat

# Or manually
python -m src.main
```

### 3. Invite to Slack
- Go to a channel
- Type `@Piddy` and add it to the channel
- Or message @Piddy directly

## Common Commands

### Code Generation
```
@Piddy Generate a FastAPI endpoint for user registration

@Piddy Create a Python function to validate email addresses

@Piddy Write a Flask route for file uploads with error handling
```

### Code Review
```
@Piddy Review this code for security issues

@Piddy Check this for performance problems

@Piddy Audit this for best practices
```

### Database Design
```
@Piddy Design a database schema for a blog (User, Post, Comment)

@Piddy Create SQLAlchemy models for an e-commerce system

@Piddy Generate MongoDB schemas for a chat application
```

### Security Analysis
```
@Piddy Analyze this code for security vulnerabilities

@Piddy Check for SQL injection risks

@Piddy Review authentication implementation
```

### Infrastructure
```
@Piddy Generate Docker configuration for a FastAPI app

@Piddy Design Kubernetes deployment manifests

@Piddy Create Docker Compose for microservices
```

### API Design
```
@Piddy Design a REST API for a task management system

@Piddy Create GraphQL schema for a social network

@Piddy Design authentication flow with OAuth2
```

## Response Format

Piddy responses include:

```
✅ Code Generation

[Your generated code block here]

📊 Execution time: 2.34s | 🔧 Command type: code_generation
```

## Tips & Tricks

### Provide Context
```
@Piddy I'm using FastAPI with PostgreSQL and SQLAlchemy. 
Generate a model for a User entity with: id, email, 
password_hash, created_at, updated_at.
```

### Use Threads
Reply in a thread to continue the conversation:
```
Thread Reply: Can you also add validation?
```

### Code Blocks
For complex code analysis:
````
@Piddy Review this code:

```python
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()
```

Add proper error handling and logging.
````

### Follow-ups
Keep refining requests in the same thread:
```
Thread Reply 1: Add unit tests
Thread Reply 2: Make it async
Thread Reply 3: Add caching
```

## Troubleshooting

### Piddy not responding
1. Check Piddy is running locally
2. Verify `SLACK_BOT_TOKEN` in `.env`
3. Restart Piddy: `python -m src.main`

### "Connection failed"
- Piddy might not be running
- Try: `python -m src.main` to start it

### "Permission denied"
- Bot needs to be invited to channel: `@Piddy`
- Or message directly in DMs

### See Logs
```bash
# View connection status
python -m src.main 2>&1 | grep -i slack
```

## Supported Frameworks

### Python
- FastAPI
- Django
- Flask

### JavaScript
- Express
- NestJS

### Go
- Gin

### Java
- Spring Boot

### Rust
- Actix

## Supported Databases

- PostgreSQL
- MySQL
- MongoDB
- Redis
- DynamoDB
- Elasticsearch

## Design Patterns Available

- Singleton
- Factory
- Strategy
- Observer
- Decorator
- Adapter
- Builder
- Repository
- Middleware
- Dependency Injection
- Chain of Responsibility

## Architecture Patterns

- Layered
- Microservices
- Event-Driven
- Hexagonal

## Emoji Meanings

| Emoji | Meaning |
|-------|---------|
| 🤔 | Processing your request |
| ✅ | Completed successfully |
| ❌ | Error occurred |
| 📊 | Metrics/statistics |
| 🔧 | Tool/command type |
| 💻 | Code/programming |
| 🔐 | Security related |
| 🚀 | Infrastructure/deployment |

## Advanced

### Using `. Set environment`
```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-1-..."
export ANTHROPIC_API_KEY="sk-ant-..."
python -m src.main
```

### Docker
```bash
docker-compose up -d
# Then use Slack normally
```

### Multiple Instances
Create separate Slack apps for dev/staging/production

### Monitoring
Check logs for:
- Connection status
- Messages processed
- Success/failure rates
- Response times

## Next Steps

- Full setup: See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
- API reference: See [API.md](API.md)
- Capabilities: See [CAPABILITIES.md](CAPABILITIES.md)
- Full docs: See [README.md](README.md)

---

Happy coding with Piddy! 🎉
