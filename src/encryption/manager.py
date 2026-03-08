"""
At-rest encryption for Phase 4.
Provides encryption/decryption of sensitive data at rest.
"""
import os
import json
import logging
from typing import Any, Optional, Dict
from cryptography.fernet import Fernet
import base64
import binascii
import hashlib

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption/decryption of sensitive data at rest.
    Uses AES-128 via Fernet for authenticated encryption.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption manager.

        Args:
            encryption_key: Master encryption key (if None, uses env variable or generates)
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")

        if encryption_key is None:
            # Generate new key
            self.key = Fernet.generate_key()
            logger.warning("⚠️ Generated new encryption key. Set ENCRYPTION_KEY env var for persistence.")
        else:
            # Load provided key
            if isinstance(encryption_key, str):
                try:
                    self.key = encryption_key.encode() if not isinstance(encryption_key, bytes) else encryption_key
                    # Validate it's a proper Fernet key
                    Fernet(self.key)
                except (ValueError, TypeError, binascii.Error):
                    # Key format invalid, derive from password
                    self.key = self._derive_key_from_password(encryption_key)
            else:
                self.key = encryption_key

        self.cipher = Fernet(self.key)
        logger.info("✅ Encryption manager initialized")

    def _derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Derive encryption key from password using SHA256."""
        if salt is None:
            salt = b'\x00' * 16  # Use empty salt for deterministic derivation

        # Use SHA256 for key derivation (simple and effective for Fernet)
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        
        # Fernet requires exactly 32 bytes, base64 encoded
        # Pad to ensure valid Fernet key (must be 44 bytes when base64 encoded)
        derived_key = base64.urlsafe_b64encode(key_material[:32])
        
        # Ensure it's 44 bytes (valid Fernet key length)
        while len(derived_key) < 44:
            derived_key += b'='
        
        return derived_key[:44]  # Return exactly 44 bytes

    def encrypt_data(self, data: Any) -> str:
        """
        Encrypt data and return base64-encoded ciphertext.

        Args:
            data: Data to encrypt (will be JSON serialized if dict/list)

        Returns:
            Base64-encoded encrypted data
        """
        try:
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized = json.dumps(data).encode()
            elif isinstance(data, str):
                serialized = data.encode()
            elif isinstance(data, bytes):
                serialized = data
            else:
                serialized = str(data).encode()

            # Encrypt
            encrypted = self.cipher.encrypt(serialized)

            # Return base64-encoded for storage/transport
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_data(self, encrypted_data: str, return_type: str = "auto") -> Any:
        """
        Decrypt data from base64-encoded ciphertext.

        Args:
            encrypted_data: Base64-encoded encrypted data
            return_type: 'auto', 'dict', 'str', 'bytes'

        Returns:
            Decrypted data
        """
        try:
            # Decode from base64
            ciphertext = base64.b64decode(encrypted_data.encode())

            # Decrypt
            decrypted = self.cipher.decrypt(ciphertext)

            # Parse based on return_type
            if return_type == "auto":
                # Try JSON first
                try:
                    return json.loads(decrypted.decode())
                except json.JSONDecodeError:
                    return decrypted.decode()
            elif return_type == "dict":
                return json.loads(decrypted.decode())
            elif return_type == "str":
                return decrypted.decode()
            elif return_type == "bytes":
                return decrypted
            else:
                return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        Encrypt a file and save encrypted version.

        Args:
            input_path: Path to file to encrypt
            output_path: Path to save encrypted file

        Returns:
            True if successful
        """
        try:
            with open(input_path, "rb") as f:
                data = f.read()

            encrypted = self.cipher.encrypt(data)

            with open(output_path, "wb") as f:
                f.write(encrypted)

            logger.info(f"File encrypted: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return False

    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        Decrypt an encrypted file and save decrypted version.

        Args:
            input_path: Path to encrypted file
            output_path: Path to save decrypted file

        Returns:
            True if successful
        """
        try:
            with open(input_path, "rb") as f:
                encrypted = f.read()

            decrypted = self.cipher.decrypt(encrypted)

            with open(output_path, "wb") as f:
                f.write(decrypted)

            logger.info(f"File decrypted: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return False

    def encrypt_field(self, obj: Dict, field_name: str) -> Dict:
        """
        Encrypt a specific field in a dictionary.

        Args:
            obj: Dictionary containing field
            field_name: Name of field to encrypt

        Returns:
            Modified dictionary with encrypted field
        """
        if field_name in obj:
            obj[f"{field_name}_encrypted"] = self.encrypt_data(obj[field_name])
            # Remove original
            del obj[field_name]
        return obj

    def decrypt_field(self, obj: Dict, field_name: str, original_name: Optional[str] = None) -> Dict:
        """
        Decrypt a specific field in a dictionary.

        Args:
            obj: Dictionary containing encrypted field
            field_name: Name of encrypted field
            original_name: Original field name (if different from field_name_encrypted)

        Returns:
            Modified dictionary with decrypted field
        """
        encrypted_field = f"{field_name}_encrypted" if original_name is None else field_name
        if encrypted_field in obj:
            obj[original_name or field_name] = self.decrypt_data(obj[encrypted_field])
            del obj[encrypted_field]
        return obj

    def rotate_key(self, old_key: bytes, new_key: bytes, data: str) -> str:
        """
        Rotate encryption key - decrypt with old key, encrypt with new.

        Args:
            old_key: Previous encryption key
            new_key: New encryption key
            data: Base64-encoded encrypted data

        Returns:
            Re-encrypted data with new key
        """
        try:
            # Decrypt with old key
            old_cipher = Fernet(old_key)
            ciphertext = base64.b64decode(data.encode())
            decrypted = old_cipher.decrypt(ciphertext)

            # Encrypt with new key
            new_cipher = Fernet(new_key)
            new_encrypted = new_cipher.encrypt(decrypted)

            return base64.b64encode(new_encrypted).decode()
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise

    def get_key_fingerprint(self) -> str:
        """Get a fingerprint of the current encryption key for verification."""
        import hashlib
        return hashlib.sha256(self.key).hexdigest()[:16]

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    @staticmethod
    def export_key(key: bytes = None) -> str:
        """
        Export key for storage/backup.

        Note: Store securely in environment variables or key management service.
        """
        if key is None:
            key = Fernet.generate_key()
        return base64.b64encode(key).decode()


# Sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    "token",
    "password",
    "secret",
    "key",
    "api_key",
    "private_key",
    "signing_secret",
    "credential",
    "aws_secret",
]


class EncryptedData:
    """Wrapper for data that should remain encrypted."""

    def __init__(self, manager: EncryptionManager, data: Any):
        """Initialize with encryption manager and data."""
        self.manager = manager
        self._encrypted = manager.encrypt_data(data)

    def decrypt(self) -> Any:
        """Decrypt and return data."""
        return self.manager.decrypt_data(self._encrypted)

    def __repr__(self) -> str:
        return f"EncryptedData(length={len(self._encrypted)})"


# Global encryption manager instance
_encryption_instance: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = EncryptionManager()
    return _encryption_instance


def should_encrypt_field(field_name: str) -> bool:
    """Check if a field should be encrypted based on name."""
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in SENSITIVE_FIELDS)


def auto_encrypt_sensitive_data(data: Dict) -> Dict:
    """
    Automatically encrypt sensitive fields in a dictionary.

    Args:
        data: Dictionary that may contain sensitive fields

    Returns:
        Dictionary with sensitive fields encrypted
    """
    manager = get_encryption_manager()
    result = data.copy()

    for field_name, value in result.items():
        if should_encrypt_field(field_name) and value:
            result[f"{field_name}_encrypted"] = manager.encrypt_data(value)
            result[field_name] = "[ENCRYPTED]"

    return result


def auto_decrypt_sensitive_data(data: Dict) -> Dict:
    """
    Automatically decrypt encrypted fields in a dictionary.

    Args:
        data: Dictionary with encrypted fields

    Returns:
        Dictionary with fields decrypted
    """
    manager = get_encryption_manager()
    result = data.copy()

    # Find encrypted fields (_encrypted suffix)
    for field_name in list(result.keys()):
        if field_name.endswith("_encrypted"):
            original_field = field_name[:-10]  # Remove _encrypted suffix
            if result[field_name]:
                try:
                    result[original_field] = manager.decrypt_data(result[field_name])
                    del result[field_name]
                except Exception as e:
                    logger.error(f"Failed to decrypt {field_name}: {e}")

    return result
