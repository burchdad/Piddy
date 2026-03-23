# Cloud & DevOps Quick Reference

## Scope: Cloud platforms, containers, CI/CD, infrastructure as code
**Platforms:** AWS, GCP, Azure  
**Tools:** Docker, Kubernetes, Terraform, GitHub Actions  

## Docker

```dockerfile
# Multi-stage Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

```bash
docker build -t app:latest .
docker compose up -d
docker compose logs -f api
```

## Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels: { app: api }
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api:v1.2.3
          ports: [{ containerPort: 3000 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits: { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /health, port: 3000 }
```

```bash
kubectl apply -f deployment.yaml
kubectl get pods -l app=api
kubectl logs -f deploy/api
kubectl rollout restart deploy/api
```

## Terraform

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

resource "aws_db_instance" "main" {
  identifier     = "prod-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.medium"
}
```

```bash
terraform init
terraform plan
terraform apply
```

## GitHub Actions

```yaml
name: CI/CD
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm test
```
