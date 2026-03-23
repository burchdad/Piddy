# API Design Standards

## Scope: REST conventions, versioning, error responses, pagination
**Authority:** Microsoft REST API Guidelines, JSON:API, Google API Design Guide  
**Applies To:** HTTP/REST APIs  

## URL Structure

```
GET    /api/v1/users              # list
GET    /api/v1/users/123          # get one
POST   /api/v1/users              # create
PUT    /api/v1/users/123          # full update
PATCH  /api/v1/users/123          # partial update
DELETE /api/v1/users/123          # delete

# Sub-resources
GET    /api/v1/users/123/orders   # user's orders

# Query params for filtering / pagination
GET    /api/v1/users?role=admin&sort=-created_at&page=2&limit=20
```

**Rules:**
- Nouns, not verbs: `/users` not `/getUsers`
- Plural: `/users` not `/user`
- Kebab-case: `/user-profiles` not `/userProfiles`
- No trailing slashes

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Successful GET/PUT/PATCH |
| `201` | Created | Successful POST (return resource + Location header) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Validation failure |
| `401` | Unauthorized | Missing/invalid authentication |
| `403` | Forbidden | Authenticated but insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate / state conflict |
| `422` | Unprocessable | Semantically invalid request |
| `429` | Too Many Requests | Rate limited |
| `500` | Server Error | Unhandled exception |

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address" },
      { "field": "age", "message": "Must be at least 0" }
    ]
  }
}
```

**Rules:**
- Consistent error shape across all endpoints
- Machine-readable `code` + human-readable `message`
- Never leak stack traces or internal details to clients

## Pagination

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "totalPages": 8
  }
}
```

**Cursor-based** (preferred for large/real-time datasets):
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```

## Versioning

| Strategy | Example | Pros/Cons |
|----------|---------|-----------|
| URL path | `/api/v1/users` | Simple, explicit, easy to route |
| Header | `Accept: application/vnd.api+json;v=1` | Clean URLs, harder to test |
| Query param | `/api/users?version=1` | Easy to use, clutters params |

**Recommended:** URL path versioning (`/api/v1/`) — most widely adopted.
