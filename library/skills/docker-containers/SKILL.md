---
name: docker-containers
description: Build, run, and optimize Docker containers and compose services
---

# Docker & Containers

## Dockerfile Best Practices
```dockerfile
# Use specific version tags (not :latest)
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code last (changes most frequently)
COPY . .

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser
USER appuser

# Use exec form for CMD (proper signal handling)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Layer Optimization
- Order instructions from least to most frequently changed
- Combine related `RUN` commands with `&&`
- Use `.dockerignore` to exclude unnecessary files
- Use multi-stage builds to reduce final image size
- Clean up caches in the same layer they're created

## Docker Compose
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/app
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      retries: 5

volumes:
  pgdata:
```

## Common Commands
```bash
docker build -t myapp:1.0 .
docker run -d --name myapp -p 8000:8000 myapp:1.0
docker compose up -d
docker compose logs -f api
docker system prune -a  # clean up unused images/containers
```

## Security
- Never store secrets in Dockerfile or image layers
- Use `--no-cache-dir` for pip to reduce image size
- Scan images with `docker scout` or Trivy
- Pin base image digests for reproducibility in production
- Run as non-root user
