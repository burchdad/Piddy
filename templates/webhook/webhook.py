"""
Webhook Receiver Template
=========================
Receives incoming webhooks with HMAC signature verification.

Usage:
    cp -r templates/webhook/ src/webhooks/my_hook/
    # Set WEBHOOK_SECRET and implement handle_event()
"""
from fastapi import APIRouter, Request, HTTPException, Header
import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Set this from environment or key_manager
WEBHOOK_SECRET = ""


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


async def handle_event(event_type: str, payload: dict) -> dict:
    """Override with your webhook handling logic."""
    logger.info(f"Received webhook: {event_type}")
    return {"status": "processed", "event": event_type}


@router.post("/receive")
async def receive_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
):
    body = await request.body()

    if WEBHOOK_SECRET and x_signature:
        if not verify_signature(body, x_signature, WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = request.headers.get("X-Event-Type", "unknown")
    result = await handle_event(event_type, payload)
    return result
