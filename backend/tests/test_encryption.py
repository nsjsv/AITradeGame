"""Tests for encryption utilities"""

import pytest
from backend.utils.encryption import encrypt_api_key, decrypt_api_key, EncryptionManager


class TestEncryption:
    """Test encryption utilities"""
    
    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption"""
        original = "test-api-key-12345"
        encrypted = encrypt_api_key(original)
        decrypted = decrypt_api_key(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        encrypted = encrypt_api_key("")
        assert encrypted == ""
    
    def test_decrypt_empty_string(self):
        """Test decrypting empty string"""
        decrypted = decrypt_api_key("")
        assert decrypted == ""
    
    def test_different_keys_produce_different_ciphertext(self):
        """Test that same plaintext produces different ciphertext each time"""
        original = "test-api-key"
        encrypted1 = encrypt_api_key(original)
        encrypted2 = encrypt_api_key(original)
        
        # Fernet includes timestamp, so ciphertext will be different
        assert encrypted1 != encrypted2
        
        # But both decrypt to same value
        assert decrypt_api_key(encrypted1) == original
        assert decrypt_api_key(encrypted2) == original
    
    def test_encryption_manager_singleton(self):
        """Test that encryption manager is singleton"""
        from backend.utils.encryption import get_encryption_manager
        
        manager1 = get_encryption_manager()
        manager2 = get_encryption_manager()
        
        assert manager1 is manager2
    
    def test_decrypt_invalid_ciphertext(self):
        """Test decrypting invalid ciphertext"""
        invalid = "not-a-valid-encrypted-string"
        result = decrypt_api_key(invalid)
        
        # Should return empty string on failure
        assert result == ""
