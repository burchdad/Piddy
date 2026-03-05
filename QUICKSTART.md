# Piddy Quick Start Guide

## 30-Second Setup

### 1. Clone & Install
```bash
cd Piddy
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY (required for Claude)
# - SLACK_BOT_TOKEN, etc. (optional for Slack)
```

### 3. Run
```bash
# Local development
python -m src.main

# Or with auto-reload
make dev

# Or with Docker
docker-compose up
```

Visit: `http://localhost:8000/docs` for interactive API docs

## First API Call

### Generate REST Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "code_generation",
    "description": "Generate a FastAPI endpoint for user registration with email validation and JWT token response",
    "context": {
      "framework": "FastAPI",
      "auth_type": "JWT",
      "validation": true
    },
    "priority": 8
  }'
```

### Check Agent Health
```bash
curl http://localhost:8000/api/v1/agent/health
```

### List Capabilities
```bash
curl http://localhost:8000/api/v1/agent/capabilities
```

## Common Use Cases

### Generate Database Model
```json
{
  "command_type": "code_generation",
  "description": "Generate a SQLAlchemy model for a Product entity with fields: id, name, description, price, stock, created_at, updated_at",
  "context": {
    "framework": "SQLAlchemy",
    "language": "python"
  }
}
```

### Analyze Code Quality
```json
{
  "command_type": "code_review",
  "description": "Review this code for quality issues and security vulnerabilities",
  "context": {
    "code": "def get_user(user_id):\n    return db.query(User).filter(User.id == user_id).first()",
    "focus": ["security", "performance", "best_practices"]
  }
}
```

### Design API
```json
{
  "command_type": "api_design",
  "description": "Design a RESTful API for a blog platform with Users, Posts, and Comments",
  "context": {
    "resources": ["User", "Post", "Comment"],
    "style": "REST",
    "auth": "JWT"
  }
}
```

### Get Design Pattern
```json
{
  "command_type": "code_generation",
  "description": "Show me the Repository pattern implementation for data access",
  "context": {
    "pattern": "repository",
    "language": "python",
    "database": "sqlalchemy"
  }
}
```

### Security Analysis
```json
{
  "command_type": "code_review",
  "description": "Perform a security analysis of this authentication code",
  "context": {
    "code": "password = request.form['password']\nuser = db.query(User).filter(User.password == password).first()"
  }
}
```

## Docker Usage

### Build Image
```bash
docker build -t piddy:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  piddy:latest
```

### Docker Compose
```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

## Development Workflow

### Run Tests
```bash
pytest tests/
pytest tests/ -v  # verbose
pytest tests/ --cov  # with coverage
```

### Code Quality
```bash
# Format
make format

# Lint
make lint

# Type check
make typecheck

# All checks
make check
```

### Make Commands
```bash
make help        # Show all commands
make install     # Install dependencies
make test        # Run tests
make dev         # Run with reload
make docker-build # Build Docker image
make clean       # Clean cache
```

## Slack Integration

### Quick Setup (5 minutes)
1. Create Slack app at https://api.slack.com/apps
2. Enable Socket Mode & generate xapp token
3. Configure OAuth scopes and get xoxb token
4. Copy tokens to `.env`
5. Run: `bash start-slack.sh` (Linux/Mac) or `start-slack.bat` (Windows)

### Use in Slack
```
@Piddy Generate a FastAPI endpoint for user authentication
@Piddy Review this code for security issues
@Piddy Design a database schema for an e-commerce platform
```

### Documentation
- **[SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md)** - Common commands and examples
- **[SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)** - Complete setup guide with screenshots
- **[SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)** - Troubleshooting & FAQ
- **[start-slack.sh](start-slack.sh)** / **[start-slack.bat](start-slack.bat)** - Automated startup scripts

## Troubleshooting

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Issues
```bash
# Check .env file
cat .env

# Verify key is valid
echo $ANTHROPIC_API_KEY
```

### Port Already in Use
```bash
# Use different port
SERVER_PORT=8001 python -m src.main

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Slack Token Invalid
```bash
# Verify in .env
SLACK_BOT_TOKEN=xoxb-xxxxx...
SLACK_SIGNING_SECRET=xxxxx...
```

## Performance Tips

### Local Development
- Use `make dev` for auto-reload
- Set `DEBUG=True` in .env
- Run tests with `-x` to stop on first failure

### Production
- Set `DEBUG=False`
- Use production database (not SQLite)
- Enable rate limiting
- Monitor with proper logging
- Use secrets management

## Next Steps

1. **Explore Tools**: Check out `CAPABILITIES.md` for full feature list
2. **View Examples**: See `API.md` for detailed request/response examples
3. **Read Docs**: Full documentation in `README.md`
4. **Slack Setup**: Configure Slack integration in `SLACK_SETUP.md`
5. **Deployment**: Deploy using `DEPLOYMENT.md`

## API Documentation

- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Need Help?

- Check `README.md` for comprehensive documentation
- See `API.md` for endpoint reference
- Review `CAPABILITIES.md` for feature documentation
- Check `SLACK_SETUP.md` for Slack integration
- See `DEPLOYMENT.md` for production setup

---

Happy coding with Piddy! 🚀
