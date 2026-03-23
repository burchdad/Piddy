---
name: python-api
description: Generate production-ready Python APIs with FastAPI — routing, validation, middleware, auth, and async patterns
---

# Python API Development

Comprehensive patterns for building production-ready Python APIs with FastAPI.

## Router Structure

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])

class CreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list)

class ResourceResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: str

    model_config = {"from_attributes": True}

@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(req: CreateRequest, db: Session = Depends(get_db)):
    """Create a new resource."""
    resource = Resource(**req.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

@router.get("/", response_model=list[ResourceResponse])
async def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return db.query(Resource).offset(skip).limit(limit).all()

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.delete("/{resource_id}", status_code=204)
async def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
```

## Pydantic Validation Patterns

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Annotated

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[\w.-]+@[\w.-]+\.\w+$")
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=13, le=150)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode="after")
    def check_password_not_email(self):
        if self.password.lower() == self.email.lower():
            raise ValueError("Password cannot be the same as email")
        return self
```

## Dependency Injection

```python
from fastapi import Depends, Header, HTTPException

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> User:
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)
    user = db.query(User).get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/me")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

## Middleware & Error Handling

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time, logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.3f}s)")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

## Async Patterns

```python
import asyncio
import httpx

# Parallel external API calls
async def fetch_all_data(ids: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [client.get(f"https://api.example.com/items/{id}") for id in ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [r.json() for r in responses if not isinstance(r, Exception)]

# Background tasks
from fastapi import BackgroundTasks

@router.post("/notify")
async def send_notification(bg: BackgroundTasks):
    bg.add_task(send_email, to="user@example.com", subject="Hello")
    return {"status": "queued"}
```

## Best Practices

1. **Validate at the boundary** — Pydantic models on all request/response
2. **Use async/await** for I/O-bound work (DB, HTTP, file)
3. **Dependency injection** for DB sessions, auth, config
4. **Proper status codes**: 201 create, 204 delete, 404 not found, 422 validation error
5. **Type hints everywhere** — enables auto-generated OpenAPI docs
6. **Keep routes thin** — business logic in services, not route handlers
7. **Structured logging** — JSON logs with request context
8. **Health endpoint** — `GET /health` returning `{"status": "ok"}`
