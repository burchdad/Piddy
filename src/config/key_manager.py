"""
Piddy Key Manager — Secure local key storage with Fernet encryption.

Keys are encrypted at rest in config/keys.enc using a machine-derived
encryption key stored in config/.keyfile. On first run both files are
created automatically.
"""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet

# Paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = _PROJECT_ROOT / "config"
KEYS_FILE = CONFIG_DIR / "keys.enc"
KEYFILE = CONFIG_DIR / ".keyfile"

# Keys that Piddy can use (not all required)
ALL_KEYS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",
    "SLACK_APP_TOKEN",
    "GITHUB_TOKEN",
]

# Minimum to run — at least one LLM provider
REQUIRED_KEYS = ["ANTHROPIC_API_KEY"]


def _get_fernet() -> Fernet:
    """Return a Fernet instance, creating the key file on first call."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not KEYFILE.exists():
        KEYFILE.write_bytes(Fernet.generate_key())
    return Fernet(KEYFILE.read_bytes().strip())


def _read_store() -> dict:
    """Decrypt and return the key store, or empty dict if missing."""
    if not KEYS_FILE.exists():
        return {}
    try:
        f = _get_fernet()
        return json.loads(f.decrypt(KEYS_FILE.read_bytes()))
    except Exception:
        return {}


def _write_store(data: dict) -> None:
    """Encrypt and persist the key store."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    f = _get_fernet()
    KEYS_FILE.write_bytes(f.encrypt(json.dumps(data).encode()))


def keys_configured() -> bool:
    """True if all REQUIRED keys are present and non-empty."""
    store = _read_store()
    return all(store.get(k) for k in REQUIRED_KEYS)


def get_config_status() -> dict:
    """Return per-key status (configured / missing) without exposing values."""
    store = _read_store()
    configured_providers = [k for k in ALL_KEYS if store.get(k)]
    return {
        "configured": keys_configured(),
        "keys": {k: bool(store.get(k)) for k in ALL_KEYS},
        "configured_providers": configured_providers,
    }


def save_keys(payload: dict) -> None:
    """Merge incoming keys into the store (only non-empty values)."""
    store = _read_store()
    for k in ALL_KEYS:
        val = payload.get(k, "").strip()
        if val:
            store[k] = val
    _write_store(store)


def get_key(name: str) -> str:
    """Retrieve a single decrypted key value (or empty string)."""
    return _read_store().get(name, "")


def get_all_keys() -> dict:
    """Return all stored keys (decrypted). Use internally only."""
    return _read_store()


def delete_keys() -> None:
    """Wipe the encrypted key store (factory reset)."""
    if KEYS_FILE.exists():
        KEYS_FILE.unlink()
