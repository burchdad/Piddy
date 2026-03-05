# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API doesn't require authentication for MVP. This should be added in production.

## Response Format

All API responses follow this format:

```json
{
  "success": true/false,
  "data": {},
  "error": null,
  "timestamp": "2026-03-05T10:00:00Z"
}
```

## Command API

### Submit Command

**Endpoint:** `POST /api/v1/agent/command`

**Description:** Submit a backend development task to Piddy

**Request Body:**
```json
{
  "command_type": "code_generation",
  "description": "Generate a Python function that validates email addresses",
  "context": {
    "framework": "Python",
    "validation_requirements": "RFC 5322 compliant"
  },
  "source": "api",
  "priority": 8,
  "metadata": {
    "language": "python",
    "include_tests": true
  }
}
```

**Field Descriptions:**
- `command_type` (required): Type of command to execute
  - `code_generation`: Generate code
  - `api_design`: Design APIs
  - `database_schema`: Create database schemas
  - `code_review`: Review existing code
  - `debugging`: Debug and fix code
  - `infrastructure`: Infrastructure as code
  - `documentation`: Generate documentation
  - `migration`: Handle migrations
  - `custom`: Custom tasks

- `description` (required): Clear description of what needs to be done

- `context` (optional): Additional context/requirements
  - Key-value pairs with relevant information
  - Examples: framework, language, requirements, constraints

- `source` (optional): Where the command came from (default: "api")
  - `api`: From API call
  - `slack`: From Slack
  - `agent`: From another AI agent

- `priority` (optional): Priority level 1-10 (default: 5)
  - 1: Low priority
  - 10: Urgent

- `metadata` (optional): Additional metadata
  - Include language, testing requirements, etc.

**Response:**
```json
{
  "success": true,
  "command_type": "code_generation",
  "result": "def validate_email(email: str) -> bool:\n    \"\"\"Validate email address...\"\"\"\n    ...",
  "error": null,
  "execution_time": 2.34,
  "metadata": {
    "source": "api"
  }
}
```

**Status Codes:**
- `200 OK`: Command processed successfully
- `400 Bad Request`: Invalid command format
- `500 Internal Server Error`: Processing error

### Batch Commands

**Endpoint:** `POST /api/v1/agent/command/batch`

**Description:** Submit multiple commands for sequential processing

**Request Body:**
```json
[
  {
    "command_type": "code_generation",
    "description": "Generate database models",
    "context": {"framework": "SQLAlchemy"}
  },
  {
    "command_type": "api_design",
    "description": "Design REST API endpoints",
    "context": {"api_style": "RESTful"}
  }
]
```

**Response:**
```json
[
  {
    "success": true,
    "command_type": "code_generation",
    "result": "...",
    "error": null,
    "execution_time": 1.23
  },
  {
    "success": true,
    "command_type": "api_design",
    "result": "...",
    "error": null,
    "execution_time": 2.45
  }
]
```

## Health & Status

### Health Check

**Endpoint:** `GET /api/v1/agent/health`

**Response:**
```json
{
  "status": "healthy",
  "model": "claude-3-opus-20240229",
  "tools_available": 12
}
```

### Capabilities

**Endpoint:** `GET /api/v1/agent/capabilities`

**Response:**
```json
{
  "agent": "Piddy",
  "version": "0.1.0",
  "capabilities": [
    "code_generation",
    "api_design",
    "database_schema",
    "code_review",
    "debugging",
    "infrastructure",
    "documentation",
    "migration",
    "custom"
  ],
  "tools_available": 12
}
```

## Examples

### Generate FastAPI Application

```bash
curl -X POST "http://localhost:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "code_generation",
    "description": "Generate a complete FastAPI application with user authentication, database integration, and API documentation",
    "context": {
      "framework": "FastAPI",
      "database": "PostgreSQL",
      "authentication": "JWT",
      "features": ["user registration", "login", "profile management"]
    },
    "metadata": {
      "include_tests": true,
      "include_dockerfile": true,
      "include_requirements": true
    }
  }'
```

### Design Microservices Architecture

```bash
curl -X POST "http://localhost:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "infrastructure",
    "description": "Design a microservices architecture for an e-commerce platform",
    "context": {
      "services": ["user-service", "product-service", "order-service", "payment-service"],
      "scale": "high",
      "deployment": "Kubernetes"
    },
    "metadata": {
      "include_docker_compose": true,
      "include_k8s_manifests": true
    }
  }'
```

### Code Review

```bash
curl -X POST "http://localhost:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "code_review",
    "description": "Review this Python function for performance and security issues",
    "context": {
      "code": "def get_user(user_id): return db.query(User).filter(User.id == user_id).first()",
      "focus": ["performance", "security", "best_practices"]
    }
  }'
```

## Error Handling

If a command fails, the response will include error details:

```json
{
  "success": false,
  "command_type": "code_generation",
  "result": null,
  "error": "Invalid context provided: missing required field 'framework'",
  "execution_time": 0.1
}
```

## Rate Limiting

Rate limits (to be implemented):
- 100 requests per minute per IP
- 10 concurrent requests per source

## Versioning

Current API version: `v1`

Version changes will be made at `/api/v2/`, etc.

## Changelog

### v1.0.0 (Current)
- Initial command API
- Batch command processing
- Health and capability endpoints
