"""Development and deployment setup."""

## Local Development

### Requirements
- Python 3.11+
- Docker (for containerized development)
- Docker Compose (for multi-service setup)

### Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your credentials

# Run
python -m src.main
```

### Development Scripts

```bash
# Format code
make format

# Run tests
make test

# Run linter
make lint

# Type checking
make typecheck

# Run all checks
make check
```

## Docker Deployment

### Build Image

```bash
docker build -t piddy:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e SLACK_BOT_TOKEN="your-token" \
  -e ANTHROPIC_API_KEY="your-key" \
  piddy:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## Production Deployment

### Pre-deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys secured (use secrets management)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup strategy in place

### Environment

```env
DEBUG=False
SERVER_HOST=0.0.0.0
AGENT_TEMPERATURE=0.5
LOG_LEVEL=WARNING
```

### Scaling Considerations

- Use load balancer for multiple instances
- Implement message queue for task processing
- Use database for persistence
- Add caching layer for frequently accessed data
- Monitor resource usage

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: black --check src/
      - run: flake8 src/
```

## Monitoring

### Logging

- Configure based on LOG_LEVEL in .env
- Use structured logging for production
- Send logs to centralized log service

### Metrics

- Track command execution time
- Monitor success/failure rates
- Track tool usage patterns
- Monitor system resources

### Alerting

- Alert on high error rates
- Alert on slow response times
- Alert on resource exhaustion
- Alert on integration failures

## Backup and Recovery

- Implement database backups
- Store configuration securely
- Maintain activity logs
- Test recovery procedures regularly
