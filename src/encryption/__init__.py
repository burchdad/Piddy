"""Encryption module for Phase 4 - At-rest data encryption."""
import logging
from .manager import (
    EncryptionManager,
    EncryptedData,
    get_encryption_manager,
    auto_encrypt_sensitive_data,
    auto_decrypt_sensitive_data,
    SENSITIVE_FIELDS,
)

logger = logging.getLogger(__name__)

__all__ = [
    "EncryptionManager",
    "EncryptedData",
    "get_encryption_manager",
    "auto_encrypt_sensitive_data",
    "auto_decrypt_sensitive_data",
    "SENSITIVE_FIELDS",
]
