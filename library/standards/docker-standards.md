# Docker & Container Standards

## Scope: Dockerfile best practices, compose patterns, security
**Authority:** Docker Best Practices, CIS Docker Benchmark, Hadolint  
**Tools:** Hadolint, Trivy, Docker Scout, dive  

## Dockerfile Best Practices

```dockerfile
# 1. Use specific base image tags (never :latest in production)
FROM node:20.11-alpine AS builder

# 2. Use multi-stage builds to minimize image size
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# 3. Production stage — minimal image
FROM node:20.11-alpine AS runtime
WORKDIR /app

# 4. Run as non-root user
RUN addgroup -S app && adduser -S app -G app

# 5. Copy only what's needed
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# 6. Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:3000/health || exit 1

USER app
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Layer Optimization

| Rule | Why |
|------|-----|
| Order: least → most changing | Maximize cache hits |
| Merge RUN commands | Fewer layers, smaller image |
| `COPY package*.json` before `COPY .` | Cache dependency install layer |
| Use `.dockerignore` | Exclude `node_modules`, `.git`, `.env` |
| Clean up in same RUN | `apt install -y X && rm -rf /var/lib/apt/lists/*` |

## Security Rules

| Rule | Implementation |
|------|---------------|
| Non-root user | `USER app` (never run as root) |
| Read-only filesystem | `--read-only` flag, mount tmp volumes |
| No secrets in image | Use build secrets, env vars at runtime |
| Scan images | `trivy image myapp:latest` in CI |
| Pin base image digest | `FROM node:20@sha256:abc...` for reproducibility |
| Minimal base | Alpine or distroless over full OS images |

## Docker Compose Patterns

```yaml
services:
  api:
    build:
      context: .
      target: runtime
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '1', memory: 512M }

  db:
    image: postgres:16-alpine
    volumes: [db_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
volumes:
  db_data:
```
