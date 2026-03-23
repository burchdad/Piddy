"""
Piddy Configuration API — first-run onboarding + key management endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.config.key_manager import (
    get_config_status,
    save_keys,
    get_key,
    delete_keys,
    ALL_KEYS,
)

router = APIRouter(prefix="/api/config", tags=["configuration"])


# ── Models ──────────────────────────────────────────────────────────────────

class KeyPayload(BaseModel):
    ANTHROPIC_API_KEY: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = ""
    SLACK_BOT_TOKEN: Optional[str] = ""
    SLACK_SIGNING_SECRET: Optional[str] = ""
    SLACK_APP_TOKEN: Optional[str] = ""
    GITHUB_TOKEN: Optional[str] = ""


class TestKeyRequest(BaseModel):
    provider: str  # "anthropic" | "openai"
    key: str


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/status")
async def config_status():
    """Check whether Piddy is configured (keys present)."""
    return get_config_status()


@router.post("/save")
async def save_config(payload: KeyPayload):
    """Save / update API keys (encrypted at rest)."""
    save_keys(payload.model_dump())
    # Clear settings cache so agent picks up new keys
    try:
        from config.settings import get_settings
        get_settings.cache_clear()
    except Exception:
        pass
    # Reset the agent singleton so it re-initializes with new keys
    try:
        import src.dashboard_api as _api
        _api._agent_instance = None
    except Exception:
        pass
    return {"status": "saved", **get_config_status()}


@router.post("/test")
async def test_key(req: TestKeyRequest):
    """Validate a single API key against its provider."""
    provider = req.provider.lower()
    key = req.key.strip()

    if not key:
        raise HTTPException(400, "Key is empty")

    if provider == "anthropic":
        return await _test_anthropic(key)
    elif provider == "openai":
        return await _test_openai(key)
    else:
        raise HTTPException(400, f"Unknown provider: {provider}")


@router.delete("/reset")
async def reset_config():
    """Factory-reset: wipe all stored keys."""
    delete_keys()
    return {"status": "reset", **get_config_status()}


# ── Provider test helpers ───────────────────────────────────────────────────

async def _test_anthropic(key: str) -> dict:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                },
            )
        if resp.status_code in (200, 201):
            return {"valid": True, "provider": "anthropic"}
        elif resp.status_code == 401:
            return {"valid": False, "provider": "anthropic", "error": "Invalid API key"}
        else:
            return {"valid": False, "provider": "anthropic", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"valid": False, "provider": "anthropic", "error": str(e)}


async def _test_openai(key: str) -> dict:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
            )
        if resp.status_code == 200:
            return {"valid": True, "provider": "openai"}
        elif resp.status_code == 401:
            return {"valid": False, "provider": "openai", "error": "Invalid API key"}
        else:
            return {"valid": False, "provider": "openai", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"valid": False, "provider": "openai", "error": str(e)}
