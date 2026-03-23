---
name: rest-api-design
description: Design clean, consistent REST APIs with proper status codes, pagination, and error handling
---

# REST API Design

## URL Structure
```
GET    /api/v1/users          — list users
POST   /api/v1/users          — create user
GET    /api/v1/users/{id}     — get one user
PUT    /api/v1/users/{id}     — replace user
PATCH  /api/v1/users/{id}     — update fields
DELETE /api/v1/users/{id}     — delete user

GET    /api/v1/users/{id}/orders  — nested resource
```
- Use nouns, not verbs (`/users` not `/getUsers`)
- Plural resource names (`/users` not `/user`)
- Kebab-case for multi-word resources (`/user-profiles`)
- Version in URL path (`/api/v1/`)

## HTTP Status Codes
| Code | When to Use |
|------|-------------|
| 200  | Successful GET, PUT, PATCH |
| 201  | Successful POST (created) |
| 204  | Successful DELETE (no body) |
| 400  | Bad request (validation failed) |
| 401  | Not authenticated |
| 403  | Authenticated but not authorized |
| 404  | Resource not found |
| 409  | Conflict (duplicate, version mismatch) |
| 422  | Unprocessable entity (semantic error) |
| 429  | Rate limited |
| 500  | Server error (something unexpected) |

## Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Email format is invalid",
    "details": [
      { "field": "email", "message": "Must be a valid email address" }
    ]
  }
}
```

## Pagination
```
GET /api/v1/users?page=2&limit=25

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 25,
    "total": 150,
    "pages": 6
  }
}
```

## Filtering & Sorting
```
GET /api/v1/users?status=active&sort=-created_at&fields=id,name,email
```
- Prefix sort field with `-` for descending
- Use `fields` param for sparse responses

## Best Practices
- Return the created/updated resource in response body
- Use `ETag` / `If-None-Match` for caching
- Support `Accept: application/json` header
- Rate limit by API key or IP
- Log request ID for traceability
- Never expose internal IDs or stack traces in responses
