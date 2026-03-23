---
name: api-integration
description: Connect to external APIs — REST clients, authentication, pagination, rate limiting, error handling, and webhook patterns
---

# API Integration

Patterns for consuming external APIs reliably — authentication, pagination, error handling, and webhook receivers.

## HTTP Client Setup

### Python (httpx — async preferred)

```python
import httpx

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(30.0, connect=5.0),
        )

    async def get(self, path: str, params: dict = None) -> dict:
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, data: dict) -> dict:
        response = await self.client.post(path, json=data)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
```

### JavaScript (fetch)

```javascript
async function apiCall(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
```

## Authentication Patterns

### API Key

```python
headers = {"X-API-Key": api_key}
# or
headers = {"Authorization": f"Bearer {api_key}"}
```

### OAuth 2.0 Flow

```python
# 1. Get authorization code (user browser redirect)
auth_url = f"{provider}/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT}&response_type=code"

# 2. Exchange code for tokens
async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{provider}/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT,
        })
        return response.json()  # { access_token, refresh_token, expires_in }

# 3. Use access token
headers = {"Authorization": f"Bearer {access_token}"}

# 4. Refresh when expired
async def refresh_token(refresh: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{provider}/token", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
        return response.json()
```

## Pagination

### Offset-based

```python
async def get_all_items(client: APIClient) -> list:
    items = []
    offset = 0
    limit = 100

    while True:
        page = await client.get("/items", params={"offset": offset, "limit": limit})
        items.extend(page["results"])
        if len(page["results"]) < limit:
            break
        offset += limit

    return items
```

### Cursor-based (preferred)

```python
async def get_all_items(client: APIClient) -> list:
    items = []
    cursor = None

    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor

        page = await client.get("/items", params=params)
        items.extend(page["results"])

        cursor = page.get("next_cursor")
        if not cursor:
            break

    return items
```

## Rate Limiting

### Client-side rate limiting

```python
import asyncio
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests: int, period: float):
        self.max_requests = max_requests
        self.period = period
        self.timestamps = deque()

    async def acquire(self):
        now = monotonic()
        while self.timestamps and self.timestamps[0] < now - self.period:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            sleep_time = self.timestamps[0] + self.period - now
            await asyncio.sleep(sleep_time)
        self.timestamps.append(monotonic())

limiter = RateLimiter(max_requests=30, period=60)  # 30/min

async def rate_limited_request(client, path):
    await limiter.acquire()
    return await client.get(path)
```

### Handling 429 responses

```python
async def request_with_retry(client, method, path, **kwargs):
    for attempt in range(3):
        response = await client.request(method, path, **kwargs)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
            await asyncio.sleep(retry_after)
            continue
        response.raise_for_status()
        return response.json()
    raise Exception(f"Rate limited after 3 retries: {path}")
```

## Error Handling

```python
async def safe_api_call(client, path):
    try:
        return await client.get(path)
    except httpx.TimeoutException:
        logger.warning(f"Timeout calling {path}")
        return None
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        if e.response.status_code >= 500:
            logger.error(f"Server error: {e.response.status_code} {path}")
            return None
        raise  # Re-raise 4xx client errors (except 404)
    except httpx.ConnectError:
        logger.error(f"Connection failed: {path}")
        return None
```

## Webhook Receiver

```python
from fastapi import FastAPI, Request, HTTPException
import hmac, hashlib

app = FastAPI()

@app.post("/webhooks/provider")
async def receive_webhook(request: Request):
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Signature-256", "")
    expected = hmac.new(
        WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, f"sha256={expected}"):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = request.headers.get("X-Event-Type")

    # Process event
    await process_event(event_type, payload)
    return {"status": "ok"}
```

## Common API Integrations

| Service | Auth Type | Base URL | Key Endpoint |
|---------|-----------|----------|--------------|
| GitHub | Bearer token | api.github.com | /repos/{owner}/{repo} |
| OpenAI | Bearer token | api.openai.com/v1 | /chat/completions |
| Stripe | Bearer token | api.stripe.com/v1 | /charges |
| Slack | Bearer token | slack.com/api | /chat.postMessage |
| Notion | Bearer token | api.notion.com/v1 | /pages |
| Discord | Bot token | discord.com/api/v10 | /channels/{id}/messages |
