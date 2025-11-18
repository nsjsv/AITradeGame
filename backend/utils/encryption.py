"""Encryption utilities for sensitive data

Provides encryption/decryption for API keys and other sensitive information.
Uses Fernet (symmetric encryption) from cryptography library.
"""

import os
import base64
import binascii
import logging
from typing import Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, key_file: str = '.encryption_key'):
        """Initialize encryption manager
        
        Args:
            key_file: Path to file storing encryption key
        """
        self.key_file = key_file
        self._fernet = None
        self._initialize_key()
    
    def _initialize_key(self) -> None:
        """Initialize or load encryption key"""
        if os.path.exists(self.key_file):
            # Load existing key
            with open(self.key_file, 'rb') as f:
                key = f.read()
            logger.info("Loaded existing encryption key")
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix only)
            try:
                os.chmod(self.key_file, 0o600)
            except Exception as e:
                logger.warning(f"Could not set file permissions: {e}")
            logger.info("Generated new encryption key")
        
        self._fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return plaintext
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}", exc_info=True)
            raise
    
    def _decrypt_legacy_token(self, token: str) -> Optional[str]:
        """Handle legacy tokens stored without base64 wrapping."""
        if not token:
            return ""
        try:
            decrypted_bytes = self._fernet.decrypt(token.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:  # pragma: no cover - defensive path
            logger.error(f"Legacy decryption failed: {e}", exc_info=True)
            return None
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt encrypted string
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ciphertext
        
        # Preferred format: base64-wrapped Fernet token
        try:
            encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'), validate=True)
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except (binascii.Error, ValueError):
            # Not base64 - maybe legacy or plain text
            pass
        except Exception as e:
            logger.error(f"Decryption failed: {e}", exc_info=True)
            return ""
        
        # Legacy format: raw Fernet token (typically starts with 'gAAAA')
        legacy_plain = self._decrypt_legacy_token(ciphertext)
        if legacy_plain is not None:
            logger.debug("Decrypted legacy API key format")
            return legacy_plain
        
        # Plaintext fallback (never encrypted)
        logger.warning("Detected plaintext sensitive value; returning as-is")
        return ciphertext


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance
    
    Returns:
        EncryptionManager instance
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key
    
    Args:
        api_key: Plaintext API key
        
    Returns:
        Encrypted API key
    """
    return get_encryption_manager().encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key
    
    Args:
        encrypted_key: Encrypted API key
        
    Returns:
        Plaintext API key
    """
    return get_encryption_manager().decrypt(encrypted_key)
